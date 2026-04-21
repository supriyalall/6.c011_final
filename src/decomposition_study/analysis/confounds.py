from __future__ import annotations

"""
Address the confound that harder tasks may benefit from decomposition merely because
they are harder: compare predictive models that include vs exclude explicit difficulty
proxies (length, AST size, cyclomatic approximation).
"""

from dataclasses import dataclass

from decomposition_study.features.extractors import (
    FEATURE_NAMES_FULL,
    FEATURE_NAMES_STRUCTURAL_ONLY,
    TaskFeatureRow,
    build_design_matrix,
)
from decomposition_study.models.predictor import TrainReport, fit_and_evaluate


@dataclass(frozen=True)
class ConfoundComparison:
    full: TrainReport
    structural_only: TrainReport


def compare_with_without_difficulty(
    rows: list[TaskFeatureRow],
    y: list[int],
    *,
    n_splits: int = 5,
    random_state: int = 0,
) -> ConfoundComparison:
    X_full, _ = build_design_matrix(rows, structural_only=False)
    X_struct, _ = build_design_matrix(rows, structural_only=True)
    full_report, _ = fit_and_evaluate(
        X_full,
        y,
        list(FEATURE_NAMES_FULL),
        n_splits=n_splits,
        random_state=random_state,
    )
    struct_report, _ = fit_and_evaluate(
        X_struct,
        y,
        list(FEATURE_NAMES_STRUCTURAL_ONLY),
        n_splits=n_splits,
        random_state=random_state,
    )
    return ConfoundComparison(full=full_report, structural_only=struct_report)
