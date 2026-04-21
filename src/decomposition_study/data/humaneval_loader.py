from __future__ import annotations

from typing import Any

from decomposition_study.types import CodingTask


def load_humaneval_tasks() -> list[CodingTask]:
    """Load HumanEval problems (164 function-level tasks with prompts and entry points)."""
    try:
        from human_eval.data import HUMAN_EVAL  # type: ignore[import-untyped]
    except ImportError as e:
        raise ImportError(
            "Install optional dependency: pip install human-eval"
        ) from e

    tasks: list[CodingTask] = []
    for row in HUMAN_EVAL:
        tasks.append(
            CodingTask(
                task_id=str(row["task_id"]),
                dataset="humaneval",
                statement=_extract_statement(row),
                code_context=str(row.get("prompt", "")),
                metadata={
                    "entry_point": row.get("entry_point"),
                    "canonical_solution_present": "canonical_solution" in row,
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
