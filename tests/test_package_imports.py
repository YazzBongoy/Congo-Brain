"""Smoke-test every installable Congo-Brain source module for import integrity."""

from __future__ import annotations

import importlib
from pathlib import Path

import congo_brain


def test_all_package_modules_import() -> None:
    package_root = Path(congo_brain.__file__).resolve().parent
    failures: list[str] = []

    for source in sorted(package_root.rglob("*.py")):
        relative = source.relative_to(package_root)
        if relative.name == "__main__.py":
            # Typer's executable entry point intentionally starts the CLI on import.
            continue
        parts = relative.with_suffix("").parts
        if parts[-1] == "__init__":
            parts = parts[:-1]
        module_name = ".".join((congo_brain.__name__, *parts))
        try:
            importlib.import_module(module_name)
        except Exception as exc:  # noqa: BLE001 - aggregate every broken module in one report
            failures.append(f"{module_name}: {type(exc).__name__}: {exc}")

    assert not failures, "Package import failures:\n" + "\n".join(failures)
