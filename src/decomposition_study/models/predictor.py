from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, average_precision_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


@dataclass(frozen=True)
class TrainReport:
    model_name: str
    auc: float | None
    avg_precision: float | None
    accuracy: float | None
    mean_importance: dict[str, float] | None


def fit_and_evaluate(
    X: list[list[float]],
    y: list[int],
    feature_names: list[str],
    *,
    n_splits: int = 5,
    random_state: int = 0,
) -> tuple[TrainReport, Pipeline]:
    X_arr = np.asarray(X, dtype=float)
    y_arr = np.asarray(y, dtype=int)
    if X_arr.ndim != 2:
        raise ValueError("X must be 2D")
    if len(np.unique(y_arr)) < 2:
        clf = _make_pipeline(random_state)
        clf.fit(X_arr, y_arr)
        return (
            TrainReport(
                model_name="logistic_regression",
                auc=None,
                avg_precision=None,
                accuracy=float(accuracy_score(y_arr, clf.predict(X_arr))),
                mean_importance=_coef_map(clf, feature_names),
            ),
            clf,
        )

    clf = _make_pipeline(random_state)
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    proba = cross_val_predict(
        clf, X_arr, y_arr, cv=cv, method="predict_proba", n_jobs=None
    )[:, 1]
    pred = (proba >= 0.5).astype(int)
    try:
        auc = float(roc_auc_score(y_arr, proba))
    except ValueError:
        auc = None
    try:
        ap = float(average_precision_score(y_arr, proba))
    except ValueError:
        ap = None
    acc = float(accuracy_score(y_arr, pred))

    clf.fit(X_arr, y_arr)
    report = TrainReport(
        model_name="logistic_regression_cv",
        auc=auc,
        avg_precision=ap,
        accuracy=acc,
        mean_importance=_coef_map(clf, feature_names),
    )
    return report, clf


def _make_pipeline(random_state: int) -> Pipeline:
    return Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "clf",
                LogisticRegression(
                    max_iter=2000,
                    class_weight="balanced",
                    random_state=random_state,
                    solver="lbfgs",
                ),
            ),
        ]
    )


def _coef_map(clf: Pipeline, names: list[str]) -> dict[str, float]:
    lr = clf.named_steps["clf"]
    coef = getattr(lr, "coef_", None)
    if coef is None:
        return {}
    flat = np.ravel(coef)
    if flat.shape[0] != len(names):
        return {f"f{i}": float(flat[i]) for i in range(min(len(flat), 9)))}
    return {names[i]: float(flat[i]) for i in range(len(names))}
