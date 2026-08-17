# Moteur IA — GEOS

## Prédiction (PredictiveModel)
Module `predictor.py` — projections SNN sur 5-10 ans.

### Scénarios Prédéfinis (7)
1. **Baseline** — statu quo, tendance actuelle (+2%/an)
2. **Investissement minier** — usines de transformation, +30% production
3. **Réforme fiscale** — élargissement assiette, TSCA
4. **Anti-corruption** — transparence, e-procurement
5. **Transition verte** — énergies renouvelables, tourisme
6. **Optimiste** — toutes réformes combinées
7. **Pessimiste** — instabilité, chute cours matières premières

### Méthode
- Projection déterministe: croissance annuelle composée
- Monte Carlo (100 runs): simulation stochastique avec volatilité
- Intervalles de confiance 5%-95%
- Ranking des scénarios par SNN final

## Détection d'Anomalies (CorruptionDetector)
Module `corruption_detector.py` — scoring transactions.

### Méthodes
- Détection mots-clés (corruption, détournement, etc.)
- Dépassement budget (threshold configurable)
- Ratio budget/actual
- Score 0-1, tri par score décroissant

## Jumeau Numérique (NationalDigitalTwin)
Module `digital_twin.py` — simulation par province.

### Fonctionnalités
- Investissement par province avec multiplicateur
- Taux de retour estimé
- Impact population, PIB/hab, IDH
- Comparaison inter-provinces

## IA Décisionnelle (DecisionAI)
Module `decision_ai.py` — NLP pour décideurs.

### Commandes
- "investir" → recommandations investissement
- "pauvreté" → stratégie lutte pauvreté
- "corruption" → plan anti-corruption
- "tva" → analyse réforme TVA
- Réponses contextualisées avec données réelles

## Score de Gouvernance (GovernanceScore)
Module `governance_score.py` — évaluation ministères.

### Dimensions (4)
- Budget: efficacité dépenses
- Performance: objectifs atteints
- Corruption: niveau de confiance
- Satisfaction: feedback citoyens
- Score composite 0-100, rating: Critique → Excellent
