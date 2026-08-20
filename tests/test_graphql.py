"""Tests for GEOS GraphQL API."""

import pytest

from congo_brain.api.graphql import build_schema


def test_graphql_requires_authentication(client):
    response = client.post("/graphql", json={"query": "{ __typename }"})
    assert response.status_code == 401


def test_production_schema_disables_introspection():
    result = build_schema("production").execute_sync("{ __schema { queryType { name } } }")
    assert result.errors


class TestGraphQL:
    @pytest.fixture(autouse=True)
    def _authenticate(self, client, auth_headers):
        client.headers.update(auth_headers)

    def test_graphql_endpoint_exists(self, client):
        r = client.post("/graphql", json={"query": "{ __typename }"})
        assert r.status_code == 200
        assert r.json()["data"]["__typename"] == "Query"

    def test_snn_query(self, client):
        r = client.post("/graphql", json={"query": "{ snn { snn totalCs totalPs totalGr } }"})
        assert r.status_code == 200
        data = r.json()["data"]["snn"]
        assert data["snn"] > 0
        assert data["totalCs"] > 0

    def test_provinces_query(self, client):
        r = client.post("/graphql", json={"query": "{ provinces { name population } }"})
        assert r.status_code == 200
        provs = r.json()["data"]["provinces"]
        assert len(provs) >= 5
        assert any(p["name"] == "Kinshasa" for p in provs)

    def test_companies_query(self, client):
        r = client.post("/graphql", json={"query": "{ companies { name sector psValue } }"})
        assert r.status_code == 200
        comps = r.json()["data"]["companies"]
        assert len(comps) >= 3

    def test_resources_query(self, client):
        r = client.post("/graphql", json={"query": "{ resources { name nrvValue } }"})
        assert r.status_code == 200
        res = r.json()["data"]["resources"]
        assert len(res) >= 3

    def test_ministries_query(self, client):
        r = client.post("/graphql", json={"query": "{ ministries { name budget } }"})
        assert r.status_code == 200
        mins = r.json()["data"]["ministries"]
        assert len(mins) >= 4

    def test_taxes_query(self, client):
        r = client.post("/graphql", json={"query": "{ taxes { name revenue } }"})
        assert r.status_code == 200
        taxes = r.json()["data"]["taxes"]
        assert len(taxes) >= 4

    def test_projects_query(self, client):
        r = client.post("/graphql", json={"query": "{ projects { name cost } }"})
        assert r.status_code == 200
        projs = r.json()["data"]["projects"]
        assert len(projs) >= 2

    def test_indicators_query(self, client):
        r = client.post("/graphql", json={"query": "{ indicators { name value category } }"})
        assert r.status_code == 200
        inds = r.json()["data"]["indicators"]
        assert len(inds) >= 8

    def test_dashboard_query(self, client):
        r = client.post("/graphql", json={"query": "{ dashboard { model formula } }"})
        assert r.status_code == 200
        d = r.json()["data"]["dashboard"]
        assert d["model"] == "GEOS"

    def test_scenarios_query(self, client):
        r = client.post("/graphql", json={"query": "{ scenarios { key name } }"})
        assert r.status_code == 200
        scs = r.json()["data"]["scenarios"]
        assert len(scs) >= 5

    def test_predict_query(self, client):
        r = client.post(
            "/graphql", json={"query": '{ predict(scenario: "baseline", years: 5) { scenario finalSnn snnChangePct } }'}
        )
        assert r.status_code == 200
        p = r.json()["data"]["predict"]
        assert p["scenario"] == "Baseline (statu quo)"
        assert p["finalSnn"] != 0

    def test_predict_unknown_fallback(self, client):
        r = client.post("/graphql", json={"query": '{ predict(scenario: "inconnu", years: 3) { scenario } }'})
        assert r.status_code == 200
        assert r.json()["data"]["predict"]["scenario"] == "Baseline (statu quo)"

    def test_combined_query(self, client):
        q = "{ snn { snn } provinces { name } companies { name } }"
        r = client.post("/graphql", json={"query": q})
        assert r.status_code == 200
        d = r.json()["data"]
        assert d["snn"]["snn"] > 0
        assert len(d["provinces"]) >= 5
        assert len(d["companies"]) >= 3

    def test_public_services_query(self, client):
        r = client.post("/graphql", json={"query": "{ publicServices { name csValue } }"})
        assert r.status_code == 200
        svcs = r.json()["data"]["publicServices"]
        assert len(svcs) >= 3
