"""LLM provider calls — raw httpx, no SDK.

Routing by model name:
  gpt-*       → OpenAI                        family: openai
  gemini-*    → Google (Gemini)               family: gemini
  *otherwise* → Ollama (local OpenAI-compat)  family: ollama

Note the catch-all: any model name not matching gpt/gemini is sent to Ollama.
This is intentional — Ollama can serve many open-weight families (gemma,
qwen, llama, deepseek, ...). If the model is not pulled locally, Ollama
itself returns "model not found" — we let that error propagate.
"""

import json
import os

import httpx

from gh_query.prompt import build_prompt


GRAPHQL_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {"query": {"type": "string"}},
    "required": ["query"],
    "additionalProperties": False,
}


class LLMError(Exception):
    """Raised when an LLM call fails or returns an unparseable response."""


def family_of(model: str) -> str:
    if model.startswith("gpt"):
        return "openai"
    if model.startswith("gemini"):
        return "gemini"
    return "ollama"


def call_llm(model: str, nl: str, timeout: float = 60.0) -> str:
    """Convert NL to a GraphQL query string via the given model."""
    family = family_of(model)
    system, user = build_prompt(nl, family)
    if family == "openai":
        return _call_openai(model, system, user, timeout)
    if family == "gemini":
        return _call_gemini(model, system, user, timeout)
    return _call_ollama(model, system, user, timeout)


def _unwrap(content: str, provider: str) -> str:
    """Parse `{"query": "..."}` from an LLM response and return the query string.

    Validates that `query` is a non-empty string — Ollama's weaker structured-output
    enforcement sometimes yields `{"query": null}` or omits the field.
    """
    try:
        obj = json.loads(content)
    except json.JSONDecodeError as e:
        raise LLMError(f"{provider} returned non-JSON content: {content!r}") from e
    if not isinstance(obj, dict) or "query" not in obj:
        raise LLMError(f"{provider} response missing 'query' key: {obj!r}")
    query = obj["query"]
    if not isinstance(query, str) or not query.strip():
        raise LLMError(f"{provider} returned non-string/empty query: {query!r}")
    return query


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
                    "name": "graphql_output",
                    "strict": True,
                    "schema": GRAPHQL_OUTPUT_SCHEMA,
                },
            },
            "temperature": 0,
        },
        timeout=timeout,
    )
    if response.status_code != 200:
        raise LLMError(f"OpenAI HTTP {response.status_code}: {response.text}")
    content = response.json()["choices"][0]["message"]["content"]
    return _unwrap(content, "OpenAI")


def _call_gemini(model: str, system: str, user: str, timeout: float) -> str:
    api_key = os.environ["GEMINI_API_KEY"]
    schema = {k: v for k, v in GRAPHQL_OUTPUT_SCHEMA.items() if k != "additionalProperties"}
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
        text = body["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as e:
        raise LLMError(f"Gemini returned unexpected shape: {body!r}") from e
    return _unwrap(text, "Gemini")


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
    content = response.json()["choices"][0]["message"]["content"]
    return _unwrap(content, "Ollama")
