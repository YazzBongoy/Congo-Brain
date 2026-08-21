"""IA GOV — Intelligence Artificielle pour la Gouvernance.

Architecture en 8 modules:
    1. Resource Optimization Engine  — Cerveau: max SNN sous contraintes
    2. Consumer Surplus Engine       — Estimation CS par service public
    3. Producer Surplus Engine       — Estimation PS pour entreprises
    4. National Resource Engine      — Suivi détaillé mines/ressources
    5. Governance Score              — Note par ministère
    6. Corruption Detector           — Détection d'anomalies
    7. National Digital Twin         — Jumeau numérique de la RDC
    8. Decision AI                   — Support décisionnel en langage naturel

Pipeline: Collecte → Intelligence → Optimisation → Décision
"""

from congo_brain.services.ia_gov.collectors import DataCollector
from congo_brain.services.ia_gov.consumer_surplus import ConsumerSurplusEngine
from congo_brain.services.ia_gov.corruption_detector import CorruptionDetectionEngine
from congo_brain.services.ia_gov.decision_ai import DecisionAI
from congo_brain.services.ia_gov.digital_twin import NationalDigitalTwin
from congo_brain.services.ia_gov.governance_score import GovernanceScoreEngine
from congo_brain.services.ia_gov.national_resource import NationalResourceEngine
from congo_brain.services.ia_gov.producer_surplus import ProducerSurplusEngine
from congo_brain.services.ia_gov.resource_optimizer import ResourceOptimizationEngine

__all__ = [
    "DataCollector",
    "ResourceOptimizationEngine",
    "ConsumerSurplusEngine",
    "ProducerSurplusEngine",
    "NationalResourceEngine",
    "GovernanceScoreEngine",
    "CorruptionDetectionEngine",
    "NationalDigitalTwin",
    "DecisionAI",
]
