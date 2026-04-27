from __future__ import annotations

from dataclasses import dataclass

from decomposition_study.features.extractors import TaskFeatureRow
from decomposition_study.models.predictor import ModelType, TrainReport, fit_and_evaluate


@dataclass(frozen=True)
class DifficultyBinReport:
    bin_name: str
    n_tasks: int
    n_positive: int
    report: TrainReport | None


def evaluate_by_difficulty_bins(
    rows: list[TaskFeatureRow],
    X: list[list[float]],
    y: list[int],
    feature_names: list[str],
    *,
    model_type: ModelType,
    n_splits: int = 5,
    random_state: int = 0,
) -> list[DifficultyBinReport]:
    if not rows:
        return []
    scores = [r.statement_len_log + r.ast_nodes_log + r.cyclomatic_approx for r in rows]
    ordered = sorted(scores)
    t1 = _quantile(ordered, 1.0 / 3.0)
    t2 = _quantile(ordered, 2.0 / 3.0)
    idx_map = {"low": [], "medium": [], "high": []}
    for i, s in enumerate(scores):
        if s <= t1:
            idx_map["low"].append(i)
        elif s <= t2:
            idx_map["medium"].append(i)
        else:
            idx_map["high"].append(i)

    out: list[DifficultyBinReport] = []
    for name in ("low", "medium", "high"):
        idxs = idx_map[name]
        y_bin = [y[i] for i in idxs]
        if len(idxs) < 6 or len(set(y_bin)) < 2:
            out.append(DifficultyBinReport(name, len(idxs), sum(y_bin), None))
            continue
        X_bin = [X[i] for i in idxs]
        _, rep = fit_and_evaluate(
            X_bin,
            y_bin,
            feature_names,
            model_type=model_type,
            n_splits=min(n_splits, max(2, min(5, len(idxs) // 2))),
            random_state=random_state,
        )
        out.append(DifficultyBinReport(name, len(idxs), sum(y_bin), rep))
    return out


def _quantile(sorted_vals: list[float], q: float) -> float:
    if not sorted_vals:
        return 0.0
    idx = int(q * (len(sorted_vals) - 1))
    return sorted_vals[max(0, min(len(sorted_vals) - 1, idx))]
