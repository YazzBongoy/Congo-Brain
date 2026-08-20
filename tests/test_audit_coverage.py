"""Static policy test ensuring privileged REST operations append audit events."""

import ast
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[1] / "congo_brain" / "api" / "v1"
PUBLIC_AUTH_OPERATIONS = {("auth.py", "login"), ("auth.py", "register")}
PRIVILEGED_COMPUTATION_GETS = {
    ("budget.py", "detect_anomalies"),
    ("budget.py", "anomaly_summary"),
    ("investment.py", "optimize_portfolio"),
    ("investment.py", "compare_scenarios"),
    ("economic.py", "corruption_scenarios"),
    ("economic.py", "moeg_dashboard"),
    ("geos.py", "dashboard"),
    ("geos.py", "compare_scenarios"),
    ("geos.py", "predict_scenario"),
    ("geos.py", "download_snn_pdf"),
    ("geos.py", "download_snn_excel"),
}


def _route_methods(node: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    methods: set[str] = set()
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
            if decorator.func.attr in {"get", "post", "put", "patch", "delete"}:
                methods.add(decorator.func.attr)
    return methods


def _records_audit_event(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    return any(
        isinstance(child, ast.Call)
        and isinstance(child.func, ast.Name)
        and child.func.id == "record_audit_event"
        for child in ast.walk(node)
    )


def test_every_privileged_rest_operation_has_an_audit_hook() -> None:
    missing: list[str] = []
    for source_path in sorted(API_ROOT.glob("*.py")):
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            methods = _route_methods(node)
            route_key = (source_path.name, node.name)
            is_mutation = bool(methods & {"post", "put", "patch", "delete"})
            must_audit = (is_mutation and route_key not in PUBLIC_AUTH_OPERATIONS) or (
                route_key in PRIVILEGED_COMPUTATION_GETS
            )
            if must_audit and not _records_audit_event(node):
                missing.append(f"{source_path.name}:{node.name} ({','.join(sorted(methods))})")

    assert not missing, "Privileged REST routes without audit hooks: " + ", ".join(missing)
