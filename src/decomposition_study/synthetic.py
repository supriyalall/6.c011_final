from __future__ import annotations

"""
Synthetic experiment outcomes for development / sanity checks without running agents.

The generative story encodes a known confound (harder tasks correlate with both
failure and a spurious feature) plus a structural signal so confound analysis is non-trivial.
"""

import hashlib
import math

import numpy as np

from decomposition_study.data.results_schema import ExperimentResult
from decomposition_study.features.extractors import TaskFeatureRow
from decomposition_study.types import CodingTask


def _stable_float(task_id: str, salt: str) -> float:
    h = hashlib.sha256(f"{salt}:{task_id}".encode()).digest()
    return int.from_bytes(h[:8], "big") / (2**64)


def generate_synthetic_results(
    tasks: list[CodingTask], rows: list[TaskFeatureRow], seed: int = 0
) -> list[ExperimentResult]:
    if len(tasks) != len(rows):
        raise ValueError("tasks and feature rows must align")
    rng = np.random.default_rng(seed)
    results: list[ExperimentResult] = []
    for task, fr in zip(tasks, rows):
        # Difficulty index (positively correlates with failure).
        difficulty = (
            0.45 * fr.statement_len_log
            + 0.35 * fr.ast_nodes_log
            + 0.2 * fr.cyclomatic_approx
        )
        # Structural "decomposability" index (true positive signal for decomp advantage).
        structure = (
            0.4 * fr.compositionality_steps
            + 0.25 * fr.independence_lexical
            - 0.15 * fr.coupling_calls
        )
        noise_m = 0.35 * rng.standard_normal()
        noise_d = 0.35 * rng.standard_normal()
        h = _stable_float(task.task_id, "pair")

        logit_mono = -2.2 + 1.1 * difficulty + noise_m
        logit_decomp = (
            -1.5
            + 0.95 * difficulty
            - 0.45 * structure
            + noise_d
            + 0.15 * math.sin(13.0 * h)
        )

        mono = _sigmoid(logit_mono) > rng.random()
        decomp = _sigmoid(logit_decomp) > rng.random()

        # Keep some tasks where decomposition uniquely saves (structure matters).
        if structure > 6.0 and difficulty > 3.5 and rng.random() < 0.25:
            decomp, mono = True, False

        results.append(
            ExperimentResult(
                task_id=task.task_id,
                monolithic_pass=bool(mono),
                decomposed_pass=bool(decomp),
            )
        )
    return results


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))
