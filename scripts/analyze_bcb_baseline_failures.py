#!/usr/bin/env python3
"""Summarize where the BigCodeBench-Hard baseline fails.

Uses checked-in pass/detail JSON plus cached BigCodeBench-Hard task metadata.
Writes a markdown report suitable for the results folder and presentation.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from decomposition_study.data.bigcodebench_loader import load_bigcodebench_hard_tasks


ROOT = Path("results/bigcodebench_hard")
OUT = ROOT / "baseline_failure_analysis.md"


def main() -> None:
    baseline = _load_detail(ROOT / "baseline_detail.json")
    plan = _load_detail(ROOT / "plan_then_code_detail.json")
    tasks = {t.task_id: t for t in load_bigcodebench_hard_tasks()}

    common = sorted(set(baseline) & set(plan))
    groups: dict[str, list[str]] = defaultdict(list)
    for tid in common:
        b = bool(baseline[tid]["pass"])
        p = bool(plan[tid]["pass"])
        if b and p:
            groups["both_pass"].append(tid)
        elif b and not p:
            groups["baseline_only"].append(tid)
        elif not b and p:
            groups["decomposition_only"].append(tid)
        else:
            groups["both_fail"].append(tid)

    baseline_fail = groups["decomposition_only"] + groups["both_fail"]
    failure_modes = Counter(_failure_mode(baseline[tid].get("result", "")) for tid in baseline_fail)
    domains = Counter(_domain(tasks[tid].statement, tasks[tid].metadata.get("libs", [])) for tid in baseline_fail)
    fixed_domains = Counter(_domain(tasks[tid].statement, tasks[tid].metadata.get("libs", [])) for tid in groups["decomposition_only"])
    both_fail_domains = Counter(_domain(tasks[tid].statement, tasks[tid].metadata.get("libs", [])) for tid in groups["both_fail"])

    lines: list[str] = []
    lines.append("# BigCodeBench-Hard Baseline Failure Analysis")
    lines.append("")
    lines.append("Source files: `baseline_detail.json`, `plan_then_code_detail.json`, and cached BigCodeBench-Hard task metadata.")
    lines.append("")
    lines.append("## Outcome Counts")
    lines.append("")
    lines.append("| Outcome | Count | Share of 148 tasks |")
    lines.append("|---|---:|---:|")
    for name, label in [
        ("both_pass", "Both baseline and plan-then-code pass"),
        ("baseline_only", "Baseline passes, plan-then-code fails"),
        ("decomposition_only", "Baseline fails, plan-then-code passes"),
        ("both_fail", "Both fail"),
    ]:
        n = len(groups[name])
        lines.append(f"| {label} | {n} | {n / len(common):.1%} |")
    lines.append("")
    lines.append(f"Baseline fails on **{len(baseline_fail)} / {len(common)}** BCB-Hard tasks ({len(baseline_fail) / len(common):.1%}).")
    lines.append(f"Plan-then-code fixes **{len(groups['decomposition_only'])}** of those failures, but **{len(groups['both_fail'])}** remain unsolved by both strategies.")
    lines.append("")

    lines.append("## Baseline Failure Modes")
    lines.append("")
    lines.append("| Failure mode | Count |")
    lines.append("|---|---:|")
    for mode, n in failure_modes.most_common():
        lines.append(f"| {mode} | {n} |")
    lines.append("")

    lines.append("## Where the Baseline Fails")
    lines.append("")
    lines.append("| Task pattern | Baseline failures | Fixed by plan-then-code | Still both fail |")
    lines.append("|---|---:|---:|---:|")
    for domain, n in domains.most_common():
        lines.append(f"| {domain} | {n} | {fixed_domains[domain]} | {both_fail_domains[domain]} |")
    lines.append("")

    lines.append("## Baseline Failures Fixed by Plan-then-code")
    lines.append("")
    lines.append("| task_id | Pattern | Prompt summary |")
    lines.append("|---|---|---|")
    for tid in sorted(groups["decomposition_only"]):
        task = tasks[tid]
        lines.append(f"| {tid} | {_domain(task.statement, task.metadata.get('libs', []))} | {_short(task.statement)} |")
    lines.append("")

    lines.append("## Representative Persistent Baseline Failures")
    lines.append("")
    lines.append("| task_id | Pattern | Failure mode | Prompt summary |")
    lines.append("|---|---|---|---|")
    for tid in sorted(groups["both_fail"])[:20]:
        task = tasks[tid]
        lines.append(
            f"| {tid} | {_domain(task.statement, task.metadata.get('libs', []))} | "
            f"{_failure_mode(baseline[tid].get('result', ''))} | {_short(task.statement)} |"
        )
    lines.append("")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")


def _load_detail(path: Path) -> dict[str, dict]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    return {str(r["task_id"]): r for r in rows}


def _failure_mode(result: str) -> str:
    low = (result or "").lower()
    if "timeout" in low:
        return "timeout"
    if "modulenotfounderror" in low:
        return "missing dependency"
    if "api_error" in low:
        return "api error"
    if "syntaxerror" in low or "indentationerror" in low:
        return "syntax/runtime error"
    if "traceback" in low:
        return "runtime exception"
    return "test assertion / hidden mismatch"


def _domain(statement: str, libs: list[str]) -> str:
    text = f"{statement} {' '.join(map(str, libs))}".lower()
    if any(k in text for k in ["matplotlib", "plot", "chart", "seaborn", "heatmap"]):
        return "plotting / visualization"
    if any(k in text for k in ["pandas", "dataframe", "csv", "excel", "sqlite", "database", "sql"]):
        return "data wrangling / tables"
    if any(k in text for k in ["requests", "urllib", "beautifulsoup", "html", "url", "webpage", "download"]):
        return "web / file I/O"
    if any(k in text for k in ["image", "pillow", "ocr", "cv2", "png", "jpeg"]):
        return "image / OCR processing"
    if any(k in text for k in ["sklearn", "model", "regression", "classification", "cluster"]):
        return "ML/statistics"
    if any(k in text for k in ["datetime", "date", "timezone", "calendar"]):
        return "date/time handling"
    if any(k in text for k in ["json", "xml", "yaml", "parse"]):
        return "structured parsing"
    if any(k in text for k in ["regex", "text", "nlp", "string", "word"]):
        return "text processing"
    return "general library/API use"


def _short(s: str, n: int = 150) -> str:
    one = " ".join((s or "").strip().split())
    one = one.replace("|", "/")
    if len(one) > n:
        return one[: n - 3] + "..."
    return one


if __name__ == "__main__":
    main()
