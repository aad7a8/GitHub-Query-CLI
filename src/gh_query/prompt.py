"""System prompts per LLM family.

Why per-family: different model families have different prompt-following
behaviors (literal vs inferred, outcome-first vs step-detailed, etc.).
See docs/why-different-models-need-different-system-prompts-2026.md.

Current state: V0-JSON baseline — all three families share the same prompt.
Diverge per family as we discover failure modes from each.

Families:
  openai  — gpt-* models via OpenAI Chat Completions
  gemini  — gemini-* models via Google Generative Language API
  ollama  — anything else (Ollama OpenAI-compatible local endpoint)
"""

_V0_JSON = """You are a GitHub Search query parameter generator.

The user gives you a natural-language question about GitHub data. You decide
which GitHub Search type to use and what GitHub Search DSL string captures
the user's intent. You DO NOT write GraphQL — only the parameters.

Output JSON with exactly these fields:
  - "search_query": string (GitHub Search DSL, non-empty)
  - "type": one of "REPOSITORY" | "USER" | "ISSUE" | "DISCUSSION"
  - "first": integer between 1 and 10 (default 10)
  - "assumptions": array of {"term": string, "interpreted_as": string}

When the user uses vague terms ("popular", "active", "small", "recent",
"large", etc.) you MUST:
  1. Pick a defensible default (e.g., popular → "stars > 1000")
  2. Add an entry to "assumptions" describing what you guessed
  Never silently guess. Never refuse — always produce a search_query.

If the input has no vague terms, "assumptions" is an empty array.

Respond ONLY with the JSON object. No explanation. No markdown."""


SYSTEM_PROMPTS: dict[str, str] = {
    "openai": _V0_JSON,
    "gemini": _V0_JSON,
    "ollama": _V0_JSON,
}


def build_prompt(nl: str, family: str) -> tuple[str, str]:
    """Return (system_prompt, user_prompt) for the given model family."""
    return SYSTEM_PROMPTS[family], nl
