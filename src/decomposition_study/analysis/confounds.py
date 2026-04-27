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
    build_design_matrix_normalized_by_dataset,
)
from decomposition_study.models.predictor import ModelType, TrainReport, fit_and_evaluate


@dataclass(frozen=True)
class ConfoundComparison:
    full: TrainReport
    structural_only: TrainReport


def compare_with_without_difficulty(
    rows: list[TaskFeatureRow],
    y: list[int],
    *,
    model_type: ModelType = "xgboost",
    normalize_by_dataset: bool = False,
    n_splits: int = 5,
    random_state: int = 0,
) -> ConfoundComparison:
    builder = (
        build_design_matrix_normalized_by_dataset
        if normalize_by_dataset
        else build_design_matrix
    )
    X_full, _ = builder(rows, structural_only=False)
    X_struct, _ = builder(rows, structural_only=True)
    _, full_report = fit_and_evaluate(
        X_full,
        y,
        list(FEATURE_NAMES_FULL),
        model_type=model_type,
        n_splits=n_splits,
        random_state=random_state,
    )
    _, struct_report = fit_and_evaluate(
        X_struct,
        y,
        list(FEATURE_NAMES_STRUCTURAL_ONLY),
        model_type=model_type,
        n_splits=n_splits,
        random_state=random_state,
    )
    return ConfoundComparison(full=full_report, structural_only=struct_report)
