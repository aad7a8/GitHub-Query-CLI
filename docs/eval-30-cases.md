# Part 2 Eval Dataset — 30 Cases (Ground Truth)

> **Purpose**: Per EXAM_PROMPT §2, "30 realistic, diverse natural language queries" with the perfect structured query as ground truth. Used to compare ≥3 LLMs on translation accuracy.
>
> **Coverage** (per EXAM_PROMPT §1.2 + §2):
>
> | category | n | description |
> | --- | ---: | --- |
> | A. Simple baseline | 6 | Single-qualifier or trivially combined queries — should pass at all model tiers |
> | B. Complex constraints | 6 | 3+ qualifiers, ranges, multi-word values, type tagging |
> | C. Messy phrasing | 4 | Run-on, colloquial, polite-padded, dash-interrupted |
> | D. Ambiguous inputs | 4 | Vague terms (popular / small / recent / a few); model MUST emit `assumptions` |
> | E. Conflicting constraints | 4 | Mutually exclusive constraints; model MUST acknowledge in `assumptions` |
> | F. Typos | 3 | Brand-typo-passthrough vs closed-vocab-correction |
> | G. Non-English | 3 | Chinese, Japanese, Spanish — beyond zh/en bilingual baseline |
>
> **Provenance**: Categories A/B derive directly from `github-search-bilingual.md` (official GitHub Docs examples). C/D/E synthesised over real base scenarios. F derived from `github-search-typos.md` patterns. G is new (covers the EXAM_PROMPT "languages other than English" requirement beyond Chinese).
>
> **Scoring modes** (per case, see `mode` column):
>
> - `strict` — DSL scorer (3-tier 1.0/0.5/0.0) against `expected_query`
> - `strict+assumptions` — `strict` AND `assumptions` non-empty containing one of `assumption_keywords`
> - `behavioural` — query just needs to be syntactically valid & runnable AND `assumptions` flags conflict (any of `assumption_keywords` in `term` or `interpreted_as`)

---

## A. Simple baseline (6 cases)

| #   | category | base | NL                                                      | expected_query                                | type        | first | mode   |
| --- | -------- | ---- | ------------------------------------------------------- | --------------------------------------------- | ----------- | ----: | ------ |
| 1   | A        | 1    | repos with "jquery" in the name                          | `jquery in:name`                              | REPOSITORY  | 10    | strict |
| 2   | A        | 7    | all repos under the github org                           | `org:github`                                  | REPOSITORY  | 10    | strict |
| 3   | A        | 5    | the octocat/hello-world repo                             | `repo:octocat/hello-world`                    | REPOSITORY  | 10    | strict |
| 4   | A        | 24   | repos tagged with the topic "jekyll"                     | `topic:jekyll`                                | REPOSITORY  | 10    | strict |
| 5   | A        | 68   | the user with username octocat                           | `user:octocat`                                | USER        | 10    | strict |
| 6   | A        | 41   | closed bug-labelled issues                               | `is:issue label:bug is:closed`                | ISSUE       | 10    | strict |

## B. Complex constraints (6 cases)

| #   | category | base | NL                                                                                                | expected_query                                                          | type       | first | mode   |
| --- | -------- | ---- | ------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- | ---------- | ----: | ------ |
| 7   | B        | 20   | PHP repos with at least 500 stars including forks                                                 | `stars:>=500 fork:true language:php`                                    | REPOSITORY | 10    | strict |
| 8   | B        | 91   | open good-first-issue issues in Python                                                            | `is:issue is:open label:"good first issue" language:python`             | ISSUE      | 10    | strict |
| 9   | B        | 58   | open issues in C# repos created before 2011                                                       | `language:c# created:<2011-01-01 state:open type:issue`                 | ISSUE      | 10    | strict |
| 10  | B        | 66   | personal accounts named mike registered before 2011                                               | `mike in:name created:<2011-01-01 type:user`                            | USER       | 10    | strict |
| 11  | B        | 99   | issues with comments between 500 and 1000                                                         | `comments:500..1000 type:issue`                                         | ISSUE      | 10    | strict |
| 12  | B        | 100  | issues mentioning "code of conduct" with conversation locked in non-archived repos                | `code of conduct is:locked is:issue archived:false`                     | ISSUE      | 10    | strict |

