# When Does Task Decomposition Help?

This repository implements the computational pipeline described in the study of **multi-agent coding systems**: learn which **task-level structural features** predict when a **decomposition-based** solver outperforms a **monolithic** one, given **binary pass/fail** outcomes on held-out tests.

## Setup

```bash
cd /path/to/6.c011_final
python -m venv .venv && source .venv/bin/activate
pip install -e ".[humaneval]"
```

## Run

**End-to-end with synthetic labels** (no real agent runs required):

```bash
python scripts/run_study.py --dataset humaneval --synthetic-labels --compare-confounds
```

**With your own experiment results** (from running monolithic vs decomposed agents on the same tasks):

```bash
python scripts/run_study.py --dataset humaneval --results-path data/experiment_results.json
```

Expected JSON: list of objects with `task_id`, `monolithic_pass`, `decomposed_pass` (booleans).

## Project layout

- `src/decomposition_study/data/` — HumanEval loader; optional SWE-Bench / Parquet hooks
- `src/decomposition_study/features/` — structural proxies (coupling, compositionality, independence, difficulty)
- `src/decomposition_study/models/` — binary classifier + evaluation
- `src/decomposition_study/analysis/` — difficulty confound checks (logistic with/without difficulty covariates)

The default formulation is **binary classification** (decomposition helps vs does not), aligned with pass/fail benchmarks; an alternative **regression** path for a continuous “gain” score is noted in code where relevant.
