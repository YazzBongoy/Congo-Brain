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
ATOMIC_MUTATION_HANDOFFS = {
    ("auth.py", "create_user"): None,
    ("auth.py", "update_user"): None,
    ("auth.py", "delete_user"): None,
    ("budget.py", "create_budget"): "create_budget",
    ("budget.py", "create_transaction"): "create_transaction",
    ("budget.py", "detect_anomalies"): "run_anomaly_detection",
    ("budget.py", "anomaly_summary"): "run_anomaly_detection_enhanced",
    ("investment.py", "create_investment"): "create_investment",
    ("security.py", "create_alert"): "create_alert",
    ("security.py", "resolve_alert"): "resolve_alert",
    ("transparency.py", "create_report"): "create_report",
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


def test_audited_mutations_cannot_commit_before_the_audit_append() -> None:
    failures: list[str] = []
    for (filename, function_name), service_method in ATOMIC_MUTATION_HANDOFFS.items():
        source_path = API_ROOT / filename
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        node = next(
            item
            for item in tree.body
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == function_name
        )
        if any(
            isinstance(child, ast.Call)
            and isinstance(child.func, ast.Attribute)
            and isinstance(child.func.value, ast.Name)
            and child.func.value.id == "db"
            and child.func.attr == "commit"
            for child in ast.walk(node)
        ):
            failures.append(f"{filename}:{function_name} commits directly")

        if service_method is not None:
            calls = [
                child
                for child in ast.walk(node)
                if isinstance(child, ast.Call)
                and isinstance(child.func, ast.Attribute)
                and child.func.attr == service_method
            ]
            has_deferred_commit = any(
                any(
                    keyword.arg == "commit"
                    and isinstance(keyword.value, ast.Constant)
                    and keyword.value.value is False
                    for keyword in call.keywords
                )
                for call in calls
            )
            if not has_deferred_commit:
                failures.append(f"{filename}:{function_name} does not pass commit=False")

    assert not failures, "Non-atomic audited mutations: " + ", ".join(failures)
