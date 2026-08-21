"""MOEG — Modèle d'Optimisation Économique de la Gouvernance.

Core welfare economics model for the Democratic Republic of the Congo.
Based on the principle that governance is an optimization problem:

    max W = CS + PS + T - DWL

where:
    CS = Consumer Surplus
    PS = Producer Surplus
    T  = Government Revenue (recettes publiques)
    DWL = Deadweight Loss (corruption + inefficiency)
"""

from congo_brain.services.economic.corruption_calculator import CorruptionCalculator
from congo_brain.services.economic.investment_allocator import InvestmentAllocator
from congo_brain.services.economic.nwi import NationalWelfareIndex
from congo_brain.services.economic.resource_optimizer import ResourceOptimizer
from congo_brain.services.economic.welfare_model import WelfareModel

__all__ = [
    "WelfareModel",
    "ResourceOptimizer",
    "InvestmentAllocator",
    "NationalWelfareIndex",
    "CorruptionCalculator",
]
