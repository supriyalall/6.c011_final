from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path

from decomposition_study.analysis.confounds import compare_with_without_difficulty
from decomposition_study.analysis.routing import (
    evaluate_routing_policy,
    format_baseline_decomposition_table,
    per_dataset_baseline_decomposition,
)
from decomposition_study.analysis.stratified import evaluate_by_difficulty_bins
from decomposition_study.config import DEFAULT_CONFIG
from decomposition_study.data.humaneval_loader import load_humaneval_tasks
from decomposition_study.data.results_schema import load_results_json, results_to_map
from decomposition_study.data.swe_bench_loader import load_swe_bench_lite
from decomposition_study.features.extractors import (
    build_design_matrix,
    build_design_matrix_normalized_by_dataset,
    extract_feature_row,
    select_feature_subset,
)
from decomposition_study.labels import decomposition_wins, label_to_int
from decomposition_study.models.predictor import fit_and_evaluate, fit_model, predict_proba
from decomposition_study.synthetic import generate_synthetic_results


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run decomposition-benefit prediction study.")
    p.add_argument(
        "--datasets",
        nargs="+",
        choices=("humaneval", "swe_bench_lite"),
        default=["humaneval"],
    )
    p.add_argument("--results-path", type=Path)
    p.add_argument("--synthetic-labels", action="store_true")
    p.add_argument(
        "--methods",
        nargs="+",
        choices=("xgboost", "mlp"),
        default=["xgboost", "mlp"],
        help="Primary tree model plus neural alternative.",
    )
    p.add_argument("--normalize-by-dataset", action="store_true")
    p.add_argument("--compare-confounds", action="store_true")
    p.add_argument("--difficulty-stratified-eval", action="store_true")
    p.add_argument("--feature-subset-eval", action="store_true")
    p.add_argument("--cross-dataset-generalization", action="store_true")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--n-splits", type=int, default=5)
    p.add_argument("--swebench-max-rows", type=int, default=500)
    p.add_argument("--routing-threshold", type=float, default=0.5)
    p.add_argument("--baseline-cost", type=float, default=1.0)
    p.add_argument("--decomposition-cost", type=float, default=2.0)
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    tasks = _load_tasks(args.datasets, args.swebench_max_rows)
    rows = [extract_feature_row(t) for t in tasks]
    if args.synthetic_labels:
        results = generate_synthetic_results(tasks, rows, seed=args.seed)
    elif args.results_path is not None:
        results = load_results_json(args.results_path)
    else:
        raise SystemExit("Provide --synthetic-labels or --results-path <json>.")

    results_map = results_to_map(results)
    aligned_rows = []
    y = []
    mono_flags: list[int] = []
    decomp_flags: list[int] = []
    for row in rows:
        res = results_map.get(row.task_id)
        if res is None:
            continue
        aligned_rows.append(row)
        y.append(label_to_int(decomposition_wins(res.monolithic_pass, res.decomposed_pass, DEFAULT_CONFIG)))
        mono_flags.append(int(bool(res.monolithic_pass)))
        decomp_flags.append(int(bool(res.decomposed_pass)))
    if not aligned_rows:
        raise SystemExit("No overlapping task IDs between tasks and results.")

    matrix_builder = (
        build_design_matrix_normalized_by_dataset
        if args.normalize_by_dataset
        else build_design_matrix
    )
    X_full, names_full = matrix_builder(aligned_rows, structural_only=False)
    print(f"tasks_total: {len(tasks)}")
    print(f"tasks_aligned: {len(aligned_rows)}")
    print(f"datasets: {','.join(args.datasets)}")
    print(f"positive_labels: {sum(y)}")
    print(f"negative_labels: {len(y)-sum(y)}")
    print(f"normalize_by_dataset: {args.normalize_by_dataset}")

    per_ds = per_dataset_baseline_decomposition(aligned_rows, mono_flags, decomp_flags)
    print("\n## Baseline vs decomposition (success rate = mean pass flag per task)")
    print(format_baseline_decomposition_table(per_ds))

    for method in args.methods:
        _run_method_eval(
            method=method,
            rows=aligned_rows,
            X_full=X_full,
            feature_names=names_full,
            y=y,
            mono_flags=mono_flags,
            decomp_flags=decomp_flags,
            args=args,
        )

    if args.cross_dataset_generalization and len(set(r.dataset for r in aligned_rows)) >= 2:
        for method in args.methods:
            _run_cross_dataset_eval(
                method=method,
                rows=aligned_rows,
                X_full=X_full,
                y=y,
                mono_flags=mono_flags,
                decomp_flags=decomp_flags,
                threshold=args.routing_threshold,
                baseline_cost=args.baseline_cost,
                decomposition_cost=args.decomposition_cost,
                seed=args.seed,
            )


