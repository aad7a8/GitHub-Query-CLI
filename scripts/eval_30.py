"""Part 2 multi-model eval runner.

Runs the 30 ground-truth cases (scripts/eval_30_data.py) against any
combination of LLMs and produces:

  docs/eval_30_<timestamp>.json  raw per-(model,case) records
  docs/eval_30_<timestamp>.md    per-model + per-category accuracy matrix

Usage:
  python scripts/eval_30.py                          # all 3 default models
  python scripts/eval_30.py --models gpt-5.4-mini    # subset
  python scripts/eval_30.py --case 17                # single case across models
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from dotenv import load_dotenv

from gh_query.llm import LLMError, call_llm
from gh_query.scorer import score as dsl_score
from eval_30_data import CASES

load_dotenv()


DEFAULT_MODELS = [
    "gpt-5.4-mini",
    "gemini-3.1-flash-lite-preview",
    "gemma4:e4b",
]
DOCS = ROOT / "docs"
PASS_THRESHOLD = 0.85  # EXAM_PROMPT §2.4


# ---------- scoring ----------


def assumption_acknowledges(assumptions: list[dict], keywords: list[str]) -> bool:
    """True if any assumption term/interpreted_as contains any keyword (lowercase)."""
    if not assumptions:
        return False
    kws = [k.lower() for k in keywords]
    for a in assumptions:
        text = (a.get("term", "") + " " + a.get("interpreted_as", "")).lower()
        if any(k in text for k in kws):
            return True
    return False


def grade_case(case: dict, params: dict | None, error: str | None) -> dict:
    """Compose a verdict from an LLM run record.

    Returns a dict with: dsl_score, type_match, first_match, ack, status, reason.
    `status` is "pass" / "partial" / "fail".
    """
    if error or params is None:
        return {"dsl_score": 0.0, "type_match": False, "first_match": False,
                "ack": False, "status": "fail", "reason": f"error: {error}"}

    gen_q = params["search_query"]
    # Pass expected SearchType so scorer can strip redundant `is:issue`/etc.
    ds = dsl_score(case["expected_query"], gen_q, search_type=case["expected_type"])
    type_ok = (params["type"] == case["expected_type"])
    first_ok = (params["first"] == case["expected_first"])
    ack = assumption_acknowledges(params.get("assumptions", []),
                                  case["assumption_keywords"])

    mode = case["mode"]
    if mode == "strict":
        if ds == 1.0 and type_ok and first_ok:
            status, reason = "pass", ""
        elif ds == 1.0 and not type_ok:
            status, reason = "partial", "type mismatch"
        elif ds == 1.0 and not first_ok:
            status, reason = "partial", f"first={params['first']} expected {case['expected_first']}"
        elif ds == 0.5:
            status, reason = "partial", "DSL value drift"
        else:
            status, reason = "fail", "DSL mismatch"

    elif mode == "strict+assumptions":
        if ds == 1.0 and type_ok and first_ok and ack:
            status, reason = "pass", ""
        elif ds == 1.0 and type_ok and not ack:
            status, reason = "partial", "missing assumption ack"
        elif ds >= 0.5 and type_ok and ack:
            status, reason = "partial", "DSL drift but ack OK"
        else:
            status, reason = "fail", f"dsl={ds} ack={ack} type={type_ok}"

    elif mode == "behavioural":
        non_empty = bool(gen_q.strip())
        if non_empty and ack:
            status, reason = "pass", ""
        elif non_empty:
            status, reason = "fail", "no conflict acknowledgement"
        else:
            status, reason = "fail", "empty query"

    else:
        status, reason = "fail", f"unknown mode {mode}"

    return {"dsl_score": ds, "type_match": type_ok, "first_match": first_ok,
            "ack": ack, "status": status, "reason": reason}


# ---------- runner ----------


def run_case(model: str, case: dict, timeout: float = 300.0) -> dict:
    """Single (model, case) execution."""
    record: dict = {"model": model, "case_id": case["id"]}
    t0 = time.time()
    try:
        params = call_llm(model, case["nl"], timeout=timeout)
        record["params"] = params.model_dump()
        record["error"] = None
    except LLMError as e:
        record["params"] = None
        record["error"] = str(e)
    except Exception as e:  # noqa: BLE001
        record["params"] = None
        record["error"] = f"unexpected: {e!r}"
    record["elapsed"] = time.time() - t0
    record["grade"] = grade_case(case, record["params"], record["error"])
    return record


# ---------- aggregation ----------


def per_model_stats(records: list[dict]) -> dict:
    """{ model: { pass:int, partial:int, fail:int, accuracy:float, avg_dsl:float } }"""
    out: dict = {}
    by_model: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        by_model[r["model"]].append(r)
    for model, rs in by_model.items():
        n = len(rs)
        ps = sum(1 for r in rs if r["grade"]["status"] == "pass")
        pa = sum(1 for r in rs if r["grade"]["status"] == "partial")
        fa = sum(1 for r in rs if r["grade"]["status"] == "fail")
        avg = sum(r["grade"]["dsl_score"] for r in rs) / n if n else 0.0
        out[model] = {
            "n": n, "pass": ps, "partial": pa, "fail": fa,
            "accuracy": ps / n if n else 0.0, "avg_dsl": avg,
        }
    return out


def per_category_matrix(records: list[dict], cases: list[dict]) -> dict:
    """{ category: { model: pass_count } }"""
    case_by_id = {c["id"]: c for c in cases}
    cat_totals: dict[str, int] = defaultdict(int)
    for c in cases:
        cat_totals[c["category"]] += 1
    out: dict = {"_totals": dict(cat_totals)}
    for r in records:
        cat = case_by_id[r["case_id"]]["category"]
        m = r["model"]
        out.setdefault(cat, {}).setdefault(m, 0)
        if r["grade"]["status"] == "pass":
            out[cat][m] += 1
    return out


# ---------- report ----------


def render_md(records: list[dict], cases: list[dict], started: str,
              finished: str, models: list[str]) -> str:
    L: list[str] = []
    L.append("# Part 2 Eval — 30 cases × N models")
    L.append("")
    L.append(f"- Started:  {started}")
    L.append(f"- Finished: {finished}")
    L.append(f"- Models: {', '.join(f'`{m}`' for m in models)}")
    L.append(f"- Total runs: **{len(records)}** ({len(cases)} cases × {len(models)} models)")
    L.append(f"- Pass threshold (EXAM_PROMPT §2.4): **{PASS_THRESHOLD:.0%}** = {int(len(cases)*PASS_THRESHOLD)+1}/{len(cases)} or more")
    L.append("")

    # ---- aggregate per-model ----
    L.append("## 1. Per-model accuracy")
    L.append("")
    stats = per_model_stats(records)
    L.append("| model | n | pass | partial | fail | accuracy | avg DSL | ≥85%? |")
    L.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: | :---: |")
    for m in models:
        s = stats.get(m, {"n": 0, "pass": 0, "partial": 0, "fail": 0,
                          "accuracy": 0.0, "avg_dsl": 0.0})
        ok = "✓" if s["accuracy"] >= PASS_THRESHOLD else "✗"
        L.append(f"| `{m}` | {s['n']} | {s['pass']} | {s['partial']} | {s['fail']} | "
                 f"**{s['accuracy']:.1%}** | {s['avg_dsl']:.3f} | {ok} |")
    L.append("")

    # ---- per category × model ----
    L.append("## 2. Per-category × model (pass count)")
    L.append("")
    cm = per_category_matrix(records, cases)
    totals = cm.pop("_totals")
    cat_labels = {
        "A": "A simple", "B": "B complex", "C": "C messy",
        "D": "D ambiguous", "E": "E conflicting", "F": "F typos",
        "G": "G non-English",
    }
    header = "| category | total |" + "".join(f" {m} |" for m in models)
    sep = "| --- | ---: |" + "".join(" ---: |" for _ in models)
    L.append(header); L.append(sep)
    for cat in ["A", "B", "C", "D", "E", "F", "G"]:
        total = totals.get(cat, 0)
        row = f"| {cat_labels[cat]} | {total} |"
        for m in models:
            cnt = cm.get(cat, {}).get(m, 0)
            row += f" {cnt}/{total} |"
        L.append(row)
    L.append("")

    # ---- per-case matrix ----
    L.append("## 3. Per-case status matrix")
    L.append("")
    L.append("Legend: ✓ = pass · ½ = partial · ✗ = fail · ! = LLM/API error")
    L.append("")
    case_by_id = {c["id"]: c for c in cases}
    rec_by = {(r["model"], r["case_id"]): r for r in records}
    header = "| # | cat | mode | NL |" + "".join(f" {m} |" for m in models)
    sep = "| ---: | --- | --- | --- |" + "".join(" :---: |" for _ in models)
    L.append(header); L.append(sep)
    sym_map = {"pass": "✓", "partial": "½", "fail": "✗"}
    for c in cases:
        nl_short = c["nl"]
        if len(nl_short) > 60:
            nl_short = nl_short[:57] + "..."
        nl_short = nl_short.replace("|", "\\|")
        row = f"| {c['id']} | {c['category']} | {c['mode']} | {nl_short} |"
        for m in models:
            r = rec_by.get((m, c["id"]))
            if r is None:
                row += " - |"
            elif r["error"]:
                row += " ! |"
            else:
                row += f" {sym_map[r['grade']['status']]} |"
        L.append(row)
    L.append("")

    # ---- failure samples per model ----
    L.append("## 4. Failure samples per model")
    L.append("")
    for m in models:
        L.append(f"### `{m}`")
        L.append("")
        fails = [r for r in records if r["model"] == m and r["grade"]["status"] != "pass"]
        if not fails:
            L.append("_(no failures)_")
            L.append("")
            continue
        for r in fails:
            c = case_by_id[r["case_id"]]
            L.append(f"- **#{c['id']} ({c['category']}, {c['mode']})** — {c['nl']}")
            L.append(f"  - expected: `{c['expected_query']}` (type={c['expected_type']})")
            if r["error"]:
                L.append(f"  - ERROR: {r['error'][:200]}")
            else:
                p = r["params"]
                L.append(f"  - generated: `{p['search_query']}` (type={p['type']}, first={p['first']})")
                if p.get("assumptions"):
                    for a in p["assumptions"]:
                        L.append(f"      assume: `{a['term']}` → {a['interpreted_as']}")
                g = r["grade"]
                L.append(f"  - grade: {g['status']} (dsl={g['dsl_score']}, type_ok={g['type_match']}, ack={g['ack']}, reason: {g['reason']})")
        L.append("")

    return "\n".join(L) + "\n"


# ---------- main ----------


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
    ap.add_argument("--case", type=int, default=None,
                    help="Run only this case id (debugging)")
    args = ap.parse_args()

    cases = CASES if args.case is None else [c for c in CASES if c["id"] == args.case]
    if not cases:
        print(f"No case with id {args.case}", file=sys.stderr)
        sys.exit(2)

    started = dt.datetime.now().isoformat(timespec="seconds")
    records: list[dict] = []
    total = len(args.models) * len(cases)
    done = 0
    for case in cases:
        for model in args.models:
            done += 1
            r = run_case(model, case)
            tag = r["grade"]["status"][:4].upper()
            if r["error"]:
                tag = "ERR"
            print(f"[{done:>3}/{total}] {model:30s} #{case['id']:>2} {tag} ({r['elapsed']:.1f}s) {r['grade']['reason']}",
                  file=sys.stderr, flush=True)
            records.append(r)

    finished = dt.datetime.now().isoformat(timespec="seconds")
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = DOCS / f"eval_30_{ts}.json"
    md_path   = DOCS / f"eval_30_{ts}.md"

    json_path.write_text(json.dumps({
        "started": started, "finished": finished,
        "models": args.models, "cases": cases, "records": records,
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    md_path.write_text(render_md(records, cases, started, finished, args.models),
                       encoding="utf-8")

    print(f"\nSaved JSON: {json_path}", file=sys.stderr)
    print(f"Saved MD:   {md_path}", file=sys.stderr)

    # Headline
    stats = per_model_stats(records)
    print("\n=== HEADLINE ===", file=sys.stderr)
    for m in args.models:
        s = stats.get(m, {})
        if not s:
            continue
        ok = "PASS" if s["accuracy"] >= PASS_THRESHOLD else "FAIL"
        print(f"  {m:30s} accuracy={s['accuracy']:.1%}  ({s['pass']}/{s['n']})  [{ok} ≥85%]",
              file=sys.stderr)


if __name__ == "__main__":
    main()