## C. Messy phrasing (4 cases)

| #   | category | NL                                                                                          | expected_query                                                  | type        | first | mode   |
| --- | -------- | ------------------------------------------------------------------------------------------- | --------------------------------------------------------------- | ----------- | ----: | ------ |
| 13  | C        | yo gimme repos by torvalds with more than 50k stars k thx                                   | `user:torvalds stars:>50000`                                    | REPOSITORY  | 10    | strict |
| 14  | C        | All those Ruby projects with the help wanted label, can you find them please?               | `label:"help wanted" language:ruby`                             | ISSUE       | 10    | strict |
| 15  | C        | find me PRs - draft ones - that are written in TypeScript                                    | `is:pr draft:true language:typescript`                          | ISSUE       | 10    | strict |
| 16  | C        | Before March 2012. From mozilla's shumway. Closed issues only.                              | `repo:mozilla/shumway created:<2012-03-01 is:closed type:issue` | ISSUE       | 10    | strict |

## D. Ambiguous inputs (4 cases — `assumptions` MUST be non-empty)

| #   | category | NL                                              | expected_query                                                       | type        | first | assumption_keywords                          | mode                |
| --- | -------- | ----------------------------------------------- | -------------------------------------------------------------------- | ----------- | ----: | -------------------------------------------- | ------------------- |
| 17  | D        | popular React repos                             | `react stars:>1000`                                                  | REPOSITORY  | 10    | popular                                      | strict+assumptions  |
| 18  | D        | small repos with the word linter                | `linter size:<1000`                                                  | REPOSITORY  | 10    | small                                        | strict+assumptions  |
| 19  | D        | recent issues about authentication              | `authentication type:issue created:>2025-10-28`                      | ISSUE       | 10    | recent                                       | strict+assumptions  |
| 20  | D        | show me a few good first issues for Python beginners | `label:"good first issue" language:python is:issue is:open`     | ISSUE       |  5    | a few, beginners                             | strict+assumptions  |

## E. Conflicting constraints (4 cases — `assumptions` MUST acknowledge conflict)

| #   | category | NL                                                              | expected_query (any defensible pick-a-side)               | type       | first | assumption_keywords                                                | mode         |
| --- | -------- | --------------------------------------------------------------- | --------------------------------------------------------- | ---------- | ----: | ------------------------------------------------------------------ | ------------ |
| 21  | E        | Issues that are both open and closed in pytorch/pytorch         | `repo:pytorch/pytorch is:issue is:open` (or `is:closed`)  | ISSUE      | 10    | both, conflict, contradict, exclusive, picked, chose, 互斥, 矛盾    | behavioural  |
| 22  | E        | Repos with at least 1000 stars but fewer than 100 stars         | `stars:>=1000` (or `stars:<100`)                          | REPOSITORY | 10    | both, conflict, contradict, exclusive, picked, chose, 互斥, 矛盾    | behavioural  |
| 23  | E        | PRs by @me but also by @torvalds                                | `is:pr author:torvalds` (or `author:@me`)                 | ISSUE      | 10    | both, conflict, exclusive, picked, chose, ignore, single, cannot, can't, can not, only one, two authors, 互斥, 矛盾 | behavioural  |
| 24  | E        | MIT licensed repos with Apache-2.0 license                      | `license:mit` (or `license:apache-2.0`)                   | REPOSITORY | 10    | conflict, single, one, exclusive, picked, chose, 互斥, 矛盾         | behavioural  |

## F. Typos (3 cases)

| #   | category | NL                                                                              | expected_query                                              | type       | first | mode   | rationale                                                                              |
| --- | -------- | ------------------------------------------------------------------------------- | ----------------------------------------------------------- | ---------- | ----: | ------ | -------------------------------------------------------------------------------------- |
| 25  | F        | Reposiotries wiht 'jquery' in teh repostiory name.                              | `jquery in:name`                                            | REPOSITORY | 10    | strict | English fast-typing in prose only — brand correct → expected = standard query           |
| 26  | F        | Repos in pyhton with stars over 1000                                            | `language:python stars:>1000`                               | REPOSITORY | 10    | strict | `language:` is closed-vocab; model SHOULD correct `pyhton` → `python` (per harden v4)   |
| 27  | F        | PRs in repo octcat/hello-wrold by @defnukt                                      | `repo:octcat/hello-wrold author:defnukt is:pr`              | ISSUE      | 10    | strict | `repo:` and `author:` are open-vocab; model MUST preserve user spelling per brand-prot. |

