# Référentiel provincial RDC — 26 provinces (2026)

Statuts : OBSERVED (découpage administratif et superficies), ESTIMATE
(indicateurs socio-économiques embarqués), SYNTHETIC (scores et indicateurs
dérivés du jumeau numérique). Conformément à la règle de provenance du dossier,
toute donnée conserve source, période de référence, unité, statut et date
d'ingestion. Date d'ingestion : 2026-08-24.
Implémentation : `congo_brain/data/provinces.py::PROVINCES_DRC`.

## Cadre juridique

- **Constitution de la RDC du 18 février 2006, article 2** : la République
  Démocratique du Congo est composée de 26 provinces (la ville-province de
  Kinshasa et 25 provinces).
- **Mise en œuvre effective : 2015**, à la suite des lois de découpage
  territorial de 2015, qui ont éclaté les 11 provinces historiques issues du
  découpage de 1988.
- Les 11 provinces historiques (période 1988-2015) restent pertinentes pour
  les séries statistiques antérieures à 2015 : leur rattachement est assuré par
  `HISTORICAL_PROVINCE_MAPPING` (`congo_brain/data/provinces.py`).

## Les 26 provinces officielles (découpage 2015)

Le numéro suit l'ordre administratif officiel tel qu'implémenté dans
`PROVINCES_DRC`. Données reprises fidèlement de `congo_brain/data/provinces.py`.

| N° | Province | Chef-lieu | Province historique d'origine |
|---|---|---|---|
| 1 | Kinshasa | Kinshasa | Kinshasa |
| 2 | Kongo Central | Matadi | Bas-Congo |
| 3 | Kwango | Kenge | Bandundu |
| 4 | Kwilu | Bandundu | Bandundu |
| 5 | Mai-Ndombe | Inongo | Bandundu |
| 6 | Kasaï | Tshikapa | Kasaï-Occidental |
| 7 | Kasaï-Central | Kananga | Kasaï-Occidental |
| 8 | Kasaï-Oriental | Mbuji-Mayi | Kasaï-Oriental |
| 9 | Lomami | Kabinda | Kasaï-Oriental |
| 10 | Sankuru | Lusambo | Kasaï-Oriental |
| 11 | Maniema | Kindu | Maniema |
| 12 | Nord-Kivu | Goma | Nord-Kivu |
| 13 | Sud-Kivu | Bukavu | Sud-Kivu |
| 14 | Ituri | Bunia | Orientale |
| 15 | Haut-Uélé | Isiro | Orientale |
| 16 | Bas-Uélé | Buta | Orientale |
| 17 | Mongala | Lisala | Équateur |
| 18 | Nord-Ubangi | Gbadolite | Équateur |
| 19 | Sud-Ubangi | Gemena | Équateur |
| 20 | Tshuapa | Boende | Équateur |
| 21 | Tshopo | Kisangani | Orientale |
| 22 | Équateur | Mbandaka | Équateur |
| 23 | Haut-Katanga | Lubumbashi | Katanga |
| 24 | Haut-Lomami | Kamina | Katanga |
| 25 | Lualaba | Kolwezi | Katanga |
| 26 | Tanganyika | Kalemie | Katanga |

## Mapping inverse : 11 provinces historiques vers les nouvelles provinces

Pour agréger les séries statistiques antérieures à 2015
(`HISTORICAL_PROVINCE_MAPPING`) :

| Province historique (1988-2015) | Provinces actuelles (depuis 2015) |
|---|---|
| Kinshasa | Kinshasa |
| Bas-Congo | Kongo Central |
| Bandundu | Kwango, Kwilu, Mai-Ndombe |
| Équateur | Mongala, Nord-Ubangi, Sud-Ubangi, Tshuapa, Équateur |
| Kasaï-Occidental | Kasaï, Kasaï-Central |
| Kasaï-Oriental | Kasaï-Oriental, Lomami, Sankuru |
| Katanga | Haut-Katanga, Haut-Lomami, Lualaba, Tanganyika |
| Maniema | Maniema |
| Nord-Kivu | Nord-Kivu |
| Orientale | Ituri, Haut-Uélé, Bas-Uélé, Tshopo |
| Sud-Kivu | Sud-Kivu |

## Avertissement — indicateurs socio-économiques

Les indicateurs socio-économiques embarqués dans `PROVINCES_DRC` (population,
PIB provincial, taux de pauvreté, accès à l'eau, à l'électricité et à
l'internet, taux d'alphabétisation, indice de sécurité, etc.) sont des
**estimations de démonstration 2024-2026**. Ils servent exclusivement au
développement et aux tests du moteur SNN. Ils ne constituent pas des données
officielles et doivent être remplacés, avant tout usage analytique sérieux ou
toute publication, par les données officielles de l'INS RDC et de la Banque
Mondiale (source, document, URL, date de publication, période de référence,
unité et statut conservés conformément à la règle de provenance du dossier).

### Statut par indicateur

| Indicateur | Unité | Statut | Sources visées |
|---|---|---|---|
| population | millions d'habitants | ESTIMATE | INS RDC (projections), Banque Mondiale — 2024-2026 |
| gdp | M USD/an | ESTIMATE | Banque Mondiale, FMI — répartitions provinciales approximées |
| poverty_rate | % | ESTIMATE | INS RDC, enquêtes ménages |
| electricity_access / water_access / internet_access / literacy_rate | % | ESTIMATE | Banque Mondiale, UNICEF |
| area_km2 | km² | OBSERVED | découpage officiel 2015 |
| security_index / governance_score | 0-100 | SYNTHETIC | scores de travail Congo-Brain |
| budget, roads_km, health_facilities, schools, enterprises, agricultural_output, mining_output, life_expectancy | divers | SYNTHETIC | dérivés déterministes (`_twin_fields`) pour le jumeau numérique |

## Règles d'usage

1. Toute province ajoutée au moteur SNN doit figurer dans `PROVINCES_DRC`.
2. Ne jamais coder une liste provinciale en dur dans un service : importer
   depuis `congo_brain/data/provinces.py` (`BASELINE_PROVINCES`,
   `TWIN_PROVINCES`).
3. Les agrégations historiques utilisent `HISTORICAL_PROVINCE_MAPPING`, pas
   des noms saisis manuellement.

## Sources

- Ministère de l'Intérieur RDC — https://interieur.gouv.cd (référentiel des
  territoires et provinces)
- Constitution de la RDC du 18 février 2006, article 2
- Lois de découpage territorial de 2015
- INS RDC (Institut National de la Statistique) — projections démographiques
  et enquêtes auprès des ménages
- Banque Mondiale — indicateurs socio-économiques RDC
