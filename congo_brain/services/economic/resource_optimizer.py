"""Natural Resource Value Optimizer for the DRC.

Optimizes the value chain of DRC natural resources:
    Valeur = Extraction + Transformation + Exportation

Goal: maximize Value Added instead of just Extraction revenue.

Key resources: copper, cobalt, lithium, gold, coltan, oil, timber.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ResourceValueChain:
    """Value chain for a single natural resource."""
    resource: str
    extraction_value: float = 0.0
    transformation_value: float = 0.0
    export_value: float = 0.0
    local_processing_pct: float = 0.0  # % of resource processed locally
    jobs_created: int = 0
    environmental_cost: float = 0.0

    @property
    def total_value(self) -> float:
        return self.extraction_value + self.transformation_value + self.export_value

    @property
    def value_added(self) -> float:
        """Value captured domestically (extraction + transformation)."""
        return self.extraction_value + self.transformation_value

    @property
    def capture_rate(self) -> float:
        """% of total value captured by DRC (vs exported raw)."""
        if self.total_value == 0:
            return 0.0
        return round(self.value_added / self.total_value * 100, 1)

    @property
    def net_value(self) -> float:
        return self.value_added - self.environmental_cost

    def to_dict(self) -> dict:
        return {
            "resource": self.resource,
            "extraction_value": round(self.extraction_value, 2),
            "transformation_value": round(self.transformation_value, 2),
            "export_value": round(self.export_value, 2),
            "total_value": round(self.total_value, 2),
            "value_added": round(self.value_added, 2),
            "capture_rate": self.capture_rate,
            "local_processing_pct": self.local_processing_pct,
            "jobs_created": self.jobs_created,
            "environmental_cost": round(self.environmental_cost, 2),
            "net_value": round(self.net_value, 2),
        }


# DRC Resource baseline data (2025 estimates, in billions USD)
DRC_RESOURCES_BASELINE: list[dict] = [
    {"resource": "Cuivre", "extraction_value": 12.0, "transformation_value": 1.5, "export_value": 8.0,
     "local_processing_pct": 10.0, "jobs_created": 45000, "environmental_cost": 2.0},
    {"resource": "Cobalt", "extraction_value": 6.5, "transformation_value": 0.3, "export_value": 5.0,
     "local_processing_pct": 5.0, "jobs_created": 20000, "environmental_cost": 1.5},
    {"resource": "Or", "extraction_value": 3.0, "transformation_value": 0.2, "export_value": 2.5,
     "local_processing_pct": 8.0, "jobs_created": 15000, "environmental_cost": 0.8},
    {"resource": "Coltan", "extraction_value": 1.5, "transformation_value": 0.1, "export_value": 1.2,
     "local_processing_pct": 3.0, "jobs_created": 8000, "environmental_cost": 0.5},
    {"resource": "Lithium", "extraction_value": 2.0, "transformation_value": 0.05, "export_value": 1.8,
     "local_processing_pct": 2.0, "jobs_created": 5000, "environmental_cost": 0.3},
    {"resource": "Pétrole", "extraction_value": 4.0, "transformation_value": 0.8, "export_value": 3.0,
     "local_processing_pct": 20.0, "jobs_created": 12000, "environmental_cost": 1.0},
    {"resource": "Forêt", "extraction_value": 1.0, "transformation_value": 0.3, "export_value": 0.7,
     "local_processing_pct": 30.0, "jobs_created": 30000, "environmental_cost": 0.5},
]


class ResourceOptimizer:
    """Optimizes natural resource value capture for the DRC.

    Implements:
        max Valeur Ajoutée = Σ (Extraction_i + Transformation_i)
    subject to:
        local_processing constraints
        environmental cost limits
        job creation targets
    """

    def __init__(self) -> None:
        self.resources: dict[str, ResourceValueChain] = {}
        self.target_capture_rate: float = 40.0  # Target: capture 40% of value locally

    def load_baseline(self) -> None:
        """Load DRC baseline resource data."""
        for data in DRC_RESOURCES_BASELINE:
            rc = ResourceValueChain(**data)
            self.resources[rc.resource] = rc

    def add_resource(self, resource: ResourceValueChain) -> None:
        self.resources[resource.resource] = resource

    def set_target_capture_rate(self, rate: float) -> None:
        self.target_capture_rate = rate

    @property
    def total_value(self) -> float:
        return sum(r.total_value for r in self.resources.values())

    @property
    def total_value_added(self) -> float:
        return sum(r.value_added for r in self.resources.values())

    @property
    def total_net_value(self) -> float:
        return sum(r.net_value for r in self.resources.values())

    @property
    def overall_capture_rate(self) -> float:
        if self.total_value == 0:
            return 0.0
        return round(self.total_value_added / self.total_value * 100, 1)

    @property
    def total_jobs(self) -> int:
        return sum(r.jobs_created for r in self.resources.values())

    @property
    def total_environmental_cost(self) -> float:
        return sum(r.environmental_cost for r in self.resources.values())

    @property
    def total_nrv(self) -> float:
        """Total Natural Resource Value — NRV for SNN = CS + PS + GR + NRV - DWL - EC."""
        return self.total_value_added

    def get_optimization_recommendations(self) -> list[dict]:
        """Generate recommendations to maximize value-added."""
        recommendations = []
        for r in self.resources.values():
            if r.capture_rate < self.target_capture_rate:
                gap = self.target_capture_rate - r.capture_rate
                # Estimate additional value if target is met
                potential_additional = r.export_value * (gap / 100)
                recommendations.append({
                    "resource": r.resource,
                    "current_capture_rate": r.capture_rate,
                    "target_capture_rate": self.target_capture_rate,
                    "gap_percentage": round(gap, 1),
                    "potential_additional_value": round(potential_additional, 2),
                    "action": f"Investir dans la transformation locale du {r.resource}",
                })
        recommendations.sort(key=lambda x: x["potential_additional_value"], reverse=True)
        return recommendations

    def get_dashboard(self) -> dict:
        resources = sorted(self.resources.values(), key=lambda x: x.total_value, reverse=True)
        return {
            "model": "ResourceOptimizer",
            "total_value": round(self.total_value, 2),
            "total_value_added": round(self.total_value_added, 2),
            "total_net_value": round(self.total_net_value, 2),
            "overall_capture_rate": self.overall_capture_rate,
            "target_capture_rate": self.target_capture_rate,
            "total_jobs_created": self.total_jobs,
            "total_environmental_cost": round(self.total_environmental_cost, 2),
            "resources": [r.to_dict() for r in resources],
            "recommendations": self.get_optimization_recommendations(),
        }
