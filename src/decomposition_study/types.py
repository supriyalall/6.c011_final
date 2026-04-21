from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CodingTask:
    task_id: str
    dataset: str
    statement: str
    code_context: str
    metadata: dict[str, Any] = field(default_factory=dict)
