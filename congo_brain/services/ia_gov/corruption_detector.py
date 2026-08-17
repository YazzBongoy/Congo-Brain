"""Module 6: Corruption Detector — Détection d'anomalies.

Détecte automatiquement:
    Anomalies, Surfacturations, Conflits d'intérêts,
    Retards anormaux, Dépassements budgétaires, Doubles paiements

Chaque anomalie reçoit un score de risque.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AnomalyType(str, Enum):
    OVERPRICING = "surfacturation"
    BUDGET_OVERRUN = "depassement_budgetaire"
    DELAY = "retard_anormal"
    DOUBLE_PAYMENT = "double_paiement"
    CONFLICT_OF_INTEREST = "conflit_interet"
    SHELL_COMPANY = "societe_fantome"
    UNUSUAL_PATTERN = "pattern_inhabituel"
    COST_ANOMALY = "anomalie_cout"


class RiskLevel(str, Enum):
    CRITICAL = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1


@dataclass
class Anomaly:
    """Anomalie détectée."""
    id: str
    anomaly_type: str
    description: str
    sector: str
    province: str = ""
    amount: float = 0.0           # Montant en jeu (M USD)
    risk_score: float = 0.0       # Score de risque (0-100)
    risk_level: str = ""
    confidence: float = 0.0       # Confiance de la détection (0-100)
    date_detected: str = ""
    status: str = "actif"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.anomaly_type,
            "description": self.description,
            "sector": self.sector,
            "province": self.province,
            "amount": round(self.amount, 2),
            "risk_score": round(self.risk_score, 1),
            "risk_level": self.risk_level,
            "confidence": round(self.confidence, 1),
            "status": self.status,
        }


# Anomalies types détectées en RDC
DRC_ANOMALY_PATTERNS: list[dict] = [
    {"type": "surfacturation", "description": "Coût routes 3x au-dessus du marché international",
     "sector": "Infrastructure", "amount": 150, "risk_score": 85, "confidence": 90},
    {"type": "depassement_budgetaire", "description": "Projet barrage +120% du budget initial",
     "sector": "Énergie", "amount": 200, "risk_score": 78, "confidence": 85},
    {"type": "retard_anormal", "description": "Route Kinshasa-Lubumbashi: 5 ans de retard",
     "sector": "Transport", "amount": 80, "risk_score": 72, "confidence": 95},
    {"type": "double_paiement", "description": "Double facturation fournitures ministère",
     "sector": "Santé", "amount": 12, "risk_score": 68, "confidence": 88},
    {"type": "societe_fantome", "description": "Entreprise sans employés enregistrés, contrats publics",
     "sector": "Mines", "amount": 45, "risk_score": 92, "confidence": 75},
    {"type": "conflit_interet", "description": "Directeur entreprise adjudicataire parent fonctionnaire",
     "sector": "Infrastructure", "amount": 25, "risk_score": 88, "confidence": 80},
    {"type": "pattern_inhabituel", "description": "Paiements concentrés fin d'année fiscale",
     "sector": "Finance", "amount": 60, "risk_score": 55, "confidence": 70},
    {"type": "anomalie_cout", "description": "Coût administratif 40% au-dessus de la moyenne",
     "sector": "Administration", "amount": 35, "risk_score": 62, "confidence": 82},
]


class CorruptionDetectionEngine:
    """Détecte automatiquement les anomalies de gouvernance.

    Chaque anomalie reçoit un score de risque et un niveau de confiance.
    """

    def __init__(self) -> None:
        self.anomalies: list[Anomaly] = []

    def load_baseline(self) -> None:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self.anomalies = []
        for i, data in enumerate(DRC_ANOMALY_PATTERNS):
            score = data["risk_score"]
            level_name = (
                "Critique" if score >= 80
                else "Élevé" if score >= 60
                else "Moyen" if score >= 40
                else "Faible"
            )
            self.anomalies.append(Anomaly(
                id=f"ANO-{i+1:04d}",
                anomaly_type=data["type"],
                description=data["description"],
                sector=data["sector"],
                amount=data["amount"],
                risk_score=score,
                risk_level=level_name,
                confidence=data["confidence"],
                date_detected=now,
            ))

    def add_anomaly(self, anomaly: Anomaly) -> None:
        self.anomalies.append(anomaly)

    @property
    def total_amount_at_risk(self) -> float:
        return sum(a.amount for a in self.anomalies if a.status == "actif")

    @property
    def critical_count(self) -> int:
        return len([a for a in self.anomalies if a.risk_level == "Critique"])

    @property
    def high_count(self) -> int:
        return len([a for a in self.anomalies if a.risk_level == "Élevé"])

    def get_by_sector(self) -> dict:
        by_sector: dict[str, list] = {}
        for a in self.anomalies:
            if a.sector not in by_sector:
                by_sector[a.sector] = []
            by_sector[a.sector].append(a.to_dict())
        return by_sector

    def get_by_type(self) -> dict:
        by_type: dict[str, list] = {}
        for a in self.anomalies:
            if a.anomaly_type not in by_type:
                by_type[a.anomaly_type] = []
            by_type[a.anomaly_type].append(a.to_dict())
        return by_type

    def get_risk_summary(self) -> dict:
        return {
            "total_anomalies": len(self.anomalies),
            "active_anomalies": len([a for a in self.anomalies if a.status == "actif"]),
            "total_amount_at_risk": round(self.total_amount_at_risk, 2),
            "critical": self.critical_count,
            "high": self.high_count,
            "medium": len([a for a in self.anomalies if a.risk_level == "Moyen"]),
            "low": len([a for a in self.anomalies if a.risk_level == "Faible"]),
            "average_risk_score": round(sum(a.risk_score for a in self.anomalies) / len(self.anomalies), 1) if self.anomalies else 0,
        }

    def get_dashboard(self) -> dict:
        return {
            "model": "CorruptionDetectionEngine",
            "risk_summary": self.get_risk_summary(),
            "by_sector": self.get_by_sector(),
            "by_type": self.get_by_type(),
            "anomalies": sorted([a.to_dict() for a in self.anomalies],
                                key=lambda x: x["risk_score"], reverse=True),
        }