## G. Non-English (3 cases)

| #   | category | lang | NL                                                                | expected_query                                | type        | first | mode   |
| --- | -------- | ---- | ----------------------------------------------------------------- | --------------------------------------------- | ----------- | ----: | ------ |
| 28  | G        | zh   | 找 facebook 組織下用 Rust 寫的 repo                                | `org:facebook language:rust`                  | REPOSITORY  | 10    | strict |
| 29  | G        | ja   | Pythonで書かれたmachine learningのリポジトリを探して               | `machine learning language:python`            | REPOSITORY  | 10    | strict |
| 30  | G        | es   | Busca repos de TensorFlow con más de 10000 estrellas               | `tensorflow stars:>10000`                     | REPOSITORY  | 10    | strict |

---

## Notes on ground-truth choices

### Why some "obvious" answers were NOT chosen

- **#7 (B)**: `stars:>=500 fork:true language:php` keeps `fork:true` (include forks) rather than `fork:only` (only forks) per the official docs phrasing. `language:php` matches the docs' lowercase canonical form even though common writing capitalizes "PHP".
- **#9 (B)**: uses both `state:open` and `type:issue` rather than just `is:open is:issue` because the official docs example for #58 has both. The alias map in `scorer.py` treats them as equivalent so either form scores 1.0.
- **#16 (C)**: `created:<2012-03-01` not `created:<=2012-02-29` — GitHub's date qualifiers use start-of-day boundaries.

### Ambiguous-case defaults (D)

The defaults below match what `prompt.py` v4 produces when given vague terms. Both the query and the assumption term are required for full credit:

- "popular" → `stars:>1000`
- "small" → `size:<1000` (≈ < 1 MB)
- "recent" → `created:>{today - 6 months}` (today = 2026-04-28 → cutoff 2025-10-28)
- "a few" → `first: 5`
- "beginners" → `label:"good first issue"`

### Conflicting-case scoring (E)

These have NO single correct query. Score requirements:
1. `search_query` is non-empty and parses without GitHub error
2. `assumptions` array is non-empty
3. At least one assumption's `term` or `interpreted_as` contains a keyword from `assumption_keywords`

This is deliberately lenient on the query side and strict on the acknowledgement side — testing the model's *self-awareness* rather than its translation.

### Typo-case rationale (F)

Per the prompt v4 brand-protection rule:

- **`user:` `org:` `repo:` `assignee:` `commenter:` `mentions:` `author:` `committer:` `head:` `base:` `topic:` `label:`** are open-vocabulary → model MUST preserve user spelling (#27)
- **`language:` `license:` `state:` `is:` `type:` `archived:` `draft:` etc.** are closed-vocabulary enums → model SHOULD correct typos (#26)
- Prose-only typos in NL (with brand correctly spelled) → model corrects the prose, produces standard query (#25)

### Non-English (G)

- #28 (zh) — uses 找/組織/用…寫 patterns that the bilingual sweep showed gpt handles well
- #29 (ja) — first time we test Japanese; deliberately mixes katakana (machine learning) with kanji and English (Python)
- #30 (es) — Spanish "más de" = "more than", testing the model's ability to map Spanish quantifier idioms to `>N`

---

## Distribution & token budget

```
A simple        : 6 cases (20%)   — accuracy floor
B complex       : 6 cases (20%)   — main difficulty
C messy         : 4 cases (13%)
D ambiguous     : 4 cases (13%)   — assumptions test
E conflicting   : 4 cases (13%)   — behavioural test
F typos         : 3 cases (10%)
G non-English   : 3 cases (10%)
                =====
                  30 cases
```

Across 3 models (gpt-5.4-mini / gemini-3.1-flash-lite-preview / gemma4:e4b) = 90 runs ≈ 4-6 minutes per full eval pass.
