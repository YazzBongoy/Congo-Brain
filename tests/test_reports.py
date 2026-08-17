"""Tests for GEOS Report Export (PDF + Excel)."""

import pytest

from congo_brain.services.ia_gov.snn_engine import SNNOptimizationEngine
from congo_brain.services.ia_gov.reports import generate_snn_pdf, generate_snn_excel


class TestPDFReport:
    def test_generate_pdf(self):
        engine = SNNOptimizationEngine()
        engine.load_drc_baseline()
        pdf = generate_snn_pdf(engine)
        assert isinstance(pdf, bytes)
        assert len(pdf) > 1000
        assert pdf[:4] == b"%PDF"

    def test_generate_pdf_with_predictions(self):
        engine = SNNOptimizationEngine()
        engine.load_drc_baseline()
        from congo_brain.services.ia_gov.predictor import PredictiveModel, SCENARIOS
        m = PredictiveModel()
        m.load_from_snn_engine(engine)
        preds = m.project(SCENARIOS["baseline"], years=5).to_dict()
        pdf = generate_snn_pdf(engine, preds)
        assert isinstance(pdf, bytes)
        assert len(pdf) > 1000

    def test_generate_pdf_empty_engine(self):
        engine = SNNOptimizationEngine()
        pdf = generate_snn_pdf(engine)
        assert isinstance(pdf, bytes)
        assert pdf[:4] == b"%PDF"


class TestExcelReport:
    def test_generate_excel(self):
        engine = SNNOptimizationEngine()
        engine.load_drc_baseline()
        xlsx = generate_snn_excel(engine)
        assert isinstance(xlsx, bytes)
        assert len(xlsx) > 500
        # XLSX magic number: PK (ZIP-based)
        assert xlsx[:2] == b"PK"

    def test_generate_excel_with_predictions(self):
        engine = SNNOptimizationEngine()
        engine.load_drc_baseline()
        from congo_brain.services.ia_gov.predictor import PredictiveModel, SCENARIOS
        m = PredictiveModel()
        m.load_from_snn_engine(engine)
        preds = m.project(SCENARIOS["optimiste"], years=5).to_dict()
        xlsx = generate_snn_excel(engine, preds)
        assert isinstance(xlsx, bytes)
        assert xlsx[:2] == b"PK"

    def test_generate_excel_empty_engine(self):
        engine = SNNOptimizationEngine()
        xlsx = generate_snn_excel(engine)
        assert isinstance(xlsx, bytes)
        assert xlsx[:2] == b"PK"


class TestReportAPI:
    def test_download_pdf(self, client):
        r = client.get("/api/v1/geos/reports/snn.pdf")
        assert r.status_code == 200
        assert r.headers["content-type"] == "application/pdf"
        assert "attachment" in r.headers.get("content-disposition", "")
        assert r.content[:4] == b"%PDF"

    def test_download_pdf_with_scenario(self, client):
        r = client.get("/api/v1/geos/reports/snn.pdf?scenario=optimiste&years=5")
        assert r.status_code == 200
        assert r.content[:4] == b"%PDF"

    def test_download_excel(self, client):
        r = client.get("/api/v1/geos/reports/snn.xlsx")
        assert r.status_code == 200
        assert "spreadsheet" in r.headers["content-type"]
        assert r.content[:2] == b"PK"

    def test_download_excel_with_scenario(self, client):
        r = client.get("/api/v1/geos/reports/snn.xlsx?scenario=investissement_minier&years=10")
        assert r.status_code == 200
        assert r.content[:2] == b"PK"

    def test_download_pdf_unknown_scenario_fallback(self, client):
        r = client.get("/api/v1/geos/reports/snn.pdf?scenario=inconnu")
        assert r.status_code == 200
        assert r.content[:4] == b"%PDF"
