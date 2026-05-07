from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass


def _infer_dataset_group(task_id: str) -> str:
    if task_id.startswith("HumanEval/"):
        return "humaneval"
    return "swe_bench_lite"


@dataclass(frozen=True)
class PassRateRow:
    dataset_group: str
    n_tasks: int
    baseline_pass_rate: float
    plan_then_code_pass_rate: float
    delta: float
    both_pass: int
    baseline_only: int
    plan_then_code_only: int
    neither_pass: int


def compare_pass_rates(
    baseline: dict[str, bool],
    plan_then_code: dict[str, bool],
) -> list[PassRateRow]:
    """Paired comparison on task_ids present in both maps."""
    common = sorted(set(baseline) & set(plan_then_code))
    if not common:
        return []

    by_ds: dict[str, list[str]] = defaultdict(list)
    for tid in common:
        by_ds[_infer_dataset_group(tid)].append(tid)

    rows: list[PassRateRow] = []
    for ds in sorted(by_ds.keys()):
        ids = by_ds[ds]
        n = len(ids)
        bp = sum(1 for t in ids if baseline[t]) / n
        pp = sum(1 for t in ids if plan_then_code[t]) / n
        both = sum(1 for t in ids if baseline[t] and plan_then_code[t])
        b_only = sum(1 for t in ids if baseline[t] and not plan_then_code[t])
        p_only = sum(1 for t in ids if not baseline[t] and plan_then_code[t])
        neither = sum(1 for t in ids if not baseline[t] and not plan_then_code[t])
        rows.append(
            PassRateRow(
                dataset_group=ds,
                n_tasks=n,
                baseline_pass_rate=bp,
                plan_then_code_pass_rate=pp,
                delta=pp - bp,
                both_pass=both,
                baseline_only=b_only,
                plan_then_code_only=p_only,
                neither_pass=neither,
            )
        )
    return rows


def format_pass_ablation_table(rows: list[PassRateRow]) -> str:
    if not rows:
        return "(no overlapping task_ids between baseline and plan-then-code results)"
    lines = [
        "| dataset_group | n_tasks | baseline_pass | plan_then_code_pass | delta | both | baseline_only | ptc_only | neither |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        lines.append(
            f"| {r.dataset_group} | {r.n_tasks} | {r.baseline_pass_rate:.4f} | "
            f"{r.plan_then_code_pass_rate:.4f} | {r.delta:+.4f} | {r.both_pass} | "
            f"{r.baseline_only} | {r.plan_then_code_only} | {r.neither_pass} |"
        )
    return "\n".join(lines)
