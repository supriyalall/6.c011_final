from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    roc_auc_score,
)
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
try:
    from xgboost import XGBClassifier
except Exception:  # pragma: no cover
    XGBClassifier = None  # type: ignore[assignment]

ModelType = Literal["xgboost", "logistic", "mlp"]


@dataclass(frozen=True)
class TrainReport:
    model_name: str
    auc: float | None
    avg_precision: float | None
    f1: float | None
    accuracy: float | None
    mean_importance: dict[str, float] | None


def fit_and_evaluate(
    X: list[list[float]],
    y: list[int],
    feature_names: list[str],
    *,
    model_type: ModelType = "xgboost",
    n_splits: int = 5,
    random_state: int = 0,
) -> tuple[object, TrainReport]:
    X_arr = np.asarray(X, dtype=float)
    y_arr = np.asarray(y, dtype=int)
    if X_arr.ndim != 2:
        raise ValueError("X must be 2D")
    clf, resolved_name = _make_model(model_type, random_state)
    _apply_class_reweighting(clf, resolved_name, y_arr)
    if len(np.unique(y_arr)) < 2:
        clf.fit(X_arr, y_arr)
        return (
            clf,
            TrainReport(
                model_name=f"{resolved_name}_single_class",
                auc=None,
                avg_precision=None,
                f1=None,
                accuracy=float(accuracy_score(y_arr, clf.predict(X_arr))),
                mean_importance=_importance_map(clf, feature_names, resolved_name),
            ),
        )

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
    try:
        f1 = float(f1_score(y_arr, pred))
    except ValueError:
        f1 = None
    acc = float(accuracy_score(y_arr, pred))

    clf.fit(X_arr, y_arr)
    report = TrainReport(
        model_name=f"{resolved_name}_cv",
        auc=auc,
        avg_precision=ap,
        f1=f1,
        accuracy=acc,
        mean_importance=_importance_map(clf, feature_names, resolved_name),
    )
    return clf, report


def predict_proba(model: object, X: list[list[float]]) -> list[float]:
    arr = np.asarray(X, dtype=float)
    out = model.predict_proba(arr)[:, 1]
    return [float(v) for v in out]


def fit_model(
    X: list[list[float]],
    y: list[int],
    *,
    model_type: ModelType = "xgboost",
    random_state: int = 0,
) -> tuple[object, str]:
    model, resolved_name = _make_model(model_type, random_state)
    y_arr = np.asarray(y, dtype=int)
    _apply_class_reweighting(model, resolved_name, y_arr)
    model.fit(np.asarray(X, dtype=float), y_arr)
    return model, resolved_name


def _apply_class_reweighting(model: object, model_name: str, y: np.ndarray) -> None:
    """Use XGBoost's positive-class weighting for imbalanced labels."""
    if model_name != "xgboost":
        return
    n_pos = int(np.sum(y == 1))
    n_neg = int(np.sum(y == 0))
    if n_pos > 0 and hasattr(model, "set_params"):
        model.set_params(scale_pos_weight=n_neg / n_pos)


def _make_logistic_pipeline(random_state: int) -> Pipeline:
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


def _make_model(model_type: ModelType, random_state: int) -> tuple[object, str]:
    if model_type == "logistic":
        return _make_logistic_pipeline(random_state), "logistic"
    if model_type == "mlp":
        return (
            Pipeline(
                steps=[
                    ("scaler", StandardScaler()),
                    (
                        "clf",
                        MLPClassifier(
                            hidden_layer_sizes=(64, 32),
                            activation="relu",
                            max_iter=600,
                            random_state=random_state,
                        ),
                    ),
                ]
            ),
            "mlp",
        )
    if model_type == "xgboost":
        if XGBClassifier is not None:
            return (
                XGBClassifier(
                    n_estimators=250,
                    max_depth=4,
                    learning_rate=0.06,
                    subsample=0.9,
                    colsample_bytree=0.9,
                    objective="binary:logistic",
                    eval_metric="logloss",
                    random_state=random_state,
                    n_jobs=1,
                ),
                "xgboost",
            )
        return (
            RandomForestClassifier(
                n_estimators=400,
                max_depth=6,
                class_weight="balanced_subsample",
                random_state=random_state,
                n_jobs=1,
            ),
            "xgboost_fallback_random_forest",
        )
    raise ValueError(f"Unknown model_type: {model_type}")


def _importance_map(clf: object, names: list[str], model_name: str) -> dict[str, float]:
    if model_name.startswith("xgboost") and hasattr(clf, "feature_importances_"):
        flat = np.ravel(getattr(clf, "feature_importances_"))
    elif "random_forest" in model_name and hasattr(clf, "feature_importances_"):
        flat = np.ravel(getattr(clf, "feature_importances_"))
    elif model_name == "logistic":
        lr = clf.named_steps["clf"]
        flat = np.ravel(getattr(lr, "coef_", np.array([])))
    elif model_name == "mlp":
        first = clf.named_steps["clf"].coefs_[0]
        flat = np.mean(np.abs(first), axis=1)
    else:
        return {}
    if flat.shape[0] != len(names):
        return {f"f{i}": float(flat[i]) for i in range(min(len(flat), 9))}
    return {names[i]: float(flat[i]) for i in range(len(names))}