def _run_method_eval(
    *,
    method: str,
    rows: list,
    X_full: list[list[float]],
    feature_names: list[str],
    y: list[int],
    mono_flags: list[int],
    decomp_flags: list[int],
    args: argparse.Namespace,
) -> None:
    print(f"\nmethod: {method}")
    _, report = fit_and_evaluate(
        X_full,
        y,
        feature_names,
        model_type=method,  # type: ignore[arg-type]
        n_splits=args.n_splits,
        random_state=args.seed,
    )
    print("classification_full:", asdict(report))

    model, model_name = fit_model(
        X_full,
        y,
        model_type=method,  # type: ignore[arg-type]
        random_state=args.seed,
    )
    probs = predict_proba(model, X_full)
    pred_decompose = [int(p >= args.routing_threshold) for p in probs]
    routing = evaluate_routing_policy(
        mono_flags,
        decomp_flags,
        pred_decompose,
        baseline_cost=args.baseline_cost,
        decomposition_cost=args.decomposition_cost,
    )
    print("routing_policy:", asdict(routing))

    if args.compare_confounds:
        comp = compare_with_without_difficulty(
            rows,
            y,
            model_type=method,  # type: ignore[arg-type]
            normalize_by_dataset=args.normalize_by_dataset,
            n_splits=args.n_splits,
            random_state=args.seed,
        )
        print("confounds_full:", asdict(comp.full))
        print("confounds_structural_only:", asdict(comp.structural_only))

    if args.difficulty_stratified_eval:
        bins = evaluate_by_difficulty_bins(
            rows,
            X_full,
            y,
            feature_names,
            model_type=method,  # type: ignore[arg-type]
            n_splits=args.n_splits,
            random_state=args.seed,
        )
        for b in bins:
            print(
                "difficulty_bin:",
                {
                    "bin_name": b.bin_name,
                    "n_tasks": b.n_tasks,
                    "n_positive": b.n_positive,
                    "report": asdict(b.report) if b.report is not None else None,
                },
            )

    if args.feature_subset_eval:
        for subset in ("task_description", "code_size", "graph_structure", "all"):
            X_sub, names_sub = select_feature_subset(X_full, feature_names, subset)
            _, rep_sub = fit_and_evaluate(
                X_sub,
                y,
                names_sub,
                model_type=method,  # type: ignore[arg-type]
                n_splits=args.n_splits,
                random_state=args.seed,
            )
            print(f"feature_subset_{subset}:", asdict(rep_sub))
    print(f"resolved_model_name: {model_name}")


def _run_cross_dataset_eval(
    *,
    method: str,
    rows: list,
    X_full: list[list[float]],
    y: list[int],
    mono_flags: list[int],
    decomp_flags: list[int],
    threshold: float,
    baseline_cost: float,
    decomposition_cost: float,
    seed: int,
) -> None:
    datasets = sorted({r.dataset for r in rows})
    for train_ds in datasets:
        test_sets = [d for d in datasets if d != train_ds]
        train_idx = [i for i, r in enumerate(rows) if r.dataset == train_ds]
        if not train_idx:
            continue
        X_train = [X_full[i] for i in train_idx]
        y_train = [y[i] for i in train_idx]
        if len(set(y_train)) < 2:
            continue
        model, model_name = fit_model(
            X_train, y_train, model_type=method, random_state=seed
        )
        for test_ds in test_sets:
            test_idx = [i for i, r in enumerate(rows) if r.dataset == test_ds]
            if not test_idx:
                continue
            X_test = [X_full[i] for i in test_idx]
            probs = predict_proba(model, X_test)
            pred = [int(p >= threshold) for p in probs]
            mono = [mono_flags[i] for i in test_idx]
            decomp = [decomp_flags[i] for i in test_idx]
            routing = evaluate_routing_policy(
                mono,
                decomp,
                pred,
                baseline_cost=baseline_cost,
                decomposition_cost=decomposition_cost,
            )
            print(
                "cross_dataset:",
                {
                    "method": method,
                    "resolved_model_name": model_name,
                    "train_dataset": train_ds,
                    "test_dataset": test_ds,
                    "n_test": len(test_idx),
                    "routing": asdict(routing),
                },
            )


def _load_tasks(datasets: list[str], swebench_max_rows: int) -> list:
    out = []
    for ds in datasets:
        if ds == "humaneval":
            out.extend(load_humaneval_tasks())
        elif ds == "swe_bench_lite":
            out.extend(load_swe_bench_lite(max_rows=swebench_max_rows))
        else:
            raise ValueError(ds)
    return out


if __name__ == "__main__":
    main()
