# Moteur Économique — GEOS

## SNNOptimizationEngine
Le cœur du système: calcule le SNN agrégé à partir de 14 entités.

### Entités (14 tables SQLAlchemy)
1. **Province** — 8 provinces avec population, area, literacy rate
2. **Citizen** — Citoyens avec province, statut, satisfaction
3. **Company** — 8 entreprises avec revenue, costs, corruption
4. **Ministry** — 8 ministères avec budget, performance
5. **Budget** — Allocations budgétaires par ministère
6. **Resource** — 8 ressources (Cu, Co, Or, Li) avec production et NRV
7. **Tax** — 6 types d'impôts avec base, rate, compliance
8. **Project** — 8 projets d'investissement publics
9. **Infrastructure** — 8 infrastructures avec coût et statut
10. **PublicService** — 8 services avec WTP, satisfaction, CS
11. **Contract** — 6 contrats gouvernementaux
12. **Payment** — Paiements avec anomalie score
13. **Market** — 5 marchés avec prix, demande, offre
14. **Indicator** — 8 indicateurs macro (croissance, inflation, chômage)

### 8 Modules IA GOV
| Module | Fichier | Rôle |
|--------|---------|------|
| 1. Resource Optimizer | resource_optimizer.py | Optimisation LP SNN |
| 2. Consumer Surplus | consumer_surplus.py | Calcul CS par service |
| 3. Producer Surplus | producer_surplus.py | Calcul PS par entreprise |
| 4. National Resource | national_resource.py | Suivi mines, production |
| 5. Governance Score | governance_score.py | Score par ministère |
| 6. Corruption Detector | corruption_detector.py | Détection anomalies |
| 7. Digital Twin | digital_twin.py | Simulation provinces |
| 8. Decision AI | decision_ai.py | NLP, recommandations |

### Données Réelles RDC (enrichies)
- **8 provinces**: Kinshasa (17M hab), Haut-Katanga (4.5M), Kongo Central (5.9M), Nord-Kivu (8.1M), Sud-Kivu (7.6M), Kasaï (5.3M), Équateur (3.1M), Tshopo (3.4M)
- **8 entreprises**: Gécamines, SNEL, Vodacom, Orange, TotalEnergies, Congo Airlines, Bralima, Brasseries
- **8 mines**: Kamoa-Kakula (Cu), Tenke Fungurume (Cu/Co), Kibali Gold (Or), Mutanda (Co), AVZ Manono (Li), Sicomines (Cu), Banro (Or)
- Sources: Banque Mondiale, PNUD, UNESCO, Transparency International
