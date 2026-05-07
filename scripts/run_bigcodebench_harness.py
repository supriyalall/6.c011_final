#!/usr/bin/env python3
"""Run an OpenAI model on BigCodeBench-Hard in two conditions (baseline vs
plan-then-code), score with a subprocess-based unittest runner, and write
per-condition pass JSON plus a paired summary JSON.

Mirrors run_humaneval_harness.py but BCB tests are unittest.TestCase classes,
so we run them in a subprocess (timeout per task) and check the exit code.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from datasets import load_dataset
from openai import OpenAI

from decomposition_study.prompts import (
    SPEC_EXTRACTION_SYSTEM,
    append_plan_then_code_block,
    compose_spec_extraction_user,
    compose_spec_guided_coder_user,
)


SYSTEM_PROMPT = (
    "You are a precise Python programmer. Given a function signature with "
    "imports and a docstring, return the complete function implementation "
    "(body only — keep the signature exactly as given). Wrap your final code "
    "in a ```python fenced block. Use only the libraries already imported in "
    "the prompt unless absolutely necessary."
)


_FENCE_RE = re.compile(r"```(?:python|py)?\s*\n(.*?)```", re.DOTALL)


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
    spec_max_tokens: int = 768,
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


def extract_completion(response: str, entry_point: str) -> str:
    """Return code suitable to append to `complete_prompt`. If the response
    contains a full `def entry_point(...)` definition, return it (it'll shadow
    the prompt's signature). Otherwise treat as body and ensure 4-space
    indentation."""
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
        return "\n" + chosen + "\n"

    lines = []
    for line in chosen.splitlines():
        if line and not line.startswith((" ", "\t")):
            lines.append("    " + line)
        else:
            lines.append(line)
    return "\n" + "\n".join(lines) + "\n"


_RUNNER_SUFFIX = """

if __name__ == "__main__":
    import unittest, sys, io
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestCases)
    runner = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
"""


def score_completion(
    complete_prompt: str,
    completion: str,
    test_code: str,
    timeout: float,
) -> tuple[bool, str]:
    program = complete_prompt + completion + "\n\n" + test_code + _RUNNER_SUFFIX
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as f:
        f.write(program)
        tmp_path = f.name

    try:
        try:
            proc = subprocess.run(
                [sys.executable, tmp_path],
                timeout=timeout,
                capture_output=True,
                text=True,
            )
        except subprocess.TimeoutExpired:
            return False, "timeout"

        if proc.returncode == 0:
            return True, "passed"
        err_tail = (proc.stderr or proc.stdout or "")[-300:].replace("\n", " | ")
        return False, f"failed: {err_tail}"
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def run_condition(
    client: OpenAI,
    model: str,
    rows: list[dict],
    condition: str,
    n_workers: int,
    exec_timeout: float,
    max_tokens: int,
) -> list[dict]:
    cond_label = condition

    def work(row: dict) -> dict:
        tid = row["task_id"]
        base_prompt = row["complete_prompt"]
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

        completion = extract_completion(response, row["entry_point"])
        passed, result_text = score_completion(
            row["complete_prompt"], completion, row["test"], timeout=exec_timeout
        )
        return {
            "task_id": tid,
            "pass": passed,
            "result": result_text,
            "response": response,
            "pass1_response": pass1_response,
            "completion": completion,
            "latency_s": time.time() - t0,
        }

    out: list[dict] = []
    done = 0
    total = len(rows)
    with ThreadPoolExecutor(max_workers=n_workers) as ex:
        futures = {ex.submit(work, r): r["task_id"] for r in rows}
        for fut in as_completed(futures):
            r = fut.result()
            out.append(r)
            done += 1
            mark = "PASS" if r["pass"] else "FAIL"
            print(
                f"[{cond_label} {done}/{total}] {r['task_id']:<22} {mark}  "
                f"({r['result'][:60]})",
                flush=True,
            )
    out.sort(key=lambda r: r["task_id"])
    return out


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="gpt-4o-mini")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--exec-timeout", type=float, default=60.0)
    ap.add_argument("--max-tokens", type=int, default=1500)
    ap.add_argument("--split", default="v0.1.4")
    ap.add_argument("--out-dir", type=Path, default=Path("results/bigcodebench_hard"))
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

    ds = load_dataset("bigcode/bigcodebench-hard", split=args.split)
    rows = [
        {
            "task_id": str(r["task_id"]),
            "complete_prompt": str(r["complete_prompt"]),
            "test": str(r["test"]),
            "entry_point": str(r["entry_point"]),
        }
        for r in ds
    ]
    if args.limit is not None:
        rows = rows[: args.limit]

    args.out_dir.mkdir(parents=True, exist_ok=True)

    per_cond_passes: dict[str, dict[str, bool]] = {}
    for cond in args.conditions:
        print(f"\n=== {cond}: {len(rows)} BCB-Hard tasks, model={args.model} ===")
        results = run_condition(
            client,
            args.model,
            rows,
            condition=cond,
            n_workers=args.workers,
            exec_timeout=args.exec_timeout,
            max_tokens=args.max_tokens,
        )

        passes = [{"task_id": r["task_id"], "pass": r["pass"]} for r in results]
        (args.out_dir / f"{cond}_passes.json").write_text(
            json.dumps(passes, indent=2), encoding="utf-8"
        )
        (args.out_dir / f"{cond}_detail.json").write_text(
            json.dumps(results, indent=2), encoding="utf-8"
        )
        n_pass = sum(1 for r in results if r["pass"])
        print(f"{cond}: {n_pass}/{len(results)} passed "
              f"({n_pass / max(len(results), 1):.1%})")
        per_cond_passes[cond] = {r["task_id"]: r["pass"] for r in results}

    _write_paired_files(args.out_dir, per_cond_passes)


def _write_paired_files(out_dir: Path, per_cond_passes: dict[str, dict[str, bool]]) -> None:
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
