# Decomposition Study Results - HumanEval

Model: `gpt-4o-mini` (OpenAI), temperature 0.

Main decomposition strategy: `plan_then_code`, a single-prompt appendix asking
the model to write a short plan before code. HumanEval scoring uses
`human_eval.execution.check_correctness`.

## Dataset

| Dataset | Tasks | Positive labels | Negative labels |
|---|---:|---:|---:|
| HumanEval | 164 | 10 | 154 |

A positive label means the decomposition run passed and the baseline run failed.
If both passed, the task is treated as baseline-sufficient because the direct
prompt has lower prompting overhead.

## Baseline vs Decomposition

| Policy | Correct | Success rate |
|---|---:|---:|
| Always-baseline | 141 / 164 | 85.98% |
| Always-plan-then-code | 146 / 164 | 89.02% |

Discordant pairs:

| both pass | baseline only | decomposition only | neither |
|---:|---:|---:|---:|
| 136 | 5 | 10 | 13 |

Plan-then-code improves HumanEval by 5 net tasks, or +3.05 percentage points.

## XGBoost Routing

The primary router uses 9 task-level features and XGBoost. Because the positive
class is rare, XGBoost is trained with positive-class reweighting
(`scale_pos_weight = n_negative / n_positive`).

| Metric | Value |
|---|---:|
| AUROC | 0.480 |
| AUPRC | 0.076 |
| F1 | 0.000 |
| Accuracy | 0.909 |

| Policy | Success | Decomposition rate | Estimated cost |
|---|---:|---:|---:|
| Always-baseline | 85.98% | 0.00% | 1.00 |
| Always-plan-then-code | 89.02% | 100.00% | 2.00 |
| XGBoost-routed | 92.07% | 6.10% | 1.06 |

The fitted routed policy exceeds always-decomposition success while applying
decomposition to only 10 of 164 tasks. This supports the cost-control use case,
although the classifier metrics remain weak because there are only 10 positive
examples.

## Feature Ablation

XGBoost feature-subset results:

| Feature subset | AUROC | AUPRC |
|---|---:|---:|
| Task-description | 0.456 | 0.062 |
| Code-size | 0.651 | 0.145 |
| Graph-structure | 0.386 | 0.049 |
| All features | 0.480 | 0.076 |

The strongest HumanEval signal comes from code-size features rather than the
full structural feature set. This suggests that the current proxies only weakly
capture the semantic notion of decomposability.

## Difficulty-Stratified Results

Difficulty bins use `statement_len_log + ast_nodes_log + cyclomatic_approx`.

| Bin | Tasks | Positive labels | AUROC | AUPRC |
|---|---:|---:|---:|---:|
| Low | 55 | 2 | 0.594 | 0.189 |
| Medium | 54 | 5 | 0.557 | 0.124 |
| High | 55 | 3 | 0.615 | 0.120 |

The small number of positives per bin makes these estimates noisy. The useful
takeaway is qualitative: decomposition benefit appears sparse across all
difficulty levels rather than concentrated only in the hardest bucket.

## File Index

| File | Contents |
|---|---|
| `humaneval/baseline_passes.json` | Per-task baseline pass flags |
| `humaneval/plan_then_code_passes.json` | Per-task plan-then-code pass flags |
| `humaneval/paired_results.json` | Paired baseline vs plan-then-code labels |
| `humaneval/study_output.txt` | Full HumanEval-only `run_study.py` output |
| `humaneval/spec_then_code_passes.json` | Optional two-pass decomposition comparison |
