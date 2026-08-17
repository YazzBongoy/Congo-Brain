"""IA GOV — Intelligence Artificielle pour la Gouvernance.

Architecture:
    Collecte des données → Intelligence Artificielle → Moteur d'Optimisation
         → (CS, PS, GR) → Tableau de bord → Décision gouvernementale
"""

from congo_brain.services.ia_gov.collectors import DataCollector, BudgetData, EconomicData, SocialData
from congo_brain.services.ia_gov.intelligence import IntelligenceEngine, AnalysisResult
from congo_brain.services.ia_gov.optimizer import GovOptimizer, OptimizationResult
from congo_brain.services.ia_gov.dashboard import GovDashboard

__all__ = [
    "DataCollector", "BudgetData", "EconomicData", "SocialData",
    "IntelligenceEngine", "AnalysisResult",
    "GovOptimizer", "OptimizationResult",
    "GovDashboard",
]
