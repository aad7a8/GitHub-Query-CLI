"""Ground-truth dataset for Part 2 eval.

Mirrors `docs/eval-30-cases.md`. The markdown is human documentation; this
file is the source of truth for the runner.

Schema per case:
  id                  int  1..30
  category            str  one of A/B/C/D/E/F/G
  base                int  source bilingual case # (None if synthetic)
  nl                  str  natural-language input given to LLM
  expected_query      str  ground-truth GitHub Search DSL string
  expected_type       str  REPOSITORY | USER | ISSUE | DISCUSSION
  expected_first      int  expected first value (default 10)
  mode                str  strict | strict+assumptions | behavioural
  assumption_keywords list[str]  for D/E modes — at least one must appear
                                 in any assumption term/interpreted_as
"""

from __future__ import annotations


CASES: list[dict] = [
    # --- A. Simple baseline (6) ---
    {"id": 1, "category": "A", "base": 1, "nl": 'repos with "jquery" in the name',
     "expected_query": "jquery in:name", "expected_type": "REPOSITORY",
     "expected_first": 10, "mode": "strict", "assumption_keywords": []},
    {"id": 2, "category": "A", "base": 7, "nl": "all repos under the github org",
     "expected_query": "org:github", "expected_type": "REPOSITORY",
     "expected_first": 10, "mode": "strict", "assumption_keywords": []},
    {"id": 3, "category": "A", "base": 5, "nl": "the octocat/hello-world repo",
     "expected_query": "repo:octocat/hello-world", "expected_type": "REPOSITORY",
     "expected_first": 10, "mode": "strict", "assumption_keywords": []},
    {"id": 4, "category": "A", "base": 24, "nl": 'repos tagged with the topic "jekyll"',
     "expected_query": "topic:jekyll", "expected_type": "REPOSITORY",
     "expected_first": 10, "mode": "strict", "assumption_keywords": []},
    {"id": 5, "category": "A", "base": 68, "nl": "the user with username octocat",
     "expected_query": "user:octocat", "expected_type": "USER",
     "expected_first": 10, "mode": "strict", "assumption_keywords": []},
    {"id": 6, "category": "A", "base": 41, "nl": "closed bug-labelled issues",
     "expected_query": "is:issue label:bug is:closed", "expected_type": "ISSUE",
     "expected_first": 10, "mode": "strict", "assumption_keywords": []},

    # --- B. Complex constraints (6) ---
    {"id": 7, "category": "B", "base": 20,
     "nl": "PHP repos with at least 500 stars including forks",
     "expected_query": "stars:>=500 fork:true language:php",
     "expected_type": "REPOSITORY", "expected_first": 10, "mode": "strict",
     "assumption_keywords": []},
    {"id": 8, "category": "B", "base": 91,
     "nl": "open good-first-issue issues in Python",
     "expected_query": 'is:issue is:open label:"good first issue" language:python',
     "expected_type": "ISSUE", "expected_first": 10, "mode": "strict",
     "assumption_keywords": []},
    {"id": 9, "category": "B", "base": 58,
     "nl": "open issues in C# repos created before 2011",
     "expected_query": "language:c# created:<2011-01-01 state:open type:issue",
     "expected_type": "ISSUE", "expected_first": 10, "mode": "strict",
     "assumption_keywords": []},
    {"id": 10, "category": "B", "base": 66,
     "nl": "personal accounts named mike registered before 2011",
     "expected_query": "mike in:name created:<2011-01-01 type:user",
     "expected_type": "USER", "expected_first": 10, "mode": "strict",
     "assumption_keywords": []},
    {"id": 11, "category": "B", "base": 99,
     "nl": "issues with comments between 500 and 1000",
     "expected_query": "comments:500..1000 type:issue",
     "expected_type": "ISSUE", "expected_first": 10, "mode": "strict",
     "assumption_keywords": []},
    {"id": 12, "category": "B", "base": 100,
     "nl": 'issues mentioning "code of conduct" with conversation locked in non-archived repos',
     "expected_query": "code of conduct is:locked is:issue archived:false",
     "expected_type": "ISSUE", "expected_first": 10, "mode": "strict",
     "assumption_keywords": []},

    # --- C. Messy phrasing (4) ---
    {"id": 13, "category": "C", "base": None,
     "nl": "yo gimme repos by torvalds with more than 50k stars k thx",
     "expected_query": "user:torvalds stars:>50000",
     "expected_type": "REPOSITORY", "expected_first": 10, "mode": "strict",
     "assumption_keywords": []},
    {"id": 14, "category": "C", "base": None,
     "nl": "All those Ruby projects with the help wanted label, can you find them please?",
     "expected_query": 'label:"help wanted" language:ruby',
     "expected_type": "ISSUE", "expected_first": 10, "mode": "strict",
     "assumption_keywords": []},
    {"id": 15, "category": "C", "base": None,
     "nl": "find me PRs - draft ones - that are written in TypeScript",
     "expected_query": "is:pr draft:true language:typescript",
     "expected_type": "ISSUE", "expected_first": 10, "mode": "strict",
     "assumption_keywords": []},
    {"id": 16, "category": "C", "base": None,
     "nl": "Before March 2012. From mozilla's shumway. Closed issues only.",
     "expected_query": "repo:mozilla/shumway created:<2012-03-01 is:closed type:issue",
     "expected_type": "ISSUE", "expected_first": 10, "mode": "strict",
     "assumption_keywords": []},

    # --- D. Ambiguous (4) — assumptions REQUIRED ---
    {"id": 17, "category": "D", "base": None,
     "nl": "popular React repos",
     "expected_query": "react stars:>1000",
     "expected_type": "REPOSITORY", "expected_first": 10,
     "mode": "strict+assumptions", "assumption_keywords": ["popular"]},
    {"id": 18, "category": "D", "base": None,
     "nl": "small repos with the word linter",
     "expected_query": "linter size:<1000",
     "expected_type": "REPOSITORY", "expected_first": 10,
     "mode": "strict+assumptions", "assumption_keywords": ["small"]},
    {"id": 19, "category": "D", "base": None,
     "nl": "recent issues about authentication",
     "expected_query": "authentication type:issue created:>2025-10-28",
     "expected_type": "ISSUE", "expected_first": 10,
     "mode": "strict+assumptions", "assumption_keywords": ["recent"]},
    {"id": 20, "category": "D", "base": None,
     "nl": "show me a few good first issues for Python beginners",
     "expected_query": 'label:"good first issue" language:python is:issue is:open',
     "expected_type": "ISSUE", "expected_first": 5,
     "mode": "strict+assumptions", "assumption_keywords": ["a few", "beginners"]},

    # --- E. Conflicting (4) — behavioural; query just needs to be runnable ---
    {"id": 21, "category": "E", "base": None,
     "nl": "Issues that are both open and closed in pytorch/pytorch",
     "expected_query": "repo:pytorch/pytorch is:issue is:open",
     "expected_type": "ISSUE", "expected_first": 10, "mode": "behavioural",
     "assumption_keywords": ["both", "conflict", "contradict", "exclusive",
                             "picked", "chose", "ignore", "互斥", "矛盾"]},
    {"id": 22, "category": "E", "base": None,
     "nl": "Repos with at least 1000 stars but fewer than 100 stars",
     "expected_query": "stars:>=1000",
     "expected_type": "REPOSITORY", "expected_first": 10, "mode": "behavioural",
     "assumption_keywords": ["both", "conflict", "contradict", "exclusive",
                             "picked", "chose", "ignore", "互斥", "矛盾"]},
    {"id": 23, "category": "E", "base": None,
     "nl": "PRs by @me but also by @torvalds",
     "expected_query": "is:pr author:torvalds",
     "expected_type": "ISSUE", "expected_first": 10, "mode": "behavioural",
     "assumption_keywords": ["both", "conflict", "exclusive", "picked",
                             "chose", "ignore", "single", "cannot",
                             "can't", "can not", "only one", "two authors",
                             "互斥", "矛盾"]},
    {"id": 24, "category": "E", "base": None,
     "nl": "MIT licensed repos with Apache-2.0 license",
     "expected_query": "license:mit",
     "expected_type": "REPOSITORY", "expected_first": 10, "mode": "behavioural",
     "assumption_keywords": ["conflict", "single", "one", "exclusive",
                             "picked", "chose", "ignore", "互斥", "矛盾"]},

    # --- F. Typos (3) ---
    {"id": 25, "category": "F", "base": None,
     "nl": 'Reposiotries wiht "jquery" in teh repostiory name.',
     "expected_query": "jquery in:name", "expected_type": "REPOSITORY",
     "expected_first": 10, "mode": "strict", "assumption_keywords": []},
    {"id": 26, "category": "F", "base": None,
     "nl": "Repos in pyhton with stars over 1000",
     "expected_query": "language:python stars:>1000",
     "expected_type": "REPOSITORY", "expected_first": 10, "mode": "strict",
     "assumption_keywords": []},
    {"id": 27, "category": "F", "base": None,
     "nl": "PRs in repo octcat/hello-wrold by @defnukt",
     "expected_query": "repo:octcat/hello-wrold author:defnukt is:pr",
     "expected_type": "ISSUE", "expected_first": 10, "mode": "strict",
     "assumption_keywords": []},

    # --- G. Non-English (3) ---
    {"id": 28, "category": "G", "base": None,
     "nl": "找 facebook 組織下用 Rust 寫的 repo",
     "expected_query": "org:facebook language:rust",
     "expected_type": "REPOSITORY", "expected_first": 10, "mode": "strict",
     "assumption_keywords": []},
    {"id": 29, "category": "G", "base": None,
     "nl": "Pythonで書かれたmachine learningのリポジトリを探して",
     "expected_query": "machine learning language:python",
     "expected_type": "REPOSITORY", "expected_first": 10, "mode": "strict",
     "assumption_keywords": []},
    {"id": 30, "category": "G", "base": None,
     "nl": "Busca repos de TensorFlow con más de 10000 estrellas",
     "expected_query": "tensorflow stars:>10000",
     "expected_type": "REPOSITORY", "expected_first": 10, "mode": "strict",
     "assumption_keywords": []},
]


# Defensive — fail loudly if data drifts
assert len(CASES) == 30, f"Expected 30 cases, got {len(CASES)}"
assert {c["id"] for c in CASES} == set(range(1, 31)), "IDs must be 1..30"
for c in CASES:
    assert c["category"] in {"A", "B", "C", "D", "E", "F", "G"}
    assert c["expected_type"] in {"REPOSITORY", "USER", "ISSUE", "DISCUSSION"}
    assert c["mode"] in {"strict", "strict+assumptions", "behavioural"}
    if c["mode"] != "strict":
        assert c["assumption_keywords"], f"#{c['id']} mode {c['mode']} requires assumption_keywords"
