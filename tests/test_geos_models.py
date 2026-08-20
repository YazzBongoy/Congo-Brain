"""Smoke tests for importability of the GEOS ORM model module."""

import importlib


def test_geos_entities_module_imports() -> None:
    module = importlib.import_module("congo_brain.models.geos.entities")

    assert module.Contract.__tablename__ == "geos_contracts"
