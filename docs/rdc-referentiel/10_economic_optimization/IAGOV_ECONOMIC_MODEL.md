# Modèle économique IAGov

Objectif : comparer des politiques publiques selon une fonction de bien-être social explicite,
documentée et testable.

Variables :
- CS : Consumer Surplus ;
- PS : Producer Surplus ;
- TR : recettes publiques ;
- VA : valeur ajoutée ;
- EC : externalités/coûts externes ;
- DWL : perte sèche ;
- C : coût budgétaire ;
- R : risque.

Score initial configurable :
S = w1*CS + w2*PS + w3*TR + w4*VA - w5*EC - w6*DWL - w7*C - w8*R

Les coefficients sont des paramètres de politique publique, pas des constantes universelles.

## Contraintes
Budget, dette, capacité administrative, capacité d'absorption, équité territoriale,
objectifs sectoriels et contraintes réglementaires.

Le moteur économique doit rester séparé du LLM : l'IA prépare/explique les scénarios,
le moteur produit les calculs vérifiables.
