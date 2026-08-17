"""GEOS Entity Models — 14 tables for the SNN optimization framework.

Each entity feeds into the Surplus National Net:
    SNN = CS + PS + GR + NRV - DWL - EC
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, Float, String, Text, Boolean, DateTime, ForeignKey, Index,
)
from sqlalchemy.orm import relationship

from congo_brain.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ── Province ───────────────────────────────────────────────────

class Province(Base):
    __tablename__ = "geos_provinces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    population = Column(Float, default=0.0)
    area_km2 = Column(Float, default=0.0)
    gdp = Column(Float, default=0.0)
    budget = Column(Float, default=0.0)
    poverty_rate = Column(Float, default=0.0)
    literacy_rate = Column(Float, default=0.0)
    electricity_access = Column(Float, default=0.0)
    water_access = Column(Float, default=0.0)
    internet_access = Column(Float, default=0.0)
    security_index = Column(Float, default=0.0)
    governance_score = Column(Float, default=0.0)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

    # Relationships
    citizens = relationship("Citizen", back_populates="province")
    companies = relationship("Company", back_populates="province")
    projects = relationship("Project", back_populates="province")
    infrastructures = relationship("Infrastructure", back_populates="province")
    public_services = relationship("PublicService", back_populates="province")


# ── Citizen ────────────────────────────────────────────────────

class Citizen(Base):
    __tablename__ = "geos_citizens"

    id = Column(Integer, primary_key=True, index=True)
    province_id = Column(Integer, ForeignKey("geos_provinces.id"))
    name = Column(String(200), nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    income_monthly = Column(Float, default=0.0)
    education_level = Column(String(50), nullable=True)
    employment_status = Column(String(50), nullable=True)
    sector = Column(String(50), nullable=True)  # agriculture, services, industry
    has_electricity = Column(Boolean, default=False)
    has_water = Column(Boolean, default=False)
    has_internet = Column(Boolean, default=False)
    satisfaction_score = Column(Float, default=0.0)  # 0-10
    created_at = Column(DateTime, default=_utcnow)

    province = relationship("Province", back_populates="citizens")


# ── Company ────────────────────────────────────────────────────

class Company(Base):
    __tablename__ = "geos_companies"

    id = Column(Integer, primary_key=True, index=True)
    province_id = Column(Integer, ForeignKey("geos_provinces.id"))
    name = Column(String(200), nullable=False)
    sector = Column(String(100), nullable=True)
    employees = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    production_cost = Column(Float, default=0.0)
    tax_burden = Column(Float, default=0.0)
    admin_cost = Column(Float, default=0.0)
    corruption_cost = Column(Float, default=0.0)
    logistics_cost = Column(Float, default=0.0)
    energy_cost = Column(Float, default=0.0)
    is_formal = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_utcnow)

    province = relationship("Province", back_populates="companies")
    contracts = relationship("Contract", back_populates="company")

    @property
    def producer_surplus(self) -> float:
        total = (self.production_cost + self.tax_burden + self.admin_cost
                 + self.corruption_cost + self.logistics_cost + self.energy_cost)
        return max(0, self.revenue - total)


# ── Ministry ───────────────────────────────────────────────────

class Ministry(Base):
    __tablename__ = "geos_ministries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False)
    sector = Column(String(100), nullable=True)
    budget_allocated = Column(Float, default=0.0)
    budget_executed = Column(Float, default=0.0)
    optimization_score = Column(Float, default=0.0)  # 0-100
    transparency_score = Column(Float, default=0.0)
    performance_score = Column(Float, default=0.0)
    satisfaction_score = Column(Float, default=0.0)
    employees_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=_utcnow)

    projects = relationship("Project", back_populates="ministry")
    budgets = relationship("Budget", back_populates="ministry")

    @property
    def governance_score(self) -> float:
        return round(
            0.40 * self.optimization_score
            + 0.20 * self.transparency_score
            + 0.20 * self.performance_score
            + 0.20 * self.satisfaction_score, 1
        )

    @property
    def execution_rate(self) -> float:
        return round(self.budget_executed / self.budget_allocated * 100, 1) if self.budget_allocated > 0 else 0.0


# ── Budget ─────────────────────────────────────────────────────

class Budget(Base):
    __tablename__ = "geos_budgets"

    id = Column(Integer, primary_key=True, index=True)
    ministry_id = Column(Integer, ForeignKey("geos_ministries.id"))
    year = Column(Integer, nullable=False)
    allocated = Column(Float, default=0.0)
    executed = Column(Float, default=0.0)
    category = Column(String(50), nullable=True)  # current, capital
    source = Column(String(50), nullable=True)  # tax, customs, mining, aid
    created_at = Column(DateTime, default=_utcnow)

    ministry = relationship("Ministry", back_populates="budgets")

    @property
    def execution_rate(self) -> float:
        return round(self.executed / self.allocated * 100, 1) if self.allocated > 0 else 0.0


# ── Resource (Natural) ────────────────────────────────────────

class Resource(Base):
    __tablename__ = "geos_resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    province_id = Column(Integer, ForeignKey("geos_provinces.id"), nullable=True)
    mineral_type = Column(String(50), nullable=True)
    reserves_tons = Column(Float, default=0.0)
    annual_production_tons = Column(Float, default=0.0)
    market_value_per_ton = Column(Float, default=0.0)
    local_processing_pct = Column(Float, default=0.0)
    tax_rate = Column(Float, default=0.0)
    employees = Column(Integer, default=0)
    export_value = Column(Float, default=0.0)
    environmental_cost = Column(Float, default=0.0)
    created_at = Column(DateTime, default=_utcnow)

    @property
    def gross_value(self) -> float:
        return self.annual_production_tons * self.market_value_per_ton / 1_000_000

    @property
    def value_added(self) -> float:
        return self.gross_value * (1 + self.local_processing_pct / 100)

    @property
    def natural_resource_value(self) -> float:
        return self.value_added

    @property
    def tax_revenue(self) -> float:
        return self.gross_value * self.tax_rate / 100


# ── Tax ────────────────────────────────────────────────────────

class Tax(Base):
    __tablename__ = "geos_taxes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    tax_type = Column(String(50), nullable=True)  # income, vat, customs, mining, property
    rate = Column(Float, default=0.0)
    base = Column(Float, default=0.0)  # tax base (M USD)
    revenue = Column(Float, default=0.0)
    compliance_rate = Column(Float, default=0.0)  # %
    evasion_estimate = Column(Float, default=0.0)  # M USD
    year = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=_utcnow)


# ── Project ────────────────────────────────────────────────────

class Project(Base):
    __tablename__ = "geos_projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    ministry_id = Column(Integer, ForeignKey("geos_ministries.id"), nullable=True)
    province_id = Column(Integer, ForeignKey("geos_provinces.id"), nullable=True)
    sector = Column(String(100), nullable=True)
    cost = Column(Float, default=0.0)
    budget_allocated = Column(Float, default=0.0)
    budget_executed = Column(Float, default=0.0)
    # SNN impact estimates
    cs_impact = Column(Float, default=0.0)
    ps_impact = Column(Float, default=0.0)
    gr_impact = Column(Float, default=0.0)
    nrv_impact = Column(Float, default=0.0)
    dwl_impact = Column(Float, default=0.0)
    ec_impact = Column(Float, default=0.0)
    # Meta
    status = Column(String(50), default="planned")  # planned, ongoing, completed, delayed
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    duration_months = Column(Integer, default=0)
    jobs_created = Column(Integer, default=0)
    corruption_risk = Column(Float, default=0.0)
    created_at = Column(DateTime, default=_utcnow)

    ministry = relationship("Ministry", back_populates="projects")
    province = relationship("Province", back_populates="projects")
    contracts = relationship("Contract", back_populates="project")

    @property
    def snn_impact(self) -> float:
        return (self.cs_impact + self.ps_impact + self.gr_impact
                + self.nrv_impact - self.dwl_impact - self.ec_impact)

    @property
    def execution_rate(self) -> float:
        return round(self.budget_executed / self.budget_allocated * 100, 1) if self.budget_allocated > 0 else 0.0


# ── Infrastructure ─────────────────────────────────────────────

class Infrastructure(Base):
    __tablename__ = "geos_infrastructures"

    id = Column(Integer, primary_key=True, index=True)
    province_id = Column(Integer, ForeignKey("geos_provinces.id"))
    name = Column(String(200), nullable=False)
    infra_type = Column(String(50), nullable=True)  # road, bridge, hospital, school, power, water
    length_km = Column(Float, default=0.0)
    capacity = Column(Float, default=0.0)
    condition_score = Column(Float, default=0.0)  # 0-100
    annual_maintenance_cost = Column(Float, default=0.0)
    users_served = Column(Integer, default=0)
    is_functional = Column(Boolean, default=True)
    construction_year = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

    province = relationship("Province", back_populates="infrastructures")


# ── Public Service ─────────────────────────────────────────────

class PublicService(Base):
    __tablename__ = "geos_public_services"

    id = Column(Integer, primary_key=True, index=True)
    province_id = Column(Integer, ForeignKey("geos_provinces.id"))
    name = Column(String(200), nullable=False)
    service_type = Column(String(50), nullable=True)  # health, education, water, electricity, transport, justice
    willingness_to_pay = Column(Float, default=0.0)
    actual_price = Column(Float, default=0.0)
    quality_score = Column(Float, default=0.0)
    access_time_hours = Column(Float, default=0.0)
    indirect_cost = Column(Float, default=0.0)
    coverage_pct = Column(Float, default=0.0)
    satisfaction_pct = Column(Float, default=0.0)
    created_at = Column(DateTime, default=_utcnow)

    province = relationship("Province", back_populates="public_services")

    @property
    def consumer_surplus(self) -> float:
        return max(0, self.willingness_to_pay - self.actual_price - self.indirect_cost)

    @property
    def quality_adjusted_cs(self) -> float:
        return self.consumer_surplus * (self.quality_score / 10) if self.quality_score > 0 else 0


# ── Contract ───────────────────────────────────────────────────

class Contract(Base):
    __tablename__ = "geos_contracts"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("geos_projects.id"), nullable=True)
    company_id = Column(Integer, ForeignKey("geos_companies.id"), nullable=True)
    name = Column(String(200), nullable=False)
    value = Column(Float, default=0.0)
    awarded_value = Column(Float, default=0.0)
    status = Column(String(50), default="awarded")  # awarded, ongoing, completed, cancelled
    award_date = Column(DateTime, nullable=True)
    is_competitive = Column(Boolean, default=True)
    has Beneficial Ownership = Column(Boolean, default=False)
    corruption_flag = Column(Boolean, default=False)
    anomaly_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=_utcnow)

    project = relationship("Project", back_populates="contracts")
    company = relationship("Company", back_populates="contracts")

    @property
    def cost_overrun(self) -> float:
        if self.value > 0:
            return round((self.awarded_value - self.value) / self.value * 100, 1)
        return 0.0


# ── Payment ────────────────────────────────────────────────────

class Payment(Base):
    __tablename__ = "geos_payments"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("geos_contracts.id"), nullable=True)
    amount = Column(Float, default=0.0)
    payment_date = Column(DateTime, nullable=True)
    beneficiary = Column(String(200), nullable=True)
    purpose = Column(String(200), nullable=True)
    is_verified = Column(Boolean, default=False)
    anomaly_flag = Column(Boolean, default=False)
    anomaly_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=_utcnow)


# ── Market ─────────────────────────────────────────────────────

class Market(Base):
    __tablename__ = "geos_markets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    sector = Column(String(100), nullable=True)
    province_id = Column(Integer, ForeignKey("geos_provinces.id"), nullable=True)
    total_revenue = Column(Float, default=0.0)
    total_employment = Column(Integer, default=0)
    avg_price_index = Column(Float, default=0.0)
    competition_index = Column(Float, default=0.0)
    informal_pct = Column(Float, default=0.0)
    created_at = Column(DateTime, default=_utcnow)


# ── Indicator ──────────────────────────────────────────────────

class Indicator(Base):
    __tablename__ = "geos_indicators"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=True)  # economic, social, governance, environmental
    value = Column(Float, default=0.0)
    target = Column(Float, default=0.0)
    unit = Column(String(50), nullable=True)
    year = Column(Integer, nullable=True)
    province_id = Column(Integer, ForeignKey("geos_provinces.id"), nullable=True)
    source = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=_utcnow)

    @property
    def achievement_pct(self) -> float:
        return round(self.value / self.target * 100, 1) if self.target > 0 else 0.0
