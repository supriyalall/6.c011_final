#!/usr/bin/env python3
"""Characterize the tasks that plan_then_code helps with, in two views:

1. Quantitative: per-outcome group, mean of each structural feature, plus a
   simple effect-size column (Cohen's d on the helps-vs-rest contrast).
2. Qualitative: list every ptc-helps task with its statement / first lines so
   patterns can be eyeballed.
"""

from __future__ import annotations

import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

from decomposition_study.data.bigcodebench_loader import load_bigcodebench_hard_tasks
from decomposition_study.data.humaneval_loader import load_humaneval_tasks
from decomposition_study.features.extractors import (
    FEATURE_NAMES_FULL,
    extract_feature_row,
)


PAIRED_PATH = Path("results/combined_paired_results.json")  # baseline vs plan_then_code


def _outcome_group(monolithic_pass: bool, decomposed_pass: bool) -> str:
    if monolithic_pass and decomposed_pass:
        return "both_pass"
    if not monolithic_pass and not decomposed_pass:
        return "both_fail"
    if not monolithic_pass and decomposed_pass:
        return "ptc_helps"
    return "ptc_hurts"


def main() -> None:
    paired = json.loads(PAIRED_PATH.read_text(encoding="utf-8"))
    outcome_by_tid: dict[str, str] = {}
    for r in paired:
        outcome_by_tid[r["task_id"]] = _outcome_group(
            bool(r["monolithic_pass"]), bool(r["decomposed_pass"])
        )

    tasks = list(load_humaneval_tasks()) + list(load_bigcodebench_hard_tasks())
    rows = []
    for t in tasks:
        og = outcome_by_tid.get(t.task_id)
        if og is None:
            continue
        feat = extract_feature_row(t)
        rows.append((t, feat, og))

    # 1) Quantitative: mean of each feature per outcome group, with Cohen's d
    # (ptc_helps vs all-other) reported alongside.
    by_group: dict[str, list] = defaultdict(list)
    for _, feat, og in rows:
        by_group[og].append(feat)
    helps_feats = by_group.get("ptc_helps", [])
    other_feats = [
        f for og in ("both_pass", "both_fail", "ptc_hurts") for f in by_group.get(og, [])
    ]

    print(f"Total aligned tasks: {len(rows)}")
    print("Outcome group counts:")
    for og in ("ptc_helps", "ptc_hurts", "both_pass", "both_fail"):
        print(f"  {og}: {len(by_group.get(og, []))}")
    print()

    print(
        "## Mean of each feature, by outcome group (combined HumanEval + BCB-Hard)"
    )
    header = "| feature | ptc_helps | ptc_hurts | both_pass | both_fail | Cohen_d (helps vs rest) |"
    sep = "|---|---:|---:|---:|---:|---:|"
    print(header)
    print(sep)

    for fname in FEATURE_NAMES_FULL:
        means = {}
        for og, feats in by_group.items():
            vals = [getattr(f, fname) for f in feats]
            means[og] = statistics.fmean(vals) if vals else float("nan")
        # Cohen's d: helps vs rest
        helps_vals = [getattr(f, fname) for f in helps_feats]
        other_vals = [getattr(f, fname) for f in other_feats]
        if len(helps_vals) >= 2 and len(other_vals) >= 2:
            mh = statistics.fmean(helps_vals)
            mo = statistics.fmean(other_vals)
            sh = statistics.pstdev(helps_vals)
            so = statistics.pstdev(other_vals)
            n1, n2 = len(helps_vals), len(other_vals)
            pooled = math.sqrt(((n1 - 1) * sh**2 + (n2 - 1) * so**2) / (n1 + n2 - 2))
            d = (mh - mo) / pooled if pooled > 0 else 0.0
        else:
            d = float("nan")
        print(
            f"| {fname} | "
            f"{means.get('ptc_helps', float('nan')):.3f} | "
            f"{means.get('ptc_hurts', float('nan')):.3f} | "
            f"{means.get('both_pass', float('nan')):.3f} | "
            f"{means.get('both_fail', float('nan')):.3f} | "
            f"{d:+.2f} |"
        )

    print()
    # Per-dataset breakdown of ptc_helps counts
    print("## ptc_helps counts by dataset")
    by_ds: dict[str, int] = defaultdict(int)
    for t, _, og in rows:
        if og == "ptc_helps":
            by_ds[t.dataset] += 1
    for ds, n in sorted(by_ds.items()):
        print(f"  {ds}: {n}")
    print()

    # 2) Qualitative: list every ptc_helps task with its statement
    print("## ptc_helps tasks (the 18 where decomposition flipped fail to pass)")
    print()
    helps_rows = [(t, f) for t, f, og in rows if og == "ptc_helps"]
    helps_rows.sort(key=lambda x: (x[0].dataset, x[0].task_id))
    for t, f in helps_rows:
        stmt = (t.statement or "").strip().replace("\n", " ")
        if len(stmt) > 280:
            stmt = stmt[:277] + "..."
        print(f"### {t.task_id} ({t.dataset})")
        print(f"  statement: {stmt}")
        print(
            f"  features: stmt_len_log={f.statement_len_log:.2f} "
            f"code_len_log={f.code_len_log:.2f} "
            f"ast_nodes_log={f.ast_nodes_log:.2f} "
            f"num_functions={f.num_functions:.0f} "
            f"comp_steps={f.compositionality_steps:.1f} "
            f"coupling_imports={f.coupling_imports:.0f} "
            f"coupling_calls={f.coupling_calls:.0f}"
        )
        print()


if __name__ == "__main__":
    main()
