#!/usr/bin/env python3
"""Export baseline vs plan-then-code prompts for HumanEval and SWE-Bench Lite."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from decomposition_study.data.humaneval_loader import load_humaneval_tasks
from decomposition_study.data.swe_bench_loader import load_swe_bench_lite


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Write JSON with baseline and plan-then-code prompt text per task."
    )
    p.add_argument(
        "--datasets",
        nargs="+",
        choices=("humaneval", "swe_bench_lite"),
        default=["humaneval", "swe_bench_lite"],
    )
    p.add_argument("--swebench-max-rows", type=int, default=500)
    p.add_argument(
        "--output",
        type=Path,
        default=Path("data/prompt_ablation/prompt_pairs.json"),
        help="Output JSON path (parent dirs created).",
    )
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    rows: list[dict] = []
    if "humaneval" in args.datasets:
        base = {t.task_id: t for t in load_humaneval_tasks(plan_then_code=False)}
        ptc = {t.task_id: t for t in load_humaneval_tasks(plan_then_code=True)}
        for tid in sorted(base.keys()):
            b, p = base[tid], ptc[tid]
            rows.append(
                {
                    "task_id": tid,
                    "dataset": "humaneval",
                    "prompt_baseline": b.code_context,
                    "prompt_plan_then_code": p.code_context,
                }
            )
    if "swe_bench_lite" in args.datasets:
        base = {
            t.task_id: t
            for t in load_swe_bench_lite(max_rows=args.swebench_max_rows, plan_then_code=False)
        }
        ptc = {
            t.task_id: t
            for t in load_swe_bench_lite(max_rows=args.swebench_max_rows, plan_then_code=True)
        }
        for tid in sorted(base.keys()):
            b, p = base[tid], ptc[tid]
            rows.append(
                {
                    "task_id": tid,
                    "dataset": "swe_bench_lite",
                    "problem_statement_baseline": b.statement,
                    "problem_statement_plan_then_code": p.statement,
                }
            )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"Wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
