"""System prompts per LLM family.

Why per-family: different model families have different prompt-following
behaviors (literal vs inferred, outcome-first vs step-detailed, etc.).
See docs/why-different-models-need-different-system-prompts-2026.md.

Current state: V0 baseline — all three families share the same minimal prompt.
Diverge per family as we discover failure modes from each.

Families:
  openai  — gpt-* models via OpenAI Chat Completions
  gemini  — gemini-* models via Google Generative Language API
  ollama  — anything else (Ollama OpenAI-compatible local endpoint)
"""

_V0 = """You are a GitHub GraphQL v4 query generator.
Convert the user's natural language to a single valid GitHub GraphQL query.

Respond ONLY with JSON: {"query": "<graphql>"}.
No explanation. No markdown."""


SYSTEM_PROMPTS: dict[str, str] = {
    "openai": _V0,
    "gemini": _V0,
    "ollama": _V0,
}


def build_prompt(nl: str, family: str) -> tuple[str, str]:
    """Return (system_prompt, user_prompt) for the given model family."""
    return SYSTEM_PROMPTS[family], nl
