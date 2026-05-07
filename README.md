# When Does Task Decomposition Help on HumanEval?

This repository implements the HumanEval-only version of our decomposition-routing
study. The goal is to learn which task-level structural features predict when a
plan-then-code decomposition prompt outperforms a direct baseline prompt.

Team members: Xiaoyang Cao, Supriya Lall.

## Method

We model decomposition benefit as a binary classification task over selected
features. The primary classifier is XGBoost, trained to predict whether
decomposition outperforms the baseline on a HumanEval task. This is a good fit
for the project because the data are tabular, structured, and small: the current
study uses all 164 HumanEval tasks and a 9-feature task-level representation.
The feature space is intentionally low-dimensional so the model remains
interpretable and less prone to overfitting than a larger neural model.

The decomposition strategy is a plan-then-code prompt appendix. Each HumanEval
problem is evaluated twice with the same model and temperature: once with the
original direct prompt and once with the appended planning instruction. The
binary label is positive when the decomposition run passes and the baseline run
fails. When both strategies pass, the baseline is treated as sufficient because
it avoids the extra decomposition prompt cost.

The extracted features are:

- Difficulty and scale proxies: `statement_len_log`, `code_len_log`,
  `ast_nodes_log`, `num_functions`, and `cyclomatic_approx`.
- Structural proxies: `coupling_imports`, `coupling_calls`,
  `compositionality_steps`, and `independence_lexical`.

We incorporate four evaluation modifications:

- HumanEval-only normalization: because the current study uses a single
  function-level benchmark, cross-dataset Z-score normalization is not applied.
  The `--normalize-by-dataset` option remains available for future combined
  benchmark runs.
- Automated stratified training: tasks are split into low, medium, and high
  difficulty bins using the combined score
  `statement_len_log + ast_nodes_log + cyclomatic_approx`.
- Class-imbalance handling: decomposition helps only 10 of 164 tasks in the
  full HumanEval run, so XGBoost uses `scale_pos_weight = n_negative / n_positive`.
- Post-hoc interpretability: XGBoost feature importances are reported for the
  full model and for feature-subset ablations. SHAP can be layered on top once
  the baseline router is stable, but the current checked-in output reports
  built-in feature importances.

An alternative approach would be to use a transformer encoder such as CodeBERT
over the problem description and code context, followed by a classification
head. That may capture semantic cues that the current structural features miss,
but it is less interpretable and more data-hungry than the feature-based method.

## Evaluation

Functional correctness is measured with HumanEval Pass@1 using
`human_eval.execution.check_correctness`. We compare three policies:

- Always-baseline: use the direct prompt for every task.
- Always-decomposition: use the plan-then-code prompt for every task.
- Classifier-routed: use decomposition only when the classifier predicts a
  positive decomposition benefit.

Classification quality is measured with AUROC, AUPRC, F1, and accuracy. AUPRC
is especially important because the positive class is rare. Downstream routing
quality is measured by total success rate and estimated computational overhead,
where baseline cost is `1.0` and decomposition cost is `2.0` by default.

For the checked-in full HumanEval plan-then-code run:

| Policy | Success | Decomposition rate | Estimated cost |
|---|---:|---:|---:|
| Always-baseline | 85.98% | 0.00% | 1.00 |
| Always-decomposition | 89.02% | 100.00% | 2.00 |
| XGBoost-routed | 92.07% | 6.10% | 1.06 |

The main interpretation is that HumanEval contains a small number of tasks where
planning helps. The fitted router can exceed the always-decomposition success
rate while using decomposition on far fewer tasks, but classification metrics
remain close to chance because there are only 10 positive examples.

## Setup

```bash
cd /path/to/6.c011_final
python -m venv .venv
source .venv/bin/activate
pip install -e ".[humaneval]"
```

## Run the HumanEval Study

The checked-in HumanEval pass/fail files are in `results/humaneval/`. To rerun
the routing analysis from paired baseline and plan-then-code outcomes:

```bash
python scripts/run_study.py \
  --datasets humaneval \
  --results-path results/humaneval/paired_results.json \
  --methods xgboost mlp \
  --compare-confounds \
  --difficulty-stratified-eval \
  --feature-subset-eval
```

For a smoke-free run of the LLM harness over all 164 tasks, omit `--limit`:

```bash
python scripts/run_humaneval_harness.py \
  --conditions baseline plan_then_code \
  --out-dir results/humaneval
```

Then compare the paired pass rates:

```bash
python scripts/compare_pass_rates.py \
  --baseline results/humaneval/baseline_passes.json \
  --plan-then-code results/humaneval/plan_then_code_passes.json
```

## Project Layout

- `src/decomposition_study/data/` - HumanEval task and result loaders.
- `src/decomposition_study/features/` - structural and difficulty feature
  extraction.
- `src/decomposition_study/models/` - XGBoost/MLP classifiers and evaluation.
- `src/decomposition_study/analysis/` - routing, feature ablation, confound
  checks, and difficulty-stratified evaluation.
- `results/humaneval/` - full HumanEval baseline, plan-then-code, and
  spec-then-code outputs.
