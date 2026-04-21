from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

WinMode = Literal["strict", "any_gain"]


@dataclass(frozen=True)
class StudyConfig:
    """Shared knobs for labels and evaluation."""

    win_mode: WinMode = "strict"
    """strict: label=1 iff decomposed passes and monolithic fails. any_gain: pass_decomp > pass_mono."""


DEFAULT_CONFIG = StudyConfig()
