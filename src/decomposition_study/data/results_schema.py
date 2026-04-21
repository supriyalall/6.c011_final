from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class ExperimentResult:
    task_id: str
    monolithic_pass: bool
    decomposed_pass: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "monolithic_pass": self.monolithic_pass,
            "decomposed_pass": self.decomposed_pass,
        }


def load_results_json(path: str | Path) -> list[ExperimentResult]:
    p = Path(path)
    raw = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("Results JSON must be a list of objects")
    out: list[ExperimentResult] = []
    for row in raw:
        if not isinstance(row, dict):
            raise ValueError("Each result must be an object")
        out.append(
            ExperimentResult(
                task_id=str(row["task_id"]),
                monolithic_pass=_as_bool(row["monolithic_pass"]),
                decomposed_pass=_as_bool(row["decomposed_pass"]),
            )
        )
    return out


def results_to_map(results: Iterable[ExperimentResult]) -> dict[str, ExperimentResult]:
    return {r.task_id: r for r in results}


def _as_bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return bool(v)
    raise TypeError(f"Expected bool, got {type(v)}")


def dump_results_json(path: str | Path, results: list[ExperimentResult]) -> None:
    Path(path).write_text(
        json.dumps([r.to_dict() for r in results], indent=2),
        encoding="utf-8",
    )
