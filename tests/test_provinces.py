"""Invariants for the canonical DRC province reference data."""

from congo_brain.data.provinces import (
    BASELINE_PROVINCES,
    CURRENT_PROVINCE_COUNT,
    HISTORICAL_PROVINCE_MAPPING,
    PROVINCES_DRC,
    TWIN_PROVINCES,
)
from congo_brain.services.ia_gov.collectors import DataCollector
from congo_brain.services.ia_gov.digital_twin import NationalDigitalTwin
from congo_brain.services.ia_gov.snn_engine import SNNOptimizationEngine


def test_current_province_reference_contains_26_unique_provinces() -> None:
    names = [province["name"] for province in PROVINCES_DRC]

    assert CURRENT_PROVINCE_COUNT == 26
    assert len(names) == CURRENT_PROVINCE_COUNT
    assert len(set(names)) == CURRENT_PROVINCE_COUNT
    assert "Kinshasa" in names


def test_historical_mapping_covers_each_current_province_once() -> None:
    current_names = {province["name"] for province in PROVINCES_DRC}
    mapped_names = [name for provinces in HISTORICAL_PROVINCE_MAPPING.values() for name in provinces]

    assert len(HISTORICAL_PROVINCE_MAPPING) == 11
    assert len(mapped_names) == CURRENT_PROVINCE_COUNT
    assert set(mapped_names) == current_names


def test_all_ia_gov_engines_use_the_canonical_26_provinces() -> None:
    assert len(BASELINE_PROVINCES) == CURRENT_PROVINCE_COUNT
    assert len(TWIN_PROVINCES) == CURRENT_PROVINCE_COUNT

    collector = DataCollector()
    collector.load_drc_baseline()
    assert len(collector.province_data) == CURRENT_PROVINCE_COUNT

    snn_engine = SNNOptimizationEngine()
    snn_engine.load_drc_baseline()
    assert len(snn_engine.provinces) == CURRENT_PROVINCE_COUNT

    digital_twin = NationalDigitalTwin()
    digital_twin.load_baseline()
    assert len(digital_twin.provinces) == CURRENT_PROVINCE_COUNT
