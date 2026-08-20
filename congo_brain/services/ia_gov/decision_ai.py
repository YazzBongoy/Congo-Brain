"""Module 8: Decision AI — Support décisionnel en langage naturel.

L'utilisateur pose une question:
    "Où investir 500 millions de dollars?"
    "Quel est l'impact d'une baisse de la TVA?"
    "Comment réduire la pauvreté de 10%?"

L'IA répond avec:
    Allocation recommandée, Gains attendus, Justification SNN
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DecisionRecommendation:
    """Recommandation de décision IA."""

    question: str
    allocations: list[dict] = field(default_factory=list)
    expected_impacts: dict = field(default_factory=dict)
    justification: str = ""
    snn_impact: float = 0.0
    confidence: float = 0.0

    def to_dict(self) -> dict:
        return {
            "question": self.question,
            "allocations": self.allocations,
            "expected_impacts": self.expected_impacts,
            "justification": self.justification,
            "snn_impact": round(self.snn_impact, 2),
            "confidence": round(self.confidence, 1),
        }


# Patterns de questions et réponses pré-calculées
DECISION_PATTERNS: list[dict] = [
    {
        "question_pattern": "investir",
        "context": "budget",
        "allocations": [
            {"sector": "Agriculture", "pct": 30, "amount": 150, "reason": "Emplois + sécurité alimentaire + NRV"},
            {"sector": "Énergie", "pct": 25, "amount": 125, "reason": "Effet multiplicateur sur toute l'économie"},
            {"sector": "Infrastructure", "pct": 20, "amount": 100, "reason": "Réduction coûts logistiques"},
            {"sector": "Santé", "pct": 15, "amount": 75, "reason": "Productivité workforce"},
            {"sector": "Éducation", "pct": 10, "amount": 50, "reason": "Capital humain long terme"},
        ],
        "impacts": {"gdp": "+1.2%", "emplois": "+180,000", "pauvreté": "-3.5%", "recettes": "+800M"},
        "justification": "L'agriculture et l'énergie offrent le meilleur ratio CS/PS par dollar investi en RDC.",
        "snn_impact": 8.5,
        "confidence": 78,
    },
    {
        "question_pattern": "réduire la pauvreté",
        "context": "social",
        "allocations": [
            {"sector": "Agriculture", "pct": 35, "amount": 175, "reason": "70% de la population rurale"},
            {"sector": "Éducation", "pct": 25, "amount": 125, "reason": "Sortie du cycle pauvreté"},
            {"sector": "Santé", "pct": 20, "amount": 100, "reason": "Réduction mortalité + productivité"},
            {"sector": "Infrastructure rurale", "pct": 15, "amount": 75, "reason": "Accès marchés"},
            {"sector": "Microfinance", "pct": 5, "amount": 25, "reason": "Autonomisation économique"},
        ],
        "impacts": {"pauvreté": "-8%", "emploi_rural": "+250,000", "revenu_menage": "+40%"},
        "justification": "Cibler la population rurale (70% en pauvreté) via l'agriculture et l'éducation.",
        "snn_impact": 12.0,
        "confidence": 72,
    },
    {
        "question_pattern": "réduire la corruption",
        "context": "gouvernance",
        "allocations": [
            {"sector": "Numérique", "pct": 30, "amount": 150, "reason": "Dématérialisation = transparence"},
            {"sector": "Justice", "pct": 25, "amount": 125, "reason": "Sanctions = dissuasion"},
            {"sector": "Société civile", "pct": 20, "amount": 100, "reason": "Contrôle citoyen"},
            {"sector": "Fonction publique", "pct": 15, "amount": 75, "reason": "Modernisation administration"},
            {"sector": "Audit", "pct": 10, "amount": 50, "reason": "Vérification permanente"},
        ],
        "impacts": {"dwl_reduction": "-30%", "recettes_supplementaires": "+1.5B", "confiance": "+25%"},
        "justification": "La numérisation réduit les contacts corruption et améliore la traçabilité.",
        "snn_impact": 15.0,
        "confidence": 65,
    },
    {
        "question_pattern": "baisse de la TVA",
        "context": "fiscal",
        "allocations": [
            {"sector": "PME formelles", "pct": 40, "amount": 200, "reason": "Formalisation + compétitivité"},
            {"sector": "Consommateurs", "pct": 35, "amount": 175, "reason": "CS += baisse prix"},
            {"sector": "Économie formelle", "pct": 25, "amount": 125, "reason": "Réduction informel"},
        ],
        "impacts": {"cs": "+2B", "formalisation": "+15%", "recettes": "-0.8B à court terme, +1.2B à long terme"},
        "justification": "La TVA élevée pousse vers l'informel. Une baisse formalise l'économie.",
        "snn_impact": 6.0,
        "confidence": 60,
    },
]


class DecisionAI:
    """Support décisionnel en langage naturel.

    Analyse la question de l'utilisateur et retourne
    une recommandation structurée avec allocation et impacts.
    """

    def __init__(self) -> None:
        self.patterns = DECISION_PATTERNS

    def answer(self, question: str, budget: float = 500) -> DecisionRecommendation:
        """Répond à une question de décision."""
        question_lower = question.lower()

        # Trouver le pattern correspondant
        best_match = None
        best_score = 0
        for pattern in self.patterns:
            score = 0
            words = pattern["question_pattern"].split()
            for word in words:
                if word in question_lower:
                    score += 1
            if score > best_score:
                best_score = score
                best_match = pattern

        if best_match is None or best_score == 0:
            return self._default_answer(question, budget)

        # Ajuster les montants au budget
        allocations = []
        for alloc in best_match["allocations"]:
            adjusted = {**alloc}
            adjusted["amount"] = round(budget * alloc["pct"] / 100, 1)
            allocations.append(adjusted)

        return DecisionRecommendation(
            question=question,
            allocations=allocations,
            expected_impacts=best_match["impacts"],
            justification=best_match["justification"],
            snn_impact=best_match["snn_impact"] * budget / 500,
            confidence=best_match["confidence"],
        )

    def _default_answer(self, question: str, budget: float) -> DecisionRecommendation:
        """Réponse par défaut si pas de pattern correspondant."""
        return DecisionRecommendation(
            question=question,
            allocations=[
                {"sector": "Agriculture", "pct": 25, "amount": round(budget * 0.25, 1)},
                {"sector": "Énergie", "pct": 25, "amount": round(budget * 0.25, 1)},
                {"sector": "Santé", "pct": 20, "amount": round(budget * 0.20, 1)},
                {"sector": "Éducation", "pct": 20, "amount": round(budget * 0.20, 1)},
                {"sector": "Infrastructure", "pct": 10, "amount": round(budget * 0.10, 1)},
            ],
            expected_impacts={"gdp": "+0.8%", "emplois": "+100,000"},
            justification="Allocation diversifiée équilibrant court et long terme.",
            snn_impact=5.0 * budget / 500,
            confidence=50,
        )

    def get_available_topics(self) -> list[str]:
        return [
            "Où investir [montant] millions de dollars?",
            "Comment réduire la pauvreté?",
            "Comment réduire la corruption?",
            "Quel est l'impact d'une baisse de la TVA?",
        ]

    def get_dashboard(self) -> dict:
        return {
            "model": "DecisionAI",
            "description": "Support décisionnel en langage naturel basé sur le SNN",
            "available_topics": self.get_available_topics(),
            "pattern_count": len(self.patterns),
        }
