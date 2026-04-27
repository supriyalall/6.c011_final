from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class PerDatasetOutcomes:
    """Fixed strategies: always run baseline only vs always run decomposition."""

    dataset: str
    n_tasks: int
    baseline_success_rate: float
    decomposition_success_rate: float


def per_dataset_baseline_decomposition(
    rows: list[object], monolithic_pass: list[int], decomposed_pass: list[int]
) -> list[PerDatasetOutcomes]:
    """
    Aggregate per-dataset pass rates for the two non-routed policies.

    `rows` must have a `.dataset` string attribute (e.g. TaskFeatureRow).
    """
    n = len(rows)
    if n != len(monolithic_pass) or n != len(decomposed_pass):
        raise ValueError("rows and pass lists must have equal length")
    acc: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0])  # n, sum_m, sum_d
    for row, m, d in zip(rows, monolithic_pass, decomposed_pass, strict=True):
        ds = str(getattr(row, "dataset", "unknown"))
        t = acc[ds]
        t[0] += 1
        t[1] += m
        t[2] += d
    out: list[PerDatasetOutcomes] = []
    for ds in sorted(acc.keys()):
        nt, sm, sd = acc[ds]
        out.append(
            PerDatasetOutcomes(
                dataset=ds,
                n_tasks=nt,
                baseline_success_rate=sm / nt if nt else 0.0,
                decomposition_success_rate=sd / nt if nt else 0.0,
            )
        )
    return out


def format_baseline_decomposition_table(rows: list[PerDatasetOutcomes]) -> str:
    """Markdown table: dataset | n_tasks | baseline | decomposition | delta."""
    if not rows:
        return ""
    lines = [
        "| dataset | n_tasks | baseline_success | decomposition_success | decomp - baseline |",
        "|---|---:|---:|---:|---:|",
    ]
    for r in rows:
        delta = r.decomposition_success_rate - r.baseline_success_rate
        lines.append(
            f"| {r.dataset} | {r.n_tasks} | {r.baseline_success_rate:.4f} | "
            f"{r.decomposition_success_rate:.4f} | {delta:+.4f} |"
        )
    return "\n".join(lines)


@dataclass(frozen=True)
class RoutingReport:
    always_baseline_success: float
    always_decomposition_success: float
    classifier_routed_success: float
    classifier_decomposition_rate: float
    estimated_cost_always_baseline: float
    estimated_cost_always_decomposition: float
    estimated_cost_classifier_routed: float


def evaluate_routing_policy(
    monolithic_pass: list[int],
    decomposed_pass: list[int],
    predicted_decompose: list[int],
    *,
    baseline_cost: float = 1.0,
    decomposition_cost: float = 2.0,
) -> RoutingReport:
    n = len(monolithic_pass)
    if n == 0:
        raise ValueError("No examples for routing evaluation")
    if len(decomposed_pass) != n or len(predicted_decompose) != n:
        raise ValueError("Inputs must have equal length")
    base_success = sum(monolithic_pass) / n
    decomp_success = sum(decomposed_pass) / n
    routed_outcomes = [
        decomposed_pass[i] if predicted_decompose[i] else monolithic_pass[i]
        for i in range(n)
    ]
    routed_success = sum(routed_outcomes) / n
    decomp_rate = sum(predicted_decompose) / n
    return RoutingReport(
        always_baseline_success=base_success,
        always_decomposition_success=decomp_success,
        classifier_routed_success=routed_success,
        classifier_decomposition_rate=decomp_rate,
        estimated_cost_always_baseline=baseline_cost,
        estimated_cost_always_decomposition=decomposition_cost,
        estimated_cost_classifier_routed=(
            baseline_cost * (1.0 - decomp_rate) + decomposition_cost * decomp_rate
        ),
    )
