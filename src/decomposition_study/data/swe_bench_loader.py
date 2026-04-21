from __future__ import annotations

"""
SWE-Bench (~2,294 instances) can be loaded from HuggingFace `datasets` or local Parquet.
This module provides a thin adapter so the same feature pipeline applies.

Install: pip install '.[swebench]'

Example::

    from datasets import load_dataset
    ds = load_dataset("princeton-nlp/SWE-bench_Lite", split="test")
"""

from decomposition_study.types import CodingTask


def load_swe_bench_lite(split: str = "test", max_rows: int | None = None) -> list[CodingTask]:
    try:
        from datasets import load_dataset  # type: ignore[import-untyped]
    except ImportError as e:
        raise ImportError("Install optional dependency: pip install datasets") from e

    ds = load_dataset("princeton-nlp/SWE-bench_Lite", split=split)
    tasks: list[CodingTask] = []
    for i, row in enumerate(ds):
        if max_rows is not None and i >= max_rows:
            break
        row_d = dict(row)
        tid = str(row_d.get("instance_id", f"swebench_{i}"))
        problem = str(row_d.get("problem_statement", ""))
        repo = str(row_d.get("repo", ""))
        tasks.append(
            CodingTask(
                task_id=tid,
                dataset="swe_bench_lite",
                statement=problem[:50000],
                code_context=str(row_d.get("patch", ""))[:2000],
                metadata={"repo": repo},
            )
        )
    return tasks


def task_from_row(instance_id: str, problem_statement: str, patch: str, repo: str) -> CodingTask:
    return CodingTask(
        task_id=instance_id,
        dataset="swe_bench",
        statement=problem_statement,
        code_context=patch[:5000],
        metadata={"repo": repo},
    )
