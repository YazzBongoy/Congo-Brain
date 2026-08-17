# Modèle Mathématique — GEOS

## Formule du Surplus National Net (SNN)

```
SNN = CS + PS + GR + NRV - DWL - EC
```

## Composants Détaillés

### CS — Consumer Surplus (Surplus des Consommateurs)
```
CS = Σ sectors (Qd × (WTP - P_actual))
```
- Qd = Quantité demandée
- WTP = Willingness To Pay (prix maximum accepté)
- P_actual = Prix actuel du service/bien
- **Interprétation**: bien-être des citoyens consommateurs

### PS — Producer Surplus (Surplus des Producteurs)
```
PS = Revenue - Production_Cost - Tax_Burden - Admin_Cost - Corruption_Cost - Logistics_Cost - Energy_Cost
```
- **Interprétation**: marge nette des entreprises nationales

### GR — Government Revenue (Recettes Gouvernementales)
```
GR = Σ taxes (base × rate × compliance)
```
- Types: IS, TVA, Douanes, Minières, Foncier, IRPP
- Compliance = taux de conformité fiscale

### NRV — Net Resource Value (Valeur Nette des Ressources)
```
NRV = Σ resources (Production × Market_Price × (1 + Local_Processing_Pct) × Tax_Rate)
```
- Intègre la transformation locale (added value)
- **Interprétation**: richesse réelle extraite et transformée

### DWL — Deadweight Loss (Perte Sèche)
```
DWL = Σ factors (Direct_Loss + Budget_Variance + Compliance_Cost + Time_Cost + Corruption_Premium + Opportunity_Cost)
```
- Pénalise corruption, bureaucratie, inefficacité

### EC — Environmental Cost (Coûts Environnementaux)
```
EC = Σ impacts (Pollution + CO2 + Deforestation + Water_Impact + Mitigation + Remediation)
```
- Pénalise dégradation environnementale

## Indice de Bien-être National (NWI)
```
NWI = 0.25×CS + 0.25×PS + 0.15×GR + 0.15×NRV + 0.10×Sustainability - 0.05×DWL% - 0.05×EC%
```
- Score 0-100, rating: Critique / Faible / Moyen / Bon / Excellent

## Optimisation LP
```
max  Σ w_i × x_i
s.t. Σ x_i ≤ Budget
     x_i ≥ 0  ∀i
```
- Objectif: maximiser SNN sous contrainte budgétaire
- Solver: scipy.optimize.linprog (greedy fallback)
