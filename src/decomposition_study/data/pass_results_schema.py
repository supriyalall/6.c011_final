from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PassResult:
    """Single-strategy outcome: did the run pass tests for this task?"""

    task_id: str
    pass_: bool

    def to_dict(self) -> dict[str, Any]:
        return {"task_id": self.task_id, "pass": bool(self.pass_)}


def load_pass_results_json(path: str | Path) -> dict[str, bool]:
    """Load JSON list of {task_id, pass} into a task_id -> pass map."""
    p = Path(path)
    raw = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("Pass results JSON must be a list of objects")
    out: dict[str, bool] = {}
    for row in raw:
        if not isinstance(row, dict):
            raise ValueError("Each row must be an object")
        tid = str(row["task_id"])
        v = row.get("pass")
        if isinstance(v, bool):
            out[tid] = v
        elif isinstance(v, (int, float)):
            out[tid] = bool(v)
        else:
            raise TypeError(f"pass must be bool, got {type(v)}")
    return out


def dump_pass_results_json(path: str | Path, results: list[PassResult]) -> None:
    Path(path).write_text(
        json.dumps([r.to_dict() for r in results], indent=2),
        encoding="utf-8",
    )
