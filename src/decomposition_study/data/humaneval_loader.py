from __future__ import annotations

from typing import Any

from decomposition_study.prompts import append_plan_then_code_block
from decomposition_study.types import CodingTask


def load_humaneval_tasks(*, plan_then_code: bool = False) -> list[CodingTask]:
    """Load HumanEval problems (164 function-level tasks with prompts and entry points)."""
    try:
        from human_eval.data import read_problems  # type: ignore[import-untyped]
    except ImportError as e:
        raise ImportError(
            "Install optional dependency: pip install human-eval"
        ) from e

    problems = read_problems()
    tasks: list[CodingTask] = []
    for row in problems.values():
        row_d = dict(row)
        prompt = str(row_d.get("prompt", ""))
        if plan_then_code:
            prompt = append_plan_then_code_block(prompt)
            row_d["prompt"] = prompt
        tasks.append(
            CodingTask(
                task_id=str(row_d["task_id"]),
                dataset="humaneval",
                statement=_extract_statement(row_d),
                code_context=prompt,
                metadata={
                    "entry_point": row_d.get("entry_point"),
                    "canonical_solution_present": "canonical_solution" in row_d,
                    "plan_then_code": plan_then_code,
                },
            )
        )
    return tasks


def _extract_statement(row: dict[str, Any]) -> str:
    prompt = str(row.get("prompt", ""))
    if '"""' in prompt:
        try:
            return prompt.split('"""', 2)[1].strip()
        except IndexError:
            pass
    return prompt[:2000]


def humaneval_task_ids() -> list[str]:
    return [t.task_id for t in load_humaneval_tasks()]
