from __future__ import annotations

import ast
import math
import re
from dataclasses import dataclass
from statistics import mean, pstdev

from decomposition_study.types import CodingTask


_WORD = re.compile(r"[a-zA-Z]{3,}")


@dataclass(frozen=True)
class TaskFeatureRow:
    task_id: str
    dataset: str
    # Difficulty / scale proxies
    statement_len_log: float
    code_len_log: float
    ast_nodes_log: float
    num_functions: float
    cyclomatic_approx: float
    # Structural proxies
    coupling_imports: float
    coupling_calls: float
    compositionality_steps: float
    independence_lexical: float


def extract_feature_row(task: CodingTask) -> TaskFeatureRow:
    stmt = task.statement
    code = task.code_context or ""
    combined = f"{stmt}\n{code}"

    n_stmt = len(stmt)
    n_code = len(code)
    ast_nodes, n_funcs, cyclo = _ast_stats(code)
    coupling_imports = float(_count_import_lines(code))
    coupling_calls = float(_approx_external_calls(code))
    comp_steps = float(_compositionality_steps(stmt))
    indep = float(_independence_score(stmt))

    return TaskFeatureRow(
        task_id=task.task_id,
        dataset=task.dataset,
        statement_len_log=math.log1p(n_stmt),
        code_len_log=math.log1p(n_code),
        ast_nodes_log=math.log1p(ast_nodes),
        num_functions=float(n_funcs),
        cyclomatic_approx=float(cyclo),
        coupling_imports=coupling_imports,
        coupling_calls=coupling_calls,
        compositionality_steps=comp_steps,
        independence_lexical=indep,
    )


def features_to_vector(row: TaskFeatureRow, include_difficulty: bool = True) -> list[float]:
    structural = [
        row.coupling_imports,
        row.coupling_calls,
        row.compositionality_steps,
        row.independence_lexical,
    ]
    difficulty = [
        row.statement_len_log,
        row.code_len_log,
        row.ast_nodes_log,
        row.num_functions,
        row.cyclomatic_approx,
    ]
    if include_difficulty:
        return difficulty + structural
    return structural


FEATURE_NAMES_FULL: tuple[str, ...] = (
    "statement_len_log",
    "code_len_log",
    "ast_nodes_log",
    "num_functions",
    "cyclomatic_approx",
    "coupling_imports",
    "coupling_calls",
    "compositionality_steps",
    "independence_lexical",
)

FEATURE_NAMES_STRUCTURAL_ONLY: tuple[str, ...] = (
    "coupling_imports",
    "coupling_calls",
    "compositionality_steps",
    "independence_lexical",
)

FEATURE_GROUPS: dict[str, tuple[str, ...]] = {
    "task_description": ("statement_len_log", "compositionality_steps", "independence_lexical"),
    "code_size": ("code_len_log", "ast_nodes_log", "num_functions"),
    "graph_structure": ("cyclomatic_approx", "coupling_imports", "coupling_calls"),
    "all": FEATURE_NAMES_FULL,
}


def _ast_stats(code: str) -> tuple[int, int, int]:
    if not code.strip():
        return 0, 0, 0
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return max(1, len(code) // 40), 0, 1

    nodes = sum(1 for _ in ast.walk(tree))
    funcs = sum(1 for n in ast.walk(tree) if isinstance(n, ast.FunctionDef))
    branches = sum(
        1
        for n in ast.walk(tree)
        if isinstance(
            n, (ast.If, ast.For, ast.While, ast.Try, ast.BoolOp, ast.comprehension)
        )
    )
    return nodes, funcs, max(1, branches)


def _count_import_lines(code: str) -> int:
    n = 0
    for line in code.splitlines():
        s = line.strip()
        if s.startswith("import ") or s.startswith("from "):
            n += 1
    return n


def _approx_external_calls(code: str) -> int:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return 0

    calls = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id not in {"print", "range", "len"}:
                calls += 1
            elif isinstance(node.func, ast.Attribute):
                calls += 1
    return calls


def _compositionality_steps(statement: str) -> int:
    """Heuristic: enumerate steps / goals in the natural-language spec."""
    if not statement:
        return 0
    bullets = statement.count("\n-") + statement.count("\n*") + statement.count("\n•")
    numbered = len(re.findall(r"(?m)^\s*\d+[\).]", statement))
    steps_kw = len(re.findall(r"\b(step|first|then|next|finally)\b", statement.lower()))
    return min(32, bullets + numbered + steps_kw)


def _independence_score(statement: str) -> int:
    """Lexical hint for separable sub-problems (weak heuristic for NL-only tasks)."""
    if not statement:
        return 0
    low = statement.lower()
    hits = 0
    for w in (
        "independently",
        "independent",
        "separate",
        "each",
        "respectively",
        "respectively,",
        "modular",
        "another function",
        "another file",
    ):
        if w in low:
            hits += 1
    return min(10, hits)


def build_design_matrix(
    rows: list[TaskFeatureRow], structural_only: bool
) -> tuple[list[list[float]], list[str]]:
    names = (
        list(FEATURE_NAMES_STRUCTURAL_ONLY)
        if structural_only
        else list(FEATURE_NAMES_FULL)
    )
    include_diff = not structural_only
    X = [features_to_vector(r, include_difficulty=include_diff) for r in rows]
    return X, names


def build_design_matrix_normalized_by_dataset(
    rows: list[TaskFeatureRow], structural_only: bool
) -> tuple[list[list[float]], list[str]]:
    by_dataset: dict[str, list[TaskFeatureRow]] = {}
    for r in rows:
        by_dataset.setdefault(r.dataset, []).append(r)
    vec_map: dict[str, list[float]] = {}
    for ds_rows in by_dataset.values():
        raw = [features_to_vector(r, include_difficulty=not structural_only) for r in ds_rows]
        if not raw:
            continue
        n_features = len(raw[0])
        cols = [[v[i] for v in raw] for i in range(n_features)]
        means = [mean(c) for c in cols]
        stds = [pstdev(c) for c in cols]
        for row, vec in zip(ds_rows, raw):
            out = []
            for i, val in enumerate(vec):
                sd = stds[i]
                out.append(0.0 if sd == 0.0 else (val - means[i]) / sd)
            vec_map[row.task_id] = out
    names = (
        list(FEATURE_NAMES_STRUCTURAL_ONLY)
        if structural_only
        else list(FEATURE_NAMES_FULL)
    )
    return [vec_map[r.task_id] for r in rows], names


def select_feature_subset(
    X: list[list[float]], feature_names: list[str], subset: str
) -> tuple[list[list[float]], list[str]]:
    if subset not in FEATURE_GROUPS:
        raise ValueError(f"Unknown feature subset: {subset}")
    allowed = set(FEATURE_GROUPS[subset])
    idxs = [i for i, name in enumerate(feature_names) if name in allowed]
    if not idxs:
        raise ValueError(f"No features selected for subset: {subset}")
    out = [[row[i] for i in idxs] for row in X]
    return out, [feature_names[i] for i in idxs]
