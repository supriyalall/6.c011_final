#!/usr/bin/env python3
"""Run an OpenAI model on HumanEval in two conditions (baseline vs plan-then-code),
score with human_eval.execution.check_correctness, and write per-condition pass JSON
plus a paired summary JSON for run_study.py / compare_pass_rates.py.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from human_eval.data import read_problems
from human_eval.execution import check_correctness
from openai import OpenAI

from decomposition_study.prompts import (
    SPEC_EXTRACTION_SYSTEM,
    append_plan_then_code_block,
    compose_spec_extraction_user,
    compose_spec_guided_coder_user,
)


SYSTEM_PROMPT = (
    "You are a precise Python programmer. When given a function signature and "
    "docstring, return a complete, self-contained implementation. Include any "
    "necessary imports. Wrap the final code in a ```python fenced block."
)


def call_model(
    client: OpenAI,
    model: str,
    user_prompt: str,
    max_tokens: int,
    *,
    system_prompt: str = SYSTEM_PROMPT,
) -> str:
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.0,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content or ""


def generate_for_condition(
    client: OpenAI,
    model: str,
    base_prompt: str,
    condition: str,
    max_tokens: int,
    spec_max_tokens: int = 512,
) -> tuple[str, str | None]:
    """Returns (code_response, pass1_response_or_none)."""
    if condition == "baseline":
        return call_model(client, model, base_prompt, max_tokens), None
    if condition == "plan_then_code":
        return (
            call_model(client, model, append_plan_then_code_block(base_prompt), max_tokens),
            None,
        )
    if condition == "spec_then_code":
        spec = call_model(
            client,
            model,
            compose_spec_extraction_user(base_prompt),
            max_tokens=spec_max_tokens,
            system_prompt=SPEC_EXTRACTION_SYSTEM,
        )
        code = call_model(
            client,
            model,
            compose_spec_guided_coder_user(base_prompt, spec),
            max_tokens=max_tokens,
        )
        return code, spec
    raise ValueError(f"unknown condition: {condition}")


_FENCE_RE = re.compile(r"```(?:python|py)?\s*\n(.*?)```", re.DOTALL)


def extract_completion(response: str, entry_point: str) -> str:
    """Turn an LLM response into a string suitable as `completion` for
    check_correctness, where check_program = prompt + completion + test.

    Strategy: find a fenced code block that defines `entry_point`; pass it as a
    full module body prefixed with a newline so it shadows the prompt's stub.
    Fallback: treat entire response as code.
    """
    fences = _FENCE_RE.findall(response)
    candidates = list(fences) if fences else [response]

    chosen = None
    for c in candidates:
        if re.search(rf"\bdef\s+{re.escape(entry_point)}\s*\(", c):
            chosen = c
            break
    if chosen is None:
        chosen = candidates[-1]

    chosen = chosen.strip("\n")

    if re.search(rf"\bdef\s+{re.escape(entry_point)}\s*\(", chosen):
        # Full def present — leading newline so we don't continue prompt's last line.
        return "\n" + chosen + "\n"

    # Body-only fallback: indent every non-empty unindented line by 4 spaces.
    lines = []
    for line in chosen.splitlines():
        if line and not line.startswith((" ", "\t")):
            lines.append("    " + line)
        else:
            lines.append(line)
    return "\n" + "\n".join(lines) + "\n"


def run_condition(
    client: OpenAI,
    model: str,
    problems: dict,
    condition: str,
    n_workers: int,
    exec_timeout: float,
    max_tokens: int,
) -> list[dict]:
    cond_label = condition

    def work(tid: str, problem: dict) -> dict:
        base_prompt = problem["prompt"]
        t0 = time.time()
        try:
            response, pass1_response = generate_for_condition(
                client, model, base_prompt, condition, max_tokens=max_tokens
            )
            api_error = None
        except Exception as e:
            response = ""
            pass1_response = None
            api_error = repr(e)

        if api_error:
            return {
                "task_id": tid,
                "pass": False,
                "result": f"api_error: {api_error}",
                "response": "",
                "pass1_response": None,
                "completion": "",
                "latency_s": time.time() - t0,
            }

        completion = extract_completion(response, problem["entry_point"])
        score = check_correctness(problem, completion, timeout=exec_timeout)
        return {
            "task_id": tid,
            "pass": bool(score["passed"]),
            "result": score["result"],
            "response": response,
            "pass1_response": pass1_response,
            "completion": completion,
            "latency_s": time.time() - t0,
        }

    rows: list[dict] = []
    done = 0
    total = len(problems)
    with ThreadPoolExecutor(max_workers=n_workers) as ex:
        futures = {ex.submit(work, tid, p): tid for tid, p in problems.items()}
        for fut in as_completed(futures):
            row = fut.result()
            rows.append(row)
            done += 1
            mark = "PASS" if row["pass"] else "FAIL"
            print(
                f"[{cond_label} {done}/{total}] {row['task_id']:<18} {mark}  "
                f"({row['result'][:60]})",
                flush=True,
            )
    rows.sort(key=lambda r: r["task_id"])
    return rows


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="gpt-4o-mini")
    ap.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Run only the first N HumanEval tasks (smoke test). Default: all 164.",
    )
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--exec-timeout", type=float, default=10.0)
    ap.add_argument("--max-tokens", type=int, default=1024)
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=Path("results/humaneval"),
        help="Directory for per-condition pass JSONs and detail JSONs.",
    )
    ap.add_argument(
        "--conditions",
        nargs="+",
        choices=("baseline", "plan_then_code", "spec_then_code"),
        default=["baseline", "plan_then_code"],
    )
    return ap.parse_args()


def main() -> None:
    args = parse_args()

    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("OPENAI_API_KEY not set in environment.")

    client = OpenAI()

    problems = read_problems()
    if args.limit is not None:
        problems = dict(list(problems.items())[: args.limit])

    args.out_dir.mkdir(parents=True, exist_ok=True)

    per_cond_passes: dict[str, dict[str, bool]] = {}
    for cond in args.conditions:
        print(f"\n=== {cond}: {len(problems)} tasks, model={args.model} ===")
        rows = run_condition(
            client,
            args.model,
            problems,
            condition=cond,
            n_workers=args.workers,
            exec_timeout=args.exec_timeout,
            max_tokens=args.max_tokens,
        )

        passes = [{"task_id": r["task_id"], "pass": r["pass"]} for r in rows]
        (args.out_dir / f"{cond}_passes.json").write_text(
            json.dumps(passes, indent=2), encoding="utf-8"
        )
        (args.out_dir / f"{cond}_detail.json").write_text(
            json.dumps(rows, indent=2), encoding="utf-8"
        )
        n_pass = sum(1 for r in rows if r["pass"])
        print(f"{cond}: {n_pass}/{len(rows)} passed "
              f"({n_pass / max(len(rows), 1):.1%})")
        per_cond_passes[cond] = {r["task_id"]: r["pass"] for r in rows}

    _write_paired_files(args.out_dir, per_cond_passes)


def _write_paired_files(out_dir: Path, per_cond_passes: dict[str, dict[str, bool]]) -> None:
    """For each non-baseline condition with both baseline and that condition's
    passes available (either freshly run or already on disk), write a paired
    results JSON in run_study.py's expected schema."""
    if "baseline" not in per_cond_passes:
        baseline_path = out_dir / "baseline_passes.json"
        if baseline_path.exists():
            base_loaded = json.loads(baseline_path.read_text(encoding="utf-8"))
            per_cond_passes["baseline"] = {r["task_id"]: r["pass"] for r in base_loaded}
    if "baseline" not in per_cond_passes:
        return

    base_map = per_cond_passes["baseline"]
    for cond, cond_map in per_cond_passes.items():
        if cond == "baseline":
            continue
        common = sorted(set(base_map) & set(cond_map))
        paired = [
            {
                "task_id": tid,
                "monolithic_pass": base_map[tid],
                "decomposed_pass": cond_map[tid],
            }
            for tid in common
        ]
        legacy_name = "paired_results.json" if cond == "plan_then_code" else None
        out_name = f"paired_baseline_vs_{cond}.json"
        (out_dir / out_name).write_text(json.dumps(paired, indent=2), encoding="utf-8")
        if legacy_name:
            (out_dir / legacy_name).write_text(json.dumps(paired, indent=2), encoding="utf-8")
        n = len(paired)
        b_rate = sum(1 for r in paired if r["monolithic_pass"]) / max(n, 1)
        d_rate = sum(1 for r in paired if r["decomposed_pass"]) / max(n, 1)
        print(
            f"\nPaired baseline vs {cond} ({n} tasks): "
            f"baseline={b_rate:.1%}  {cond}={d_rate:.1%}  Δ={d_rate - b_rate:+.4f}"
        )
        print(f"Wrote {out_dir / out_name}")


if __name__ == "__main__":
    main()
