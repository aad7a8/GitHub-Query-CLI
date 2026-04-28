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


This README file contains the entire idea, so it may look somewhat disorganized.

PART-1
Break it:
The ambiguous problem is that there is no correct answer so i judge it by current thought.
Normally should focus on user/client work flow to understand what is actually correct.


Show open issues in facebook/react labeled bug > label is user define
Show issues in react > always assume facebook/react not search react
search react repo's contributors > doesn't support contributors
Show repos by google > search both but need to clearfy first
list torvalds/linux repo > doesn't use repo:torvalds/linux
Find repos licensed under MIT or Apache 2.0 > gpt always include OR\
Open issues that are closed > search only closed
Match a specific repository name > doesn't provide any info
'來自 GitHub 的 repo'  'Repositories from GitHub' > expect org:github but get stars:>0 or search github
label:help wanted > expect: label:"help wanted"
typo auto fixed but some field shouldn't

Explain: 
1) Label problem

Conclusion:
GitHub's label is a string that says "customized for each repo".

Detail

1. The search query is working in huggingface/transformers

"Show open issues in huggingface/transformers labeled bug"
{
  "search_query": "repo:huggingface/transformers is:issue is:open label:bug",
  "type": "ISSUE",
  "first": 10,
  "assumptions": []
}
{
  "search": {
    "repositoryCount": 0,
    "issueCount": 87,
    "userCount": 0,
    "discussionCount": 0,
    "nodes": [
      {
	  
2. But it's not working at facebook/react repo

"Show open issues in facebook/react repo labeled bug"
{
  "search_query": "repo:facebook/react is:issue is:open label:bug",
  "type": "ISSUE",
  "first": 10,
  "assumptions": []
}
{
  "search": {
    "repositoryCount": 0,
    "issueCount": 0,
    "userCount": 0,
    "discussionCount": 0,
    "nodes": [] 


3. Use the correct pattern

' 285 (.venv) user@user-PC:~/Project/GitHub-Query-CLI/src/gh_query$ python3 main
.py --show-query "Show open issues in facebook/react label type have bug"
 286 query { repository(owner: "facebook", name: "react") { issues(states: OPEN, labels: ["type: bug"], first: 100) { nodes { number title url state labels(first: 10) { no
     des { name } } } } } }'
{
  "search_query": "repo:facebook/react is:issue is:open label:\"type: bug\"",
  "type": "ISSUE",
  "first": 10,
  "assumptions": [
    {
      "term": "label type have bug",
      "interpreted_as": "label:\"type: bug\""
    }
  ]
}
{
  "search": {
    "repositoryCount": 0,
    "issueCount": 377,
    "userCount": 0,
    "discussionCount": 0,
    "nodes": [
	
	
	
2) Nested problem
Something like "list all repo in react repo and count star"

3) contributors is not inside search scope
Github recommand use restAPI to find contributors's info and it's out of current scope.

4) User's intent unclear
"Match a specific repository name" - user does not give any detail
Need agent loop to ask what user really want.


PART-2

○	Model Selection: How did you choose these specific 3+ models? Why were they capable of hitting the accuracy threshold across the board?
1. Cost / Latency: The searching task should not be overpriced and must act as quick as possible.
2. Structured Output: No structured output meaning not able to generate output. Reasoning: So it can think what user intent.

○	Performance: Compare how the models performed. What patterns did they initially get wrong?
Hallucinated OR — label:bug OR label:resolved (GitHub Search has no top-level OR; canonical is label:bug,resolved)
Invented qualifiers — commit:e1109ab for commit SHA (none exists; SHA is a bare token)
Operator drift — "at least N" → >N instead of >=N
Multi-word value quote loss — label:"good first issue" → label:good first issue (silently splits into label:good + 2 free-text tokens)
Unit unaware — "30 mb" → size:>=30 instead of >=30000 (GitHub size is decimal KB, 1 MB = 1000 KB)
Gemini lack of date must provide current date.

○	Learnings: What did you learn about eval design and building ground truth for structured outputs?
Overly rigorous comparisons can systematically underestimate accuracy.
Distinguishing between "completely consistent," "meaningfully correct," and "completely incorrect" is better than simply categorizing them as right or wrong.
Some search rules are equivalent and must be included to avoid misjudgments, Sometimes the rules generated by LLM and Ground Truth return the same response when calling the API.
Complex or ambiguous intentions are the most difficult.





Other thought

1) What is beyond single shot NL to GraphQL?
1. Typo, some repo can named with different user thought, somethmes the name is what user want.
How to fix?
My thought: Use agentic loop to grab the user's repo and feedback to the user.

2) Choose single shot NL to GraphQL rather then agent loop
1. GraphQL's nested selection makes most multi-entity queries single-shot.

3) Choose Raw HTTP over vendor SDKs
1. Task is simple no SDK needed
2. SDK hide some output

4) Why design different system prompt for different model?
1. Follow the report docs/why-different-models-need-different-system-prompts-2026.md same task same model can have different performance with different system prompt.

5) Why I changed from full GraphQL to JSON parameters?
GitHub Search is a two-layer DSL: a fixed outer GraphQL skeleton (`search(query: $q, type: $t, first: $n) { nodes { ... } }`) plus a variable inner search-string(`language:rust stars:>1000 sort:stars-desc`).
When the LLM produced full GraphQL, every failure was in the inner string (search query) outer structure just burning tokens