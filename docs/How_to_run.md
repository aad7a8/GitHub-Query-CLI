# How to run

## 1. Setup

```bash
cd /path/to/GitHub-Query-CLI
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

Requires Python ≥ 3.12.

## 2. Configure credentials

Copy `.env.example` to `.env` and fill in the keys you need:

```bash
cp .env.example .env
```

| variable | required for | notes |
| --- | --- | --- |
| `GITHUB_TOKEN` | always | PAT with `read:org`, `repo`, `read:user` |
| `OPENAI_API_KEY` | OpenAI models (`gpt-5.4-mini`) | |
| `GEMINI_API_KEY` | Gemini models (`gemini-3.1-flash-lite-preview`) | |
| `OLLAMA_BASE_URL` | Ollama models (`qwen3.5:9b`, etc.) | optional, defaults to `http://localhost:11434/v1` |

For Ollama: install from <https://ollama.com>, then `ollama pull qwen3.5:9b`.

## 3. CLI usage

```bash
# NL → LLM → GraphQL → GitHub API → JSON
gh-query "find repos with jquery in the name"

# Pick a model (default: gpt-5.4-mini)
gh-query --model gemini-3.1-flash-lite-preview "issues opened by me last week"
gh-query --model qwen3.5:9b "all repos under the github org"

# Inspect the generated SearchParams + GraphQL on stderr
gh-query --show-query "users named torvalds"

# Bypass the LLM and execute raw GraphQL directly
gh-query --raw 'query { viewer { login } }'
```

If the package isn't installed, run via module:

```bash
PYTHONPATH=src python3 -m gh_query.main "..."
```

## 4. Run the 30-case eval

```bash
# All default models (gpt-5.4-mini, gemini-3.1-flash-lite-preview, qwen3.5:9b)
python3 scripts/eval_30.py

# Subset of models
python3 scripts/eval_30.py --models gpt-5.4-mini

# Single case across all models (debug)
python3 scripts/eval_30.py --case 17
```

Outputs land in `docs/`:

- `eval_30_<timestamp>.json` — raw per-(model, case) records
- `eval_30_<timestamp>.md` — per-model + per-category accuracy matrix

Pass threshold is 85 % (per `docs/EXAM_PROMPT.md` §2.4).

The 30 ground-truth cases live in `scripts/eval_30_data.py` (canonical) and are mirrored in `docs/eval-30-cases.md` (human-readable).
