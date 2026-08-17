"""GEOS — GraphQL API Schema.

Strawberry GraphQL schema for all GEOS entities and queries.
Endpoint: /graphql
"""

from __future__ import annotations

import strawberry
from strawberry.scalars import JSON


# ── Types ──────────────────────────────────────────────────────

@strawberry.type
class Province:
    name: str
    population: float
    area_km2: float
    literacy_rate: float
    internet_pct: float
    security_index: float


@strawberry.type
class Company:
    name: str
    sector: str
    revenue: float
    production_cost: float
    tax_burden: float
    corruption_cost: float
    ps_value: float


@strawberry.type
class Resource:
    name: str
    resource_type: str
    annual_production_tons: float
    market_value_per_ton: float
    local_processing_pct: float
    nrv_value: float
    environmental_cost: float


@strawberry.type
class Ministry:
    name: str
    budget: float
    performance_score: float
    corruption_risk: float


@strawberry.type
class Tax:
    name: str
    tax_type: str
    base: float
    rate: float
    compliance_pct: float
    revenue: float


@strawberry.type
class Project:
    name: str
    project_type: str
    cost: float
    snn_contribution: float
    cs_impact: float
    ps_impact: float
    nrv_impact: float


@strawberry.type
class PublicService:
    name: str
    quality_score: float
    willingness_to_pay: float
    actual_price: float
    access_pct: float
    cs_value: float


@strawberry.type
class Indicator:
    name: str
    category: str
    value: float
    unit: str
    year: int
    source: str
    target: float


@strawberry.type
class SNNAggregate:
    total_cs: float
    total_ps: float
    total_gr: float
    total_nrv: float
    total_dwl: float
    total_ec: float
    snn: float
    snn_rate: float


@strawberry.type
class Scenario:
    key: str
    name: str
    description: str
    cs_growth: float
    ps_growth: float
    nrv_growth: float


@strawberry.type
class Prediction:
    scenario: str
    horizon_years: int
    base_snn: float
    final_snn: float
    snn_change_pct: float
    mean_final_snn: float
    ci_5: float
    ci_95: float
    projections: list[JSON]


@strawberry.type
class Dashboard:
    model: str
    formula: str
    snn: JSON
    entity_counts: JSON


# ── Engine singleton ───────────────────────────────────────────

_engine = None
_pred_model = None


def _get_engine():
    global _engine
    if _engine is None:
        from congo_brain.services.ia_gov.snn_engine import SNNOptimizationEngine
        _engine = SNNOptimizationEngine()
        _engine.load_drc_baseline()
    return _engine


def _get_pred():
    global _pred_model
    if _pred_model is None:
        from congo_brain.services.ia_gov.predictor import PredictiveModel
        _pred_model = PredictiveModel()
        _pred_model.load_from_snn_engine(_get_engine())
    return _pred_model


# ── Query ──────────────────────────────────────────────────────

