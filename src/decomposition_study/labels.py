from __future__ import annotations

from decomposition_study.config import StudyConfig


def decomposition_wins(
    monolithic_pass: bool,
    decomposed_pass: bool,
    cfg: StudyConfig,
) -> bool | None:
    """
    Binary label for "decomposition helps" from pass/fail flags.

    strict: positive iff decomposition passes and monolithic fails (clean uplift).
    any_gain: positive iff decomposed_pass > monolithic_pass (boolean: strictly better).

    Returns None if the outcome is ambiguous for strict mode in multi-run settings
    (not used for single pass/fail pair).
    """
    if cfg.win_mode == "strict":
        if decomposed_pass and not monolithic_pass:
            return True
        if monolithic_pass and not decomposed_pass:
            return False
        return False

    if cfg.win_mode == "any_gain":
        return bool(decomposed_pass) and not bool(monolithic_pass)

    raise ValueError(cfg.win_mode)


def label_to_int(wins: bool | None) -> int:
    if wins is None:
        return 0
    return int(wins)
