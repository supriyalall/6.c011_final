#!/usr/bin/env python3
"""Compare per-task pass rates: baseline prompts vs plan-then-code prompts."""

from __future__ import annotations

import argparse
from pathlib import Path

from decomposition_study.analysis.prompt_ablation import compare_pass_rates, format_pass_ablation_table
from decomposition_study.data.pass_results_schema import load_pass_results_json


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Compare JSON pass lists: baseline vs plan-then-code (paired by task_id)."
    )
    p.add_argument(
        "--baseline",
        type=Path,
        required=True,
        help='JSON list of {"task_id": "...", "pass": true|false}',
    )
    p.add_argument(
        "--plan-then-code",
        type=Path,
        dest="plan_then_code",
        required=True,
        help="Same schema as baseline, from runs with plan-then-code-augmented prompts.",
    )
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    b = load_pass_results_json(args.baseline)
    p = load_pass_results_json(args.plan_then_code)
    rows = compare_pass_rates(b, p)
    print(format_pass_ablation_table(rows))


if __name__ == "__main__":
    main()