@strawberry.type
class Query:
    @strawberry.field
    def dashboard(self) -> Dashboard:
        e = _get_engine()
        d = e.get_dashboard()
        return Dashboard(model=d["model"], formula=d["formula"],
                         snn=d["snn"], entity_counts=d["entity_counts"])

    @strawberry.field
    def snn(self) -> SNNAggregate:
        e = _get_engine()
        a = e.compute_snn()
        return SNNAggregate(total_cs=a.total_cs, total_ps=a.total_ps,
                            total_gr=a.total_gr, total_nrv=a.total_nrv,
                            total_dwl=a.total_dwl, total_ec=a.total_ec,
                            snn=a.snn, snn_rate=a.snn_rate)

    @strawberry.field
    def provinces(self) -> list[Province]:
        e = _get_engine()
        result = []
        for p in e.provinces:
            result.append(Province(
                name=p["name"],
                population=p.get("population", 0),
                area_km2=p.get("area_km2", 0),
                literacy_rate=p.get("literacy_rate", 0),
                internet_pct=p.get("internet_pct", 0),
                security_index=p.get("security_index", 0),
            ))
        return result

    @strawberry.field
    def companies(self) -> list[Company]:
        e = _get_engine()
        result = []
        for c in e.companies:
            tc = (c.get("production_cost", 0) + c.get("tax_burden", 0)
                  + c.get("admin_cost", 0) + c.get("corruption_cost", 0)
                  + c.get("logistics_cost", 0) + c.get("energy_cost", 0))
            ps = max(0, c.get("revenue", 0) - tc)
            result.append(Company(
                name=c["name"], sector=c.get("sector", ""),
                revenue=c.get("revenue", 0), production_cost=c.get("production_cost", 0),
                tax_burden=c.get("tax_burden", 0), corruption_cost=c.get("corruption_cost", 0),
                ps_value=round(ps, 2),
            ))
        return result

    @strawberry.field
    def resources(self) -> list[Resource]:
        e = _get_engine()
        result = []
        for r in e.resources:
            gv = r.get("annual_production_tons", 0) * r.get("market_value_per_ton", 0) / 1_000_000
            nrv = gv * (1 + r.get("local_processing_pct", 0) / 100)
            result.append(Resource(
                name=r["name"], resource_type=r.get("type", ""),
                annual_production_tons=r.get("annual_production_tons", 0),
                market_value_per_ton=r.get("market_value_per_ton", 0),
                local_processing_pct=r.get("local_processing_pct", 0),
                nrv_value=round(nrv, 2),
                environmental_cost=r.get("environmental_cost", 0),
            ))
        return result

    @strawberry.field
    def ministries(self) -> list[Ministry]:
        e = _get_engine()
        return [Ministry(name=m["name"], budget=m.get("budget", 0),
                         performance_score=m.get("performance_score", 0),
                         corruption_risk=m.get("corruption_risk", 0))
                for m in e.ministries]

    @strawberry.field
    def taxes(self) -> list[Tax]:
        e = _get_engine()
        return [Tax(name=t["name"], tax_type=t.get("type", ""),
                    base=t.get("base", 0), rate=t.get("rate", 0),
                    compliance_pct=t.get("compliance_pct", 0),
                    revenue=t.get("revenue", 0))
                for t in e.taxes]

    @strawberry.field
    def projects(self) -> list[Project]:
        e = _get_engine()
        return [Project(name=p["name"], project_type=p.get("type", ""),
                        cost=p.get("cost", 0), snn_contribution=p.get("snn_contribution", 0),
                        cs_impact=p.get("cs_impact", 0), ps_impact=p.get("ps_impact", 0),
                        nrv_impact=p.get("nrv_impact", 0))
                for p in e.projects]

    @strawberry.field
    def public_services(self) -> list[PublicService]:
        e = _get_engine()
        result = []
        for ps in e.public_services:
            cs = max(0, ps.get("willingness_to_pay", 0) - ps.get("actual_price", 0))
            result.append(PublicService(
                name=ps["name"], quality_score=ps.get("quality_score", 0),
                willingness_to_pay=ps.get("willingness_to_pay", 0),
                actual_price=ps.get("actual_price", 0),
                access_pct=ps.get("access_pct", 0),
                cs_value=round(cs, 2),
            ))
        return result

    @strawberry.field
    def indicators(self) -> list[Indicator]:
        e = _get_engine()
        return [Indicator(name=i["name"], category=i.get("category", ""),
                          value=i.get("value", 0), unit=i.get("unit", ""),
                          year=i.get("year", 0), source=i.get("source", ""),
                          target=i.get("target", 0))
                for i in e.indicators]

    @strawberry.field
    def scenarios(self) -> list[Scenario]:
        from congo_brain.services.ia_gov.predictor import SCENARIOS
        return [Scenario(key=k, name=s.name, description=s.description,
                         cs_growth=s.cs_growth, ps_growth=s.ps_growth,
                         nrv_growth=s.nrv_growth)
                for k, s in SCENARIOS.items()]

    @strawberry.field
    def predict(self, scenario: str = "baseline", years: int = 10) -> Prediction:
        from congo_brain.services.ia_gov.predictor import SCENARIOS
        m = _get_pred()
        if scenario not in SCENARIOS:
            scenario = "baseline"
        r = m.project(SCENARIOS[scenario], years, monte_carlo_runs=50)
        d = r.to_dict()
        return Prediction(
            scenario=d["scenario"], horizon_years=d["horizon_years"],
            base_snn=d["base_snn"], final_snn=d["final_snn"],
            snn_change_pct=d["snn_change_pct"],
            mean_final_snn=d["mean_final_snn"],
            ci_5=d["ci_5"], ci_95=d["ci_95"],
            projections=d["projections"],
        )


schema = strawberry.Schema(query=Query)
