from __future__ import annotations

# Appended to the original task prompt (HumanEval `prompt`, SWE-Bench problem statement).
# Kept free of triple-quoted docstrings so HumanEval `"""` parsing stays valid when prepended is not used.
PLAN_THEN_CODE_APPENDIX = """
---
Follow this response format (append your answer after the problem above):

PLAN: Outline the sub-steps or sub-tasks you will use. Keep it short (bullets OK). Do not put final solution code here.

CODE: Provide the complete solution (code or patch) as required by the original instructions.
""".strip()


def append_plan_then_code_block(user_facing_text: str) -> str:
    """Append plan-then-code instructions after the benchmark's native prompt."""
    text = user_facing_text.rstrip()
    if not text:
        return PLAN_THEN_CODE_APPENDIX
    return f"{text}\n\n{PLAN_THEN_CODE_APPENDIX}"


# Two-pass "spec-then-code" decomposition strategy.
# Pass 1: extract a structured specification from the docstring (no code).
# Pass 2: implement the function given the original prompt + the extracted spec.

SPEC_EXTRACTION_SYSTEM = (
    "You are reading a Python function specification carefully. Your only job "
    "is to extract structured requirements. Do not write any implementation "
    "code, do not include code blocks, and do not propose a plan."
)

SPEC_EXTRACTION_USER_APPENDIX = """
---
Read the function specification above and produce a structured analysis with
exactly these three sections:

1. REQUIREMENTS: a numbered list of the behavioral requirements stated or
   implied by the docstring.
2. EXAMPLES: any input/output examples present in the docstring, written as
   `<inputs> -> <expected output>`. If none, write "none".
3. EDGE_CASES: a numbered list of edge cases the implementation must handle
   (empty inputs, invalid types, boundary values, error conditions, etc.).

Return plain text. Do not write code, pseudocode, or a plan. Do not restate
the function signature.
""".strip()


def compose_spec_extraction_user(user_facing_text: str) -> str:
    """Compose the Pass-1 user prompt for spec-then-code."""
    text = user_facing_text.rstrip()
    if not text:
        return SPEC_EXTRACTION_USER_APPENDIX
    return f"{text}\n\n{SPEC_EXTRACTION_USER_APPENDIX}"


def compose_spec_guided_coder_user(user_facing_text: str, extracted_spec: str) -> str:
    """Compose the Pass-2 user prompt: original prompt + extracted spec, then code."""
    base = user_facing_text.rstrip()
    spec = extracted_spec.strip()
    return (
        f"{base}\n\n"
        "---\n"
        "Reference specification (extracted from the docstring in a prior analysis pass):\n"
        f"{spec}\n"
        "---\n\n"
        "Now write the implementation. Use the reference specification to guide "
        "your code, especially the EDGE_CASES. Wrap your final code in a "
        "```python fenced block."
    )
