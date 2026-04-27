"""LLM provider calls — raw httpx, no SDK.

Routing by model name:
  gpt-*       → OpenAI                        family: openai
  gemini-*    → Google (Gemini)               family: gemini
  *otherwise* → Ollama (local OpenAI-compat)  family: ollama

Note the catch-all: any model name not matching gpt/gemini is sent to Ollama.
This is intentional — Ollama can serve many open-weight families (gemma,
qwen, llama, deepseek, ...). If the model is not pulled locally, Ollama
itself returns "model not found" — we let that error propagate.

LLM output contract: SearchParams (Pydantic), not raw GraphQL string. See
docs/logs/ADR-02.md for the rationale (LLM produces only inner Search-DSL
parameters; outer GraphQL is a fixed Python template).
"""

import json
import os
from typing import Literal

import httpx
from pydantic import BaseModel, Field, ValidationError

from gh_query.prompt import build_prompt


SearchType = Literal["REPOSITORY", "USER", "ISSUE", "DISCUSSION"]


class Assumption(BaseModel):
    term: str
    interpreted_as: str


class SearchParams(BaseModel):
    """The structured contract LLMs must produce.

    Validated by Pydantic on every LLM response. Any deviation (missing
    field, wrong type, out-of-range first, unknown SearchType) raises
    ValidationError and is wrapped into LLMError by the caller.
    """

    search_query: str = Field(..., min_length=1)
    type: SearchType
    first: int = Field(default=10, ge=1, le=10)
    assumptions: list[Assumption] = Field(default_factory=list)


# JSON Schema embedded into the LLM API requests where supported
# (OpenAI strict json_schema, Gemini responseSchema). Kept in sync with the
# Pydantic model above by hand — small enough that drift is easy to spot.
SEARCH_PARAMS_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "search_query": {"type": "string", "minLength": 1},
        "type": {"type": "string", "enum": ["REPOSITORY", "USER", "ISSUE", "DISCUSSION"]},
        "first": {"type": "integer", "minimum": 1, "maximum": 10},
        "assumptions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "term": {"type": "string"},
                    "interpreted_as": {"type": "string"},
                },
                "required": ["term", "interpreted_as"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["search_query", "type", "first", "assumptions"],
    "additionalProperties": False,
}


class LLMError(Exception):
    """Raised when an LLM call fails or returns an invalid response."""


def family_of(model: str) -> str:
    if model.startswith("gpt"):
        return "openai"
    if model.startswith("gemini"):
        return "gemini"
    return "ollama"


def call_llm(model: str, nl: str, timeout: float = 60.0) -> SearchParams:
    """Convert NL to validated SearchParams via the given model."""
    family = family_of(model)
    system, user = build_prompt(nl, family)
    if family == "openai":
        raw = _call_openai(model, system, user, timeout)
    elif family == "gemini":
        raw = _call_gemini(model, system, user, timeout)
    else:
        raw = _call_ollama(model, system, user, timeout)
    return _parse(raw, family)


def _parse(content: str, provider: str) -> SearchParams:
    """Parse LLM JSON output into a validated SearchParams."""
    try:
        obj = json.loads(content)
    except json.JSONDecodeError as e:
        raise LLMError(f"{provider} returned non-JSON content: {content!r}") from e
    try:
        return SearchParams.model_validate(obj)
    except ValidationError as e:
        raise LLMError(f"{provider} JSON failed schema validation: {e}\nRaw: {obj!r}") from e


def _call_openai(model: str, system: str, user: str, timeout: float) -> str:
    api_key = os.environ["OPENAI_API_KEY"]
    response = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "search_params",
                    "strict": True,
                    "schema": SEARCH_PARAMS_SCHEMA,
                },
            },
            "temperature": 0,
        },
        timeout=timeout,
    )
    if response.status_code != 200:
        raise LLMError(f"OpenAI HTTP {response.status_code}: {response.text}")
    return response.json()["choices"][0]["message"]["content"]


def _call_gemini(model: str, system: str, user: str, timeout: float) -> str:
    api_key = os.environ["GEMINI_API_KEY"]
    # Gemini's responseSchema does not accept `additionalProperties`.
    schema = _strip_additional_properties(SEARCH_PARAMS_SCHEMA)
    response = httpx.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        params={"key": api_key},
        json={
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {
                "temperature": 0,
                "responseMimeType": "application/json",
                "responseSchema": schema,
            },
        },
        timeout=timeout,
    )
    if response.status_code != 200:
        raise LLMError(f"Gemini HTTP {response.status_code}: {response.text}")
    body = response.json()
    try:
        return body["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as e:
        raise LLMError(f"Gemini returned unexpected shape: {body!r}") from e


def _call_ollama(model: str, system: str, user: str, timeout: float) -> str:
    base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    response = httpx.post(
        f"{base_url}/chat/completions",
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0,
        },
        timeout=timeout,
    )
    if response.status_code != 200:
        raise LLMError(f"Ollama HTTP {response.status_code}: {response.text}")
    return response.json()["choices"][0]["message"]["content"]


def _strip_additional_properties(schema: dict) -> dict:
    """Recursively remove `additionalProperties` keys for Gemini compatibility."""
    if not isinstance(schema, dict):
        return schema
    out = {}
    for k, v in schema.items():
        if k == "additionalProperties":
            continue
        if isinstance(v, dict):
            out[k] = _strip_additional_properties(v)
        elif isinstance(v, list):
            out[k] = [_strip_additional_properties(item) for item in v]
        else:
            out[k] = v
    return out
