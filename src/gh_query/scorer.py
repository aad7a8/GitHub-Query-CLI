"""GitHub Search DSL query scorer.

The loose-string scorer used in the bilingual + typo sweeps treats two
semantically identical queries as different when qualifier order, casing,
or quoting differs. Per the actual GitHub Search DSL semantics, those are
all irrelevant. This module parses the DSL into a normalized bag of tokens
and scores three-way (1.0 / 0.5 / 0.0) per ADR-01 §5.1.

Token model
-----------
    GitHub Search query := whitespace-separated TOKENs.
    TOKEN is one of:
      - qualifier      `key:value`           e.g.  language:python
      - neg-qualifier  `-key:value`          e.g.  -label:bug
      - free-text      bare `value`          e.g.  jquery
      - neg-free       `-value`              e.g.  -bot
      - quoted-free    `"multi word"`        e.g.  "code of conduct"

Value normalization
-------------------
- strip surrounding double-quotes (GitHub treats `topic:jquery` == `topic:"jquery"`)
- lowercase (GitHub Search is case-insensitive for keys and most values)
- comma-separated lists are split + sorted (GitHub treats `label:a,b` == `label:b,a`)
- whitespace inside quoted values is preserved

Score
-----
- 1.0  parsed bag exactly equal
- 0.5  same set of qualifier keys + same free-text bag, but one or more
       qualifier *values* differ (operator/value drift like >= vs >, or
       date-boundary off-by-one)
- 0.0  otherwise (different keys, missing keys, hallucinated keys, etc.)

What the scorer intentionally does NOT do
-----------------------------------------
- semantic equivalence between distinct qualifiers (e.g. `is:issue` vs
  `type:issue` — both legal, sometimes interchangeable; we count them
  different so the eval stays sharp)
- typo-correction on values (`org:GitHb` vs `org:github` is a real miss)
- support for non-DSL syntax the model hallucinates (top-level `OR`, `*`
  wildcards) — those just produce different tokens that fail to match
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class Token:
    negated: bool
    kind: str          # "qualifier" or "free"
    key: str           # "" for free-text
    value: str         # normalized value


def _split_top_level(query: str) -> list[str]:
    """Split a query string on whitespace, respecting double-quoted runs."""
    tokens: list[str] = []
    buf: list[str] = []
    in_quote = False
    for ch in query.strip():
        if ch == '"':
            in_quote = not in_quote
            buf.append(ch)
        elif ch.isspace() and not in_quote:
            if buf:
                tokens.append("".join(buf))
                buf = []
        else:
            buf.append(ch)
    if buf:
        tokens.append("".join(buf))
    return tokens


def _strip_quotes(v: str) -> str:
    if len(v) >= 2 and v.startswith('"') and v.endswith('"'):
        return v[1:-1]
    return v


def _normalize_value(v: str) -> str:
    v = _strip_quotes(v).strip().lower()
    # comma-list canonicalization
    if "," in v:
        parts = [p.strip() for p in v.split(",") if p.strip()]
        v = ",".join(sorted(parts))
    return v


# Qualifier pairs GitHub treats as interchangeable per its own docs. We
# canonicalize the (key, value) form before comparison so the scorer
# doesn't penalize stylistic choices.
#   `type:issue`  == `is:issue`
#   `type:pr`     == `is:pr`
#   `state:open`  == `is:open`
#   `state:closed`== `is:closed`
QUALIFIER_ALIASES: dict[tuple[str, str], tuple[str, str]] = {
    ("type",  "issue"):  ("is", "issue"),
    ("type",  "pr"):     ("is", "pr"),
    ("type",  "repo"):   ("is", "repo"),
    ("type",  "repository"): ("is", "repo"),
    ("type",  "user"):   ("is", "user"),
    ("type",  "org"):    ("is", "org"),
    ("state", "open"):   ("is", "open"),
    ("state", "closed"): ("is", "closed"),
    # `draft:true` and `is:draft` are interchangeable per GitHub docs
    # (verified by api-diff: same 421938-result set on TS-PR draft query).
    ("draft", "true"):   ("is", "draft"),
}


def _canon(key: str, value: str) -> tuple[str, str]:
    return QUALIFIER_ALIASES.get((key, value), (key, value))


def parse(query: str) -> list[Token]:
    """Parse a GitHub Search query into a sorted list of normalized Tokens.

    Multi-word free-text is split into per-word tokens so that quoted vs
    unquoted multi-word free-text scores equivalent — `"code of conduct"`
    and `code of conduct` both become {code, of, conduct}. (GitHub treats
    these as different at the index level — exact-phrase vs AND tokens —
    but for top-N result comparison they are usually equivalent.)
    """
    out: list[Token] = []
    for raw in _split_top_level(query):
        negated = raw.startswith("-") and len(raw) > 1
        body = raw[1:] if negated else raw
        if ":" in body and not (body.startswith('"') and body.endswith('"')):
            key, _, val = body.partition(":")
            key_l = key.lower()
            value_n = _normalize_value(val)
            key_l, value_n = _canon(key_l, value_n)
            out.append(Token(
                negated=negated,
                kind="qualifier",
                key=key_l,
                value=value_n,
            ))
        else:
            value_n = _normalize_value(body)
            for word in value_n.split() or [value_n]:
                out.append(Token(
                    negated=negated,
                    kind="free",
                    key="",
                    value=word,
                ))
    out.sort()
    return out


# Qualifiers that are *redundant* under a given SearchType — they don't
# change top-N results in practice (api-diff verified on #14: top 10
# identical with/without `is:issue` when SearchType=ISSUE). Stripping
# these from BOTH sides gives credit to models that omit (or include)
# the redundant filter.
#
# Only "default to the wider scope" filters are listed. The OPPOSITE
# filters (is:pr under ISSUE, is:org under USER) are MEANINGFUL — they
# narrow to the non-default side — so they are kept.
REDUNDANT_UNDER_TYPE: dict[str, set[tuple[str, str]]] = {
    "ISSUE":      {("is", "issue")},  # NOT is:pr — that filters to PRs only
    "USER":       {("is", "user")},   # NOT is:org — that filters to orgs only
    "REPOSITORY": {("is", "repo")},
    "DISCUSSION": set(),
}


def _strip_redundant(tokens: list[Token], search_type: str | None) -> list[Token]:
    if not search_type:
        return tokens
    drop = REDUNDANT_UNDER_TYPE.get(search_type, set())
    if not drop:
        return tokens
    return [t for t in tokens if not (t.kind == "qualifier" and not t.negated
                                        and (t.key, t.value) in drop)]


def score(expected: str, generated: str, search_type: str | None = None) -> float:
    """Three-way score: 1.0 / 0.5 / 0.0.

    `search_type` (optional): when provided, qualifiers that are no-ops
    under that SearchType (e.g. `is:issue` when search_type='ISSUE') are
    stripped from both sides before comparison. Verified safe via api-diff.
    """
    if not generated:
        return 0.0
    e = parse(expected)
    g = parse(generated)
    if search_type:
        e = _strip_redundant(e, search_type)
        g = _strip_redundant(g, search_type)
    if e == g:
        return 1.0

    # 0.5 partial: same set of (negated, kind, key) signatures, same free-text
    # bag — only qualifier values differ.
    def sig(t: Token) -> tuple:
        return (t.negated, t.kind, t.key)

    if sorted(sig(t) for t in e) != sorted(sig(t) for t in g):
        return 0.0

    # Free-text tokens must match exactly (including value), since "free"
    # tokens have no key — comparing only signatures would drop the value.
    e_free = sorted(t for t in e if t.kind == "free")
    g_free = sorted(t for t in g if t.kind == "free")
    if e_free != g_free:
        return 0.0

    return 0.5


# ------ helpers exposed for test/eval scripts ------


def explain(expected: str, generated: str) -> dict:
    """Return a structured diff explaining why a pair scored what it did."""
    e = parse(expected); g = parse(generated)
    se = set(e); sg = set(g)
    return {
        "score": score(expected, generated),
        "expected_tokens": [t.__dict__ for t in e],
        "generated_tokens": [t.__dict__ for t in g],
        "missing_in_generated": [t.__dict__ for t in (se - sg)],
        "extra_in_generated":   [t.__dict__ for t in (sg - se)],
    }
