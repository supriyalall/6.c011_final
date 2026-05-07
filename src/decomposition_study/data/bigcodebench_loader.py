from __future__ import annotations

import ast
from typing import Any

from decomposition_study.prompts import append_plan_then_code_block
from decomposition_study.types import CodingTask


def load_bigcodebench_hard_tasks(
    *,
    plan_then_code: bool = False,
    split: str = "v0.1.4",
) -> list[CodingTask]:
    """Load BigCodeBench-Hard problems (~148 tasks).

    Each task: a function signature + docstring (`complete_prompt`), a unittest
    test class (`test`), and a list of libraries used (`libs`).
    """
    try:
        from datasets import load_dataset  # type: ignore[import-untyped]
    except ImportError as e:
        raise ImportError(
            "Install optional dependency: pip install datasets"
        ) from e

    ds = load_dataset("bigcode/bigcodebench-hard", split=split)
    tasks: list[CodingTask] = []
    for row in ds:
        row_d = dict(row)
        prompt = str(row_d.get("complete_prompt", ""))
        if plan_then_code:
            prompt = append_plan_then_code_block(prompt)
        try:
            libs = ast.literal_eval(str(row_d.get("libs", "[]")))
            if not isinstance(libs, list):
                libs = []
        except (ValueError, SyntaxError):
            libs = []
        tasks.append(
            CodingTask(
                task_id=str(row_d["task_id"]),
                dataset="bigcodebench",
                statement=_extract_statement(row_d),
                code_context=prompt,
                metadata={
                    "entry_point": row_d.get("entry_point"),
                    "libs": libs,
                    "plan_then_code": plan_then_code,
                    "split": split,
                },
            )
        )
    return tasks


def _extract_statement(row: dict[str, Any]) -> str:
    instruct = str(row.get("instruct_prompt", "")).strip()
    if instruct:
        return instruct[:2000]
    prompt = str(row.get("complete_prompt", ""))
    if '"""' in prompt:
        try:
            return prompt.split('"""', 2)[1].strip()
        except IndexError:
            pass
    return prompt[:2000]
