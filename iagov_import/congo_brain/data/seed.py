"""Seed data -- real 2025 DRC governance data (Loi de Finances 2025).

Sources:
- Loi de Finances exercice 2025 (budget.gouv.cd)
- Loi de Finances rectificative 2025 (50 691,8 Mds CDF)
- Ministere des Finances / BCC notes de conjoncture
- OCHA situation reports (Nord-Kivu, Sud-Kivu)
- Ministere des Affaires Etrangeres (passeport.gouv.cd)
- CONADEP (permis de conduire biometrique)
- ONIP (carte d'identite nationale)
"""

from __future__ import annotations

import json
from datetime import date

from sqlalchemy.orm import Session

from congo_brain.core.security import hash_password
from congo_brain.models.budget import Budget, Transaction
from congo_brain.models.citizen import (
    FAQ,
    CitizenRight,
    Contact,
    Procedure,
)
from congo_brain.models.investment import Investment
from congo_brain.models.security_alert import SecurityAlert
from congo_brain.models.transparency import TransparencyReport
from congo_brain.models.user import User


def seed_all(db: Session) -> None:
    """Insert seed data into all tables."""
    _seed_users(db)
    _seed_budgets(db)
    _seed_investments(db)
    _seed_security_alerts(db)
    _seed_transparency_reports(db)
    _seed_citizen_data(db)
    db.commit()


def _seed_users(db: Session) -> None:
    if db.query(User).count() > 0:
        return
    users = [
        User(
            username="admin",
            email="admin@congobrain.cd",
            password_hash=hash_password("admin123"),
            role="admin",
            ministry="Presidence de la Republique",
        ),
        User(
            username="analyste_budget",
            email="budget@congobrain.cd",
            password_hash=hash_password("budget123"),
            role="analyst",
            ministry="Ministere du Budget",
        ),
        User(
            username="analyste_finances",
            email="finances@congobrain.cd",
            password_hash=hash_password("finances123"),
            role="analyst",
            ministry="Ministere des Finances",
        ),
        User(
            username="analyste_invest",
            email="invest@congobrain.cd",
            password_hash=hash_password("invest123"),
            role="analyst",
            ministry="Ministere du Plan",
        ),
        User(
            username="analyste_dgi",
            email="dgi@congobrain.cd",
            password_hash=hash_password("dgi123"),
            role="analyst",
            ministry="Direction Generale des Impots",
        ),
        User(
            username="analyste_dgda",
            email="dgda@congobrain.cd",
            password_hash=hash_password("dgda123"),
            role="analyst",
            ministry="Direction Generale des Douanes et Accises",
        ),
        User(
            username="citoyen",
            email="citoyen@congobrain.cd",
            password_hash=hash_password("citoyen123"),
            role="viewer",
        ),
    ]
    db.add_all(users)
    db.flush()


# ------------------------------------------------------------------
# BudgetGuard -- Real 2025 Loi de Finances data
# Budget total initial: 51 553,5 Mds CDF (~17,5 Mds USD)
# Budget rectificatif: 50 691,8 Mds CDF (~17,2 Mds USD)
# Taux de change moyen: 2 859,2 CDF/USD
# ------------------------------------------------------------------
def _seed_budgets(db: Session) -> None:
    if db.query(Budget).count() > 0:
        return

    budgets = [
        # -- Revenue agencies (regies financieres) --
        Budget(
            ministry="DGI - Direction Generale des Impots",
            sector="Recettes Fiscales",
            allocated_amount=16_407_600_000_000,
            spent_amount=15_550_200_000_000,
            fiscal_year=2025,
        ),
        Budget(
            ministry="DGDA - Direction Generale des Douanes et Accises",
            sector="Recettes Douanieres",
            allocated_amount=7_769_100_000_000,
            spent_amount=6_247_100_000_000,
            fiscal_year=2025,
        ),
        Budget(
            ministry="DGRAD - Recettes Administratives",
            sector="Recettes Non Fiscales",
            allocated_amount=5_357_268_000_000,
            spent_amount=3_824_500_000_000,
            fiscal_year=2025,
        ),
        Budget(
            ministry="OGEFREM - Office de Gestion du Fret Multimodal",
            sector="Recettes Parafiscales",
            allocated_amount=185_000_000_000,
            spent_amount=98_500_000_000,
            fiscal_year=2025,
        ),
        # -- Expenditure ministries --
        Budget(
            ministry="Presidence de la Republique",
            sector="Fonctionnement Institutions",
            allocated_amount=998_500_000_000,
            spent_amount=1_050_000_000_000,
            fiscal_year=2025,
        ),
        Budget(
            ministry="Primature",
            sector="Coordination Gouvernementale",
            allocated_amount=1_545_000_000_000,
            spent_amount=1_310_000_000_000,
            fiscal_year=2025,
        ),
        Budget(
            ministry="Ministere de la Defense Nationale",
            sector="Defense et Securite",
            allocated_amount=12_890_000_000_000,
            spent_amount=13_200_000_000_000,
            fiscal_year=2025,
        ),
        Budget(
            ministry="Ministere des Finances",
            sector="Administration Financiere",
            allocated_amount=4_124_000_000_000,
            spent_amount=3_850_000_000_000,
            fiscal_year=2025,
        ),
        Budget(
            ministry="Ministere du Budget",
            sector="Gestion Budgetaire",
            allocated_amount=889_500_000_000,
            spent_amount=820_000_000_000,
            fiscal_year=2025,
        ),
        Budget(
            ministry="Ministere de la Sante Publique",
            sector="Couverture Sante Universelle",
            allocated_amount=3_093_000_000_000,
            spent_amount=2_650_000_000_000,
            fiscal_year=2025,
        ),
        Budget(
            ministry="Ministere de l'EPST",
            sector="Gratuite de l'Enseignement",
            allocated_amount=5_155_000_000_000,
            spent_amount=4_800_000_000_000,
            fiscal_year=2025,
        ),
        Budget(
            ministry="Ministere des Infrastructures et Travaux Publics",
            sector="Routes et Ouvrages",
            allocated_amount=4_640_000_000_000,
            spent_amount=3_100_000_000_000,
            fiscal_year=2025,
        ),
        Budget(
            ministry="Ministere de l'Agriculture, Peche et Elevage",
            sector="Securite Alimentaire",
            allocated_amount=3_824_000_000_000,
            spent_amount=2_900_000_000_000,
            fiscal_year=2025,
        ),
        Budget(
            ministry="Ministere des Mines",
            sector="Gouvernance Miniere",
            allocated_amount=2_578_000_000_000,
            spent_amount=2_100_000_000_000,
            fiscal_year=2025,
        ),
        Budget(
            ministry="Ministere de l'Interieur et Securite",
            sector="Administration Territoriale",
            allocated_amount=3_093_000_000_000,
            spent_amount=2_800_000_000_000,
            fiscal_year=2025,
        ),
        Budget(
            ministry=("Ministere du Plan et Suivi de la Revolution de la Modernite"),
            sector="PDL-145 Territoires",
            allocated_amount=2_200_000_000_000,
            spent_amount=1_600_000_000_000,
            fiscal_year=2025,
        ),
    ]
    db.add_all(budgets)
    db.flush()

    transactions = [
        # DGI revenue transactions
        Transaction(
            budget_id=1,
            amount=8_692_900_000_000,
            description="Impots secteur minier (IBP, redevances minieres)",
            transaction_type="recette",
            beneficiary="Tresor Public",
            reference_number="DGI-2025-001",
        ),
        Transaction(
            budget_id=1,
            amount=268_900_000_000,
            description="Impots secteur petrolier (redevances et IBP)",
            transaction_type="recette",
            beneficiary="Tresor Public",
            reference_number="DGI-2025-002",
        ),
        Transaction(
            budget_id=1,
            amount=6_588_400_000_000,
            description=("Autres impots directs et indirects (TVA, IBP hors mines)"),
            transaction_type="recette",
            beneficiary="Tresor Public",
            reference_number="DGI-2025-003",
        ),
        # DGDA revenue transactions
        Transaction(
            budget_id=2,
            amount=634_500_000_000,
            description=("Droits de douane et accises - Aout 2025 (105% des previsions)"),
            transaction_type="recette",
            beneficiary="Tresor Public",
            reference_number="DGDA-2025-AUG",
        ),
        Transaction(
            budget_id=2,
            amount=621_600_000_000,
            description="Fiscalite douaniere - Juillet 2025",
            transaction_type="recette",
            beneficiary="Tresor Public",
            reference_number="DGDA-2025-JUL",
        ),
        # DGRAD revenue transactions
        Transaction(
            budget_id=3,
            amount=350_200_000_000,
            description=("Recettes administratives, judiciaires et domaniales - Aout 2025 (88% des previsions)"),
            transaction_type="recette",
            beneficiary="Tresor Public",
            reference_number="DGRAD-2025-AUG",
        ),
        Transaction(
            budget_id=3,
            amount=435_700_000_000,
            description=("Parafiscalite incluant redevances et droits - Juillet 2025"),
            transaction_type="recette",
            beneficiary="Tresor Public",
            reference_number="DGRAD-2025-JUL",
        ),
        # OGEFREM
        Transaction(
            budget_id=4,
            amount=86_500_000_000,
            description=("Pertes de recettes OGEFREM - installations Est RDC sous occupation M23/AFC"),
            transaction_type="depense",
            beneficiary="Manque a gagner",
            reference_number="OGEFREM-2025-LOSS",
        ),
        # Presidency spending
        Transaction(
            budget_id=5,
            amount=1_050_000_000_000,
            description="Fonctionnement Presidence (+40% par rapport a 2024)",
            transaction_type="depense",
            beneficiary="Cabinet du President",
            reference_number="PRES-2025-FONC",
        ),
        # Defense spending
        Transaction(
            budget_id=7,
            amount=2_288_000_000_000,
            description="Doublement solde militaires et policiers (~800M USD)",
            transaction_type="depense",
            beneficiary="FARDC / Police Nationale",
            reference_number="DEF-2025-SOLDE",
        ),
        Transaction(
            budget_id=7,
            amount=943_140_000_000,
            description=("Depenses urgentes securite Q4 2025 (93% du total urgences)"),
            transaction_type="depense",
            beneficiary="Operations militaires Est",
            reference_number="DEF-2025-URG-Q4",
        ),
        Transaction(
            budget_id=7,
            amount=1_696_950_000_000,
            description=("Depenses urgentes securite Q2 2025 (pic 20,97% des depenses totales)"),
            transaction_type="depense",
            beneficiary="Operations militaires Est",
            reference_number="DEF-2025-URG-Q2",
        ),
        # Health spending
        Transaction(
            budget_id=10,
            amount=850_000_000_000,
            description="Programme Couverture Sante Universelle (CSU)",
            transaction_type="depense",
            beneficiary="Ministere de la Sante",
            reference_number="SANTE-2025-CSU",
        ),
        # Education spending
        Transaction(
            budget_id=11,
            amount=3_200_000_000_000,
            description="Programme Gratuite de l'Enseignement de Base",
            transaction_type="depense",
            beneficiary="Ecoles publiques nationales",
            reference_number="EDUC-2025-GRAT",
        ),
        # Infrastructure spending
        Transaction(
            budget_id=12,
            amount=1_200_000_000_000,
            description="Construction RN2 Mbujimayi-Bukavu",
            transaction_type="depense",
            beneficiary="Consortium BTP",
            reference_number="INFRA-2025-RN2",
        ),
        Transaction(
            budget_id=12,
            amount=800_000_000_000,
            description="Modernisation aeroports (Ndjili, Luano, Bangoka)",
            transaction_type="depense",
            beneficiary="Regie des Voies Aeriennes",
            reference_number="INFRA-2025-AERO",
        ),
        # Agriculture spending
        Transaction(
            budget_id=13,
            amount=1_500_000_000_000,
            description=("Programme securite alimentaire et developpement rural"),
            transaction_type="depense",
            beneficiary="Services agricoles",
            reference_number="AGRI-2025-SEC",
        ),
        # Mines revenue losses
        Transaction(
            budget_id=14,
            amount=926_000_000_000,
            description=("Pertes de recettes minieres Nord-Kivu et Sud-Kivu sous occupation"),
            transaction_type="depense",
            beneficiary="Manque a gagner",
            reference_number="MINES-2025-LOSS",
        ),
        # Suspect transaction for anomaly detection
        Transaction(
            budget_id=8,
            amount=500_000_000_000,
            description=("Paiement frais secrets de recherche Q1 2025 (montant anormalement eleve)"),
            transaction_type="depense",
            beneficiary="Services de renseignement",
            reference_number="FIN-2025-SUSPECT",
        ),
    ]
    db.add_all(transactions)
    db.flush()


# ------------------------------------------------------------------
# InvestSmart -- Real 2025 DRC investment projects
# ANAPI: 96 projets approuves, 5,13 Mds USD (+125,7%)
# Banque mondiale: 2 Mds USD (5 projets strategiques)
# ------------------------------------------------------------------
def _seed_investments(db: Session) -> None:
    if db.query(Investment).count() > 0:
        return
    investments = [
        Investment(
            project_name="Programme Inga 3 - Banque Mondiale",
            sector="Energie",
            province="Kongo Central",
            description=(
                "Phase 1 du programme de developpement Inga 3. "
                "Credit IDA de 250M USD approuve le 3 juin 2025 "
                "sur enveloppe totale de 1 Md USD. Objectif: "
                "11 000 MW, accroitre acces electrique de 21% "
                "a 62% d'ici 2030 (Mission 300)"
            ),
            total_budget=2_859_200_000_000,
            spent_amount=714_800_000_000,
            start_date=date(2025, 6, 3),
            expected_end_date=date(2032, 12, 31),
            status="in_progress",
            roi_score=92.0,
            efficiency_score=75.0,
            social_impact_score=98.0,
        ),
        Investment(
            project_name="Corridor de Lobito",
            sector="Transport Ferroviaire",
            province="Haut-Katanga",
            description=(
                "Corridor ferroviaire transcontinental reliant "
                "le port de Lobito (Angola) au Copperbelt via le "
                "segment RDC Kolwezi-Dilolo. Premier lien "
                "ferroviaire transcontinental ouvert en Afrique"
            ),
            total_budget=4_288_800_000_000,
            spent_amount=1_500_000_000_000,
            start_date=date(2024, 12, 4),
            expected_end_date=date(2030, 12, 31),
            status="in_progress",
            roi_score=88.0,
            efficiency_score=72.0,
            social_impact_score=90.0,
        ),
        Investment(
            project_name="Port en Eau Profonde de Banana",
            sector="Transport Maritime",
            province="Kongo Central",
            description=(
                "Construction du port en eau profonde de Banana. "
                "Projet prioritaire du programme d'action "
                "gouvernemental 2024-2028"
            ),
            total_budget=3_000_000_000_000,
            spent_amount=500_000_000_000,
            start_date=date(2025, 1, 1),
            expected_end_date=date(2029, 6, 30),
            status="in_progress",
            roi_score=78.0,
            efficiency_score=65.0,
            social_impact_score=82.0,
        ),
        Investment(
            project_name="Congo Digital - Transformation Numerique",
            sector="Numerique",
            province="National",
            description=(
                "Programme de transformation numerique incluant "
                "fibre optique nationale, digitalisation des "
                "services publics, facture normalisee et systeme "
                "Logirad DGRAD. Finance par la Banque mondiale"
            ),
            total_budget=857_760_000_000,
            spent_amount=200_000_000_000,
            start_date=date(2025, 6, 21),
            expected_end_date=date(2029, 12, 31),
            status="in_progress",
            roi_score=85.0,
            efficiency_score=80.0,
            social_impact_score=88.0,
        ),
        Investment(
            project_name="PDL-145 Territoires",
            sector="Developpement Local",
            province="National",
            description=(
                "Programme de Developpement Local des 145 "
                "Territoires. Construction d'ecoles, centres "
                "de sante, routes de desserte agricole dans "
                "chaque territoire de la RDC"
            ),
            total_budget=5_718_400_000_000,
            spent_amount=2_000_000_000_000,
            start_date=date(2023, 1, 1),
            expected_end_date=date(2028, 12, 31),
            status="in_progress",
            roi_score=70.0,
            efficiency_score=55.0,
            social_impact_score=95.0,
        ),
        Investment(
            project_name="RN2 Mbujimayi-Bukavu",
            sector="Infrastructure Routiere",
            province="Kasai Oriental",
            description=(
                "Construction de la Route Nationale N.2 reliant "
                "Mbujimayi a Bukavu. Priorite du budget 2025 "
                "pour le desenclavement des provinces centrales"
            ),
            total_budget=2_859_200_000_000,
            spent_amount=400_000_000_000,
            start_date=date(2025, 1, 1),
            expected_end_date=date(2030, 12, 31),
            status="in_progress",
            roi_score=72.0,
            efficiency_score=58.0,
            social_impact_score=85.0,
        ),
        Investment(
            project_name="Resilience Urbaine Kinshasa",
            sector="Urbanisme",
            province="Kinshasa",
            description=(
                "Programme de resilience urbaine finance par la "
                "Banque mondiale. Gestion des eaux pluviales, "
                "prevention des inondations, amenagement "
                "des quartiers"
            ),
            total_budget=571_840_000_000,
            spent_amount=100_000_000_000,
            start_date=date(2025, 6, 21),
            expected_end_date=date(2030, 6, 30),
            status="planned",
            roi_score=68.0,
            efficiency_score=62.0,
            social_impact_score=90.0,
        ),
        Investment(
            project_name="Gouvernance Economique et Transparence",
            sector="Gouvernance",
            province="National",
            description=(
                "Appui budgetaire de 600M USD de la Banque "
                "mondiale. Modernisation du Tresor, reforme "
                "des marches publics, amelioration de la "
                "comptabilite publique"
            ),
            total_budget=1_715_520_000_000,
            spent_amount=300_000_000_000,
            start_date=date(2025, 5, 21),
            expected_end_date=date(2028, 12, 31),
            status="in_progress",
            roi_score=82.0,
            efficiency_score=70.0,
            social_impact_score=75.0,
        ),
        Investment(
            project_name="Fonds d'Investissement Strategique",
            sector="Finance",
            province="National",
            description=(
                "Demarrage du Fonds d'investissement strategique "
                "de la RDC prevu dans le collectif budgetaire "
                "2025 pour la diversification economique"
            ),
            total_budget=1_429_600_000_000,
            spent_amount=0,
            start_date=date(2025, 7, 1),
            expected_end_date=date(2030, 12, 31),
            status="planned",
            roi_score=75.0,
            efficiency_score=60.0,
            social_impact_score=70.0,
        ),
        Investment(
            project_name="Couverture Sante Universelle (CSU)",
            sector="Sante",
            province="National",
            description=(
                "Mise en oeuvre de la Couverture Sante "
                "Universelle portee par le Chef de l'Etat. "
                "Construction d'hopitaux provinciaux et centres "
                "de sante dans les 26 provinces"
            ),
            total_budget=2_287_360_000_000,
            spent_amount=850_000_000_000,
            start_date=date(2024, 1, 1),
            expected_end_date=date(2028, 12, 31),
            status="in_progress",
            roi_score=65.0,
            efficiency_score=52.0,
            social_impact_score=98.0,
        ),
    ]
    db.add_all(investments)
    db.flush()


# ------------------------------------------------------------------
# PeaceNet -- Real 2025 security incidents
# Sources: OCHA, MONUSCO, IPIS, media congolais
# ------------------------------------------------------------------
def _seed_security_alerts(db: Session) -> None:
    if db.query(SecurityAlert).count() > 0:
        return
    alerts = [
        SecurityAlert(
            alert_type="conflit_arme",
            severity="critical",
            province="Nord-Kivu",
            territory="Goma",
            description=(
                "Chute de Goma aux mains du M23/AFC et forces "
                "rwandaises le 27 janvier 2025. Combats intenses, "
                "pillages, coupures d'eau et electricite, "
                "nombreuses victimes civiles"
            ),
            risk_score=9.8,
            recommended_action=(
                "Cessez-le-feu immediat, activation corridor humanitaire, protection des civils par MONUSCO"
            ),
        ),
        SecurityAlert(
            alert_type="conflit_arme",
            severity="critical",
            province="Sud-Kivu",
            territory="Bukavu",
            description=(
                "Prise de Bukavu par le M23/AFC en fevrier 2025. "
                "Avancee rapide depuis Minova (21 janvier). "
                "Chef-lieu provisoire transfere a Uvira"
            ),
            risk_score=9.5,
            recommended_action=(
                "Negociations de paix Doha/Washington, deploiement forces de securite, aide humanitaire d'urgence"
            ),
        ),
        SecurityAlert(
            alert_type="conflit_arme",
            severity="critical",
            province="Nord-Kivu",
            territory="Lubero",
            description=(
                "Affrontements FARDC-M23 le 18 fevrier 2025. "
                "Plus de 100 000 nouveaux deplaces sur les axes "
                "Alimbongo-Kitsombiro et Alimbongo-Kipese. "
                "89 civils tues dans des attaques armees"
            ),
            risk_score=9.2,
            recommended_action=("Evacuation populations, securisation axes humanitaires, renforcement FARDC"),
        ),
        SecurityAlert(
            alert_type="conflit_arme",
            severity="critical",
            province="Nord-Kivu",
            territory="Rutshuru",
            description=(
                "Affrontements entre groupes armes dans la "
                "chefferie de Bwito. 6 civils tues entre le 3 "
                "et 9 novembre 2025. 6 000 nouveaux deplaces "
                "a Kibirizi et Kabanda. Braquages sur l'axe "
                "Kiwanja-Kanyabayonga"
            ),
            risk_score=8.8,
            recommended_action=(
                "Securisation des axes routiers, protection des sites de deplaces, renforcement patrouilles"
            ),
        ),
        SecurityAlert(
            alert_type="conflit_arme",
            severity="critical",
            province="Nord-Kivu",
            territory="Masisi",
            description=(
                "Offensive M23 dans le groupement Nyamaboko. "
                "Prise du village strategique de Kazinga "
                "le 15 novembre 2025. Destructions massives, "
                "pillage de structures medicales"
            ),
            risk_score=9.0,
            recommended_action=(
                "Operation militaire de reprise, protection des structures sanitaires, assistance humanitaire"
            ),
        ),
        SecurityAlert(
            alert_type="conflit_arme",
            severity="high",
            province="Nord-Kivu",
            territory="Walikale",
            description=(
                "Assauts nocturnes du M23 a Bukumbirwa, "
                "groupement d'Ikobo. Affrontements pour le "
                "controle de localites, tensions "
                "intercommunautaires dans Waloa-Yungu"
            ),
            risk_score=8.2,
            recommended_action=(
                "Presence securitaire renforcee, mediation intercommunautaire, monitoring droits humains"
            ),
        ),
        SecurityAlert(
            alert_type="conflit_arme",
            severity="critical",
            province="Sud-Kivu",
            territory="Uvira",
            description=(
                "Chute d'Uvira le 9 decembre 2025. Chef-lieu "
                "provisoire du Sud-Kivu apres la prise de "
                "Bukavu. Expansion territoriale continue du "
                "M23 le long du lac Tanganyika"
            ),
            risk_score=9.3,
            recommended_action=(
                "Mise en oeuvre accord de Washington, retrait forces rwandaises, neutralisation FDLR, protection civils"
            ),
        ),
        SecurityAlert(
            alert_type="crise_humanitaire",
            severity="critical",
            province="Nord-Kivu",
            territory="Multiple",
            description=(
                "4 millions d'enfants de moins de 5 ans menaces "
                "de malnutrition aigue. 1,3 million en forme "
                "severe. 1,5 million de femmes enceintes/"
                "allaitantes necessitant traitement. CERF: "
                "17M USD alloues"
            ),
            risk_score=9.0,
            recommended_action=("Intensification aide alimentaire, acces humanitaire, corridors securises pour ONG"),
        ),
        SecurityAlert(
            alert_type="violence_ciblee",
            severity="high",
            province="Nord-Kivu",
            territory="Lubero",
            description=(
                "Assassinat de 3 travailleurs humanitaires "
                "HEKS/EPER a Kabirangiriro le 5 fevrier 2025. "
                "12 morts par bombardement des sites de "
                "deplaces Rusayo 1 et 2"
            ),
            risk_score=8.5,
            recommended_action=("Enquete sur violations du droit humanitaire, securisation des sites de deplaces"),
        ),
        SecurityAlert(
            alert_type="conflit_arme",
            severity="high",
            province="Sud-Kivu",
            territory="Mwenga",
            description=(
                "Avancee M23 dans la chefferie de Luhwindja, "
                "territoire de Mwenga. Capture de Luciga le "
                "6 mai 2025 aux portes de la mine de Twangiza"
            ),
            risk_score=8.0,
            recommended_action=("Securisation sites miniers, protection populations locales, surveillance MONUSCO"),
        ),
        SecurityAlert(
            alert_type="criminalite",
            severity="medium",
            province="Nord-Kivu",
            territory="Goma",
            description=(
                "Persistance des incursions nocturnes dans les "
                "quartiers peripheriques de Goma. Exactions "
                "contre civils, montee de la criminalite urbaine"
            ),
            risk_score=7.0,
            recommended_action=("Renforcement patrouilles nocturnes, eclairage public, systeme d'alerte communautaire"),
        ),
        SecurityAlert(
            alert_type="tension_sociale",
            severity="medium",
            province="Kinshasa",
            territory="Kinshasa",
            description=(
                "Tensions liees a l'inflation (8,8% moyen), "
                "depreciation du franc congolais (2 859 CDF/USD), "
                "hausse des prix des denrees alimentaires"
            ),
            risk_score=6.5,
            recommended_action=(
                "Dialogue social, controle des prix, politique monetaire de la BCC, subventions ciblees"
            ),
        ),
    ]
    db.add_all(alerts)
    db.flush()


# ------------------------------------------------------------------
# TranspaFin -- Real 2025 transparency reports
# ------------------------------------------------------------------
def _seed_transparency_reports(db: Session) -> None:
    if db.query(TransparencyReport).count() > 0:
        return
    reports = [
        TransparencyReport(
            ministry="DGI - Direction Generale des Impots",
            period="2025-Q3",
            transparency_score=78.5,
            compliance_rate=82.0,
            audit_findings=(
                "Mobilisation de 15 550,2 Mds CDF en 11 mois, "
                "soit +6,9% au-dessus des previsions. Bonne "
                "performance secteur minier (8 692,9 Mds CDF)"
            ),
            recommendations=(
                "Etendre la facture normalisee, poursuivre "
                "l'elargissement de l'assiette fiscale, "
                "renforcer la lutte contre la fraude"
            ),
            status="published",
        ),
        TransparencyReport(
            ministry="DGDA - Direction Generale des Douanes et Accises",
            period="2025-Q3",
            transparency_score=72.0,
            compliance_rate=75.0,
            audit_findings=(
                "Previsions revues en baisse de 13,8% (7 769 "
                "a 6 693 Mds CDF) suite a la contraction des "
                "activites commerciales dans les zones de "
                "conflit Est"
            ),
            recommendations=(
                "Digitalisation des procedures douanieres, "
                "renforcement du controle aux frontieres, "
                "compensation des pertes par les postes "
                "operationnels"
            ),
            status="published",
        ),
        TransparencyReport(
            ministry="DGRAD - Recettes Administratives",
            period="2025-Q3",
            transparency_score=62.0,
            compliance_rate=58.0,
            audit_findings=(
                "Chute drastique de 24,96% des previsions "
                "(3 344 a 2 509 Mds CDF). Recettes "
                "administratives et judiciaires en recul. "
                "Extension du systeme Logirad au secteur "
                "judiciaire en cours"
            ),
            recommendations=(
                "Deploiement complet du systeme Logirad, "
                "amelioration de la tracabilite des recettes "
                "non fiscales, audit des services generateurs"
            ),
            status="published",
        ),
        TransparencyReport(
            ministry="Ministere de la Defense Nationale",
            period="2025-Q3",
            transparency_score=28.0,
            compliance_rate=22.0,
            audit_findings=(
                "Depenses de securite >93% des depenses "
                "d'urgence. Depassement budgetaire sur le "
                "doublement des soldes militaires (~800M USD). "
                "Depenses classifiees non detaillees"
            ),
            recommendations=(
                "Audit parlementaire des depenses de defense, "
                "encadrement des depenses d'urgence, "
                "transparence accrue sur les marches "
                "d'equipement militaire"
            ),
            status="draft",
        ),
        TransparencyReport(
            ministry="Presidence de la Republique",
            period="2025-Q3",
            transparency_score=35.0,
            compliance_rate=30.0,
            audit_findings=(
                "Hausse de 40% des depenses de fonctionnement "
                "par rapport a 2024. Depassement budgetaire "
                "constate malgre les instructions de "
                "rationalisation du Chef de l'Etat (fev. 2025)"
            ),
            recommendations=(
                "Application effective de la reduction de 30% "
                "du train de vie des institutions, publication "
                "detaillee des depenses de fonctionnement"
            ),
            status="draft",
        ),
        TransparencyReport(
            ministry="Ministere des Mines",
            period="2025-Q3",
            transparency_score=55.0,
            compliance_rate=50.0,
            audit_findings=(
                "Pertes de 926 Mds CDF de recettes minieres "
                "dans les provinces sous occupation. Suspension "
                "exportation cobalt. ANAPI: 96 projets "
                "approuves pour 5,13 Mds USD"
            ),
            recommendations=(
                "Publication des contrats miniers, renforcement "
                "ITIE, diversification des recettes hors mines, "
                "securisation des sites miniers a l'Est"
            ),
            status="published",
        ),
        TransparencyReport(
            ministry="Ministere de l'EPST",
            period="2025-Q3",
            transparency_score=75.0,
            compliance_rate=72.0,
            audit_findings=(
                "Programme de gratuite de l'enseignement en "
                "bonne voie. 50 000 enfants ont vu leur "
                "scolarite interrompue au Nord-Kivu en raison "
                "du conflit. Fermeture ecoles a Goma"
            ),
            recommendations=(
                "Enseignement a distance dans les zones de "
                "conflit, reconstruction des ecoles detruites, "
                "suivi des fonds UNICEF"
            ),
            status="published",
        ),
        TransparencyReport(
            ministry="Ministere des Finances (Tresor Public)",
            period="2025-Q3",
            transparency_score=68.0,
            compliance_rate=65.0,
            audit_findings=(
                "Deficit cumule de 2 160,4 Mds CDF a fin juin "
                "2025. Financement par emission de titres "
                "publics. Rationalisation du train de vie: "
                "-18,9% fonctionnement institutions"
            ),
            recommendations=(
                "Modernisation du Tresor dans le cadre du "
                "programme Banque mondiale (600M USD), "
                "amelioration comptabilite publique, "
                "reforme marches publics"
            ),
            status="published",
        ),
        TransparencyReport(
            ministry="OGEFREM - Fret Multimodal",
            period="2025-Q3",
            transparency_score=42.0,
            compliance_rate=38.0,
            audit_findings=(
                "Installations de l'Est RDC hors controle de "
                "la Direction Generale depuis pres d'un an. "
                "Perte significative de recettes parafiscales. "
                "Impact de 30 ans de guerres sur les operations"
            ),
            recommendations=(
                "Evaluation complete des pertes, plan de "
                "relance post-conflit, diversification des "
                "sources de revenus, renforcement bureaux "
                "operationnels Ouest"
            ),
            status="draft",
        ),
    ]
    db.add_all(reports)
    db.flush()


# ------------------------------------------------------------------
# Citizen services -- Real 2025 DRC procedures
# ------------------------------------------------------------------
def _seed_citizen_data(db: Session) -> None:
    if db.query(Procedure).count() > 0:
        return

    passeport_steps = json.dumps(
        [
            "Obtenir le NIF sur app.dgirdc.cd/e-nif",
            "Pre-inscription en ligne sur passeport.gouv.cd",
            "Paiement de 75 USD via Equity BCDC",
            "Approbation de l'ANR avec documents personnels",
            "Capture biometrique chez DERMALOG avec code QR",
            "Retrait du passeport au site de capture",
        ]
    )
    passeport_docs = json.dumps(
        [
            "Numero d'Identification Fiscale (NIF)",
            "Ancien passeport (page BIO) ou acte de naissance",
            "Rapport de police en cas de perte ou vol",
            "2 photos d'identite (2x2 pouces)",
            "Autorisation ANR",
        ]
    )

    permis_steps = json.dumps(
        [
            "Paiement des frais d'examen (15 USD) a la RAWBANK",
            "Retrait du formulaire de demande (gratuit)",
            "Test theorique du Code de la Route au site CONADEP",
            "Test pratique de conduite",
            "Etablissement de la Note de Perception CONADEP",
            "Paiement des frais du permis selon la categorie",
            "Capture biometrique et enrolement",
            "Notification par SMS et retrait du permis",
        ]
    )
    permis_docs = json.dumps(
        [
            "Piece d'identite valide",
            "Certificat medical d'aptitude",
            "Recu de paiement RAWBANK (15 USD)",
            "Note de Perception CONADEP (selon categorie)",
            "Attestation de reussite aux examens",
        ]
    )

    cni_steps = json.dumps(
        [
            "Se presenter au centre d'identification ONIP",
            "Fournir informations: province, territoire, secteur, village",
            "Prise des donnees biometriques (empreintes, photo)",
            "Verification et validation des donnees par l'ONIP",
            "Delivrance de la carte d'identite nationale avec code QR",
        ]
    )
    cni_docs = json.dumps(
        [
            "Permis de conduire, carte d'electeur, acte de naissance, ou passeport",
            "Declaration de 3 temoins (si aucun document)",
            "Informations sur les grands-parents des deux cotes",
        ]
    )

    entreprise_steps = json.dumps(
        [
            "Obtenir le NIF aupres de la DGI (app.dgirdc.cd)",
            "Rediger et notarier les statuts de la societe",
            "Deposer le dossier au GUCE",
            "Obtenir le numero RCCM",
            "Immatriculation a la CNSS",
            "Publication au Journal Officiel",
        ]
    )
    entreprise_docs = json.dumps(
        [
            "Statuts notaries de la societe",
            "Numero d'Identification Fiscale (NIF)",
            "Piece d'identite du fondateur",
            "Preuve du capital social (attestation bancaire)",
            "Plan d'affaires",
            "Contrat de bail du siege social",
        ]
    )

    casier_steps = json.dumps(
        [
            "Se rendre au Parquet de Grande Instance",
            "Presenter la piece d'identite et remplir le formulaire",
            "Payer les frais de 10 000 FC",
            "Releve d'empreintes digitales",
            "Retrait de l'extrait dans un delai de 7 jours ouvrables",
        ]
    )
    casier_docs = json.dumps(
        [
            "Carte d'identite nationale",
            "Recu de paiement (10 000 FC)",
            "2 photos d'identite",
        ]
    )

    procedures = [
        Procedure(
            code="PROC-001",
            name="Passeport Biometrique Congolais",
            category="Voyages",
            description=(
                "Nouveau passeport biometrique lance le 5 juin "
                "2025 par le Ministere des Affaires Etrangeres. "
                "Conforme OACI 39794. Micropuce RFID, page "
                "polycarbonate, hologrammes securises"
            ),
            steps=passeport_steps,
            documents_required=passeport_docs,
            fees="75 USD",
            processing_time=("10 jours (Kinshasa), 14 jours (Province), 28 jours (Etranger)"),
            authority="Ministere des Affaires Etrangeres / DERMALOG",
        ),
        Procedure(
            code="PROC-002",
            name="Permis de Conduire Biometrique Securise",
            category="Transport",
            description=(
                "Permis de conduire biometrique avec puce "
                "electronique. Valable nationalement et "
                "internationalement. Relance nov. 2024 "
                "par la CONADEP"
            ),
            steps=permis_steps,
            documents_required=permis_docs,
            fees=("Cat.A: 44,5 USD | Cat.B: 77,5 USD | Cat.C/D: 104,5 USD (frais bancaires 5,5 USD inclus)"),
            processing_time="21 jours",
            authority=("CONADEP - Commission Nationale de Delivrance des Permis de Conduire"),
        ),
        Procedure(
            code="PROC-003",
            name="Carte d'Identite Nationale",
            category="Etat Civil",
            description=(
                "Carte d'identite nationale delivree par l'ONIP "
                "(Office National d'Identification de la "
                "Population). Carte avec code QR securise"
            ),
            steps=cni_steps,
            documents_required=cni_docs,
            fees="Gratuit (prise en charge par l'Etat)",
            processing_time="30 jours",
            authority=("ONIP - Office National d'Identification de la Population"),
        ),
        Procedure(
            code="PROC-004",
            name="Enregistrement d'une Entreprise au RCCM",
            category="Commerce",
            description=(
                "Procedure d'enregistrement d'une nouvelle "
                "entreprise aupres du Guichet Unique de "
                "Creation d'Entreprises (GUCE). Obtention "
                "du RCCM et immatriculation fiscale"
            ),
            steps=entreprise_steps,
            documents_required=entreprise_docs,
            fees="250 000 FC + frais notariaux",
            processing_time="14 jours ouvrables",
            authority="GUCE - Guichet Unique de Creation d'Entreprises",
        ),
        Procedure(
            code="PROC-005",
            name="Extrait de Casier Judiciaire",
            category="Justice",
            description=(
                "Document officiel attestant de l'absence ou "
                "de l'existence de condamnations penales. "
                "Requis pour emploi, voyages et procedures "
                "administratives"
            ),
            steps=casier_steps,
            documents_required=casier_docs,
            fees="10 000 FC",
            processing_time="7 jours ouvrables",
            authority="Parquet de Grande Instance / Greffe du Tribunal",
        ),
    ]

    pres_svc = json.dumps(
        [
            "Cabinet du President",
            "Secretariat General",
            "Maison Civile du Chef de l'Etat",
            "Conseil National de Securite",
        ]
    )
    finances_svc = json.dumps(
        [
            "Direction du Tresor Public (DGTCP)",
            "Direction Generale des Impots (DGI)",
            "Direction Generale des Douanes et Accises (DGDA)",
            "Direction Generale des Recettes Administratives (DGRAD)",
            "Inspection Generale des Finances",
        ]
    )
    budget_svc = json.dumps(
        [
            "Direction de la Preparation du Budget",
            "Direction du Controle Budgetaire",
            "Direction de la Paie",
            "Chaine de la Depense",
        ]
    )
    assemblee_svc = json.dumps(
        [
            "Bureau de l'Assemblee Nationale",
            "Commission ECOFIN",
            "Commissions permanentes",
            "Service legislatif",
        ]
    )
    justice_svc = json.dumps(
        [
            "Greffe",
            "Contentieux electoral",
            "Controle de constitutionnalite",
            "Interpretation de la Constitution",
        ]
    )
    dgm_svc = json.dumps(
        [
            "Delivrance de visas",
            "Controle migratoire",
            "Titre de sejour pour etrangers",
            "Police des frontieres",
        ]
    )

    contacts = [
        Contact(
            code="CONT-001",
            institution="Presidence de la Republique",
            address=("Palais de la Nation, Avenue du Palais de la Nation, Kinshasa/Gombe"),
            phone="+243 81 555 0001",
            email="info@presidence.cd",
            services=pres_svc,
            hours="Lun-Ven 08h00-16h00",
        ),
        Contact(
            code="CONT-002",
            institution="Ministere des Finances",
            address=("Boulevard du 30 Juin, Immeuble du Gouvernement, Kinshasa/Gombe"),
            phone="+243 81 555 0010",
            email="info@finances.gouv.cd",
            services=finances_svc,
            hours="Lun-Ven 08h00-16h00",
        ),
        Contact(
            code="CONT-003",
            institution="Ministere du Budget",
            address=(
                "Centre Financier de Kinshasa, Tour B, Place de l'Independance N.1, Avenue Nzongotolo, Kinshasa/Gombe"
            ),
            phone="+243 81 555 0020",
            email="info@budget.gouv.cd",
            services=budget_svc,
            hours="Lun-Ven 08h00-16h00",
        ),
        Contact(
            code="CONT-004",
            institution="Assemblee Nationale",
            address=("Palais du Peuple, Boulevard Triomphal, Kinshasa/Lingwala"),
            phone="+243 81 555 0002",
            email="info@assemblee-nationale.cd",
            services=assemblee_svc,
            hours="Lun-Ven 09h00-17h00",
        ),
        Contact(
            code="CONT-005",
            institution="Cour Constitutionnelle",
            address="Boulevard du 30 Juin, Kinshasa/Gombe",
            phone="+243 81 555 0003",
            email="greffe@courconstitutionnelle.cd",
            services=justice_svc,
            hours="Lun-Ven 08h30-15h30",
        ),
        Contact(
            code="CONT-006",
            institution="Direction Generale de Migration (DGM)",
            address="Avenue des Aviateurs, Kinshasa/Gombe",
            phone="+243 81 555 0050",
            email="info@dgm.cd",
            services=dgm_svc,
            hours="Lun-Ven 08h00-15h00",
        ),
    ]

    rights = [
        CitizenRight(
            code="DROIT-001",
            title="Droit a la vie",
            article="Article 16",
            description=(
                "Tout individu a droit a la vie et a l'integrite "
                "physique et mentale. Nul ne peut etre prive "
                "arbitrairement de la vie. (Constitution de la "
                "RDC, 18 fevrier 2006)"
            ),
            category="Droits Fondamentaux",
        ),
        CitizenRight(
            code="DROIT-002",
            title="Liberte d'expression",
            article="Article 23",
            description=(
                "Toute personne a droit a la liberte "
                "d'expression. Ce droit implique la liberte "
                "d'exprimer ses opinions et ses convictions, "
                "notamment par la parole, l'ecrit et l'image."
            ),
            category="Libertes Publiques",
        ),
        CitizenRight(
            code="DROIT-003",
            title="Droit a l'education gratuite",
            article="Article 43",
            description=(
                "L'enseignement primaire est obligatoire et "
                "gratuit dans les etablissements publics. Mis "
                "en oeuvre par le programme de Gratuite de "
                "l'Enseignement de Base depuis 2019."
            ),
            category="Droits Sociaux",
        ),
        CitizenRight(
            code="DROIT-004",
            title="Droit a la sante",
            article="Article 47",
            description=(
                "Le droit a la sante et a la securite "
                "alimentaire est garanti. La Couverture Sante "
                "Universelle (CSU) est en cours de deploiement "
                "dans les 26 provinces."
            ),
            category="Droits Sociaux",
        ),
        CitizenRight(
            code="DROIT-005",
            title="Droit a la propriete",
            article="Article 34",
            description=(
                "La propriete privee est sacree. L'Etat garantit "
                "le droit a la propriete individuelle ou "
                "collective. Nul ne peut etre prive de sa "
                "propriete que pour cause d'utilite publique."
            ),
            category="Droits Fondamentaux",
        ),
        CitizenRight(
            code="DROIT-006",
            title="Droit a l'information",
            article="Article 24",
            description=(
                "Toute personne a droit a l'information. La "
                "liberte de presse, la liberte d'information "
                "et d'emission par la radio et la television "
                "sont garanties."
            ),
            category="Libertes Publiques",
        ),
    ]

    faqs = [
        FAQ(
            code="FAQ-001",
            question="Comment obtenir le nouveau passeport biometrique?",
            answer=(
                "Depuis le 5 juin 2025, le nouveau passeport se "
                "demande en ligne sur passeport.gouv.cd. Etapes: "
                "obtenir le NIF sur app.dgirdc.cd, payer 75 USD "
                "via Equity BCDC, obtenir l'approbation ANR, "
                "capture biometrique DERMALOG. Delai: 10 jours "
                "a Kinshasa."
            ),
            category="Voyages",
        ),
        FAQ(
            code="FAQ-002",
            question=("Quels sont les frais du permis de conduire biometrique?"),
            answer=(
                "Les frais varient par categorie: Cat.A "
                "(deux-roues) 44,5 USD, Cat.B (vehicules legers) "
                "77,5 USD, Cat.C/D (poids lourds) 104,5 USD. "
                "Frais d'examen: 15 USD payables a la RAWBANK. "
                "Gere par la CONADEP."
            ),
            category="Transport",
        ),
        FAQ(
            code="FAQ-003",
            question="Comment payer ses impots a la DGI?",
            answer=(
                "La DGI a mis en place la digitalisation des "
                "procedures fiscales. Obtenir le NIF sur "
                "app.dgirdc.cd. Les paiements se font via les "
                "banques agreees ou en ligne. La facture "
                "normalisee est en cours de deploiement."
            ),
            category="Fiscalite",
        ),
        FAQ(
            code="FAQ-004",
            question=("Comment declarer les marchandises a la douane (DGDA)?"),
            answer=(
                "La DGDA gere les droits de douane et accises. "
                "Les declarations se font au bureau de douane du "
                "point d'entree. Documents requis: facture "
                "commerciale, connaissement, certificat "
                "d'origine, licence d'importation. Mobilisation "
                "2025: 634,5 Mds CDF en aout (105% des "
                "previsions)."
            ),
            category="Commerce",
        ),
        FAQ(
            code="FAQ-005",
            question="Comment obtenir un extrait de casier judiciaire?",
            answer=(
                "Rendez-vous au Parquet de Grande Instance avec "
                "votre carte d'identite et 2 photos. Frais: "
                "10 000 FC. Delai: 7 jours ouvrables. Releve "
                "d'empreintes digitales requis."
            ),
            category="Justice",
        ),
        FAQ(
            code="FAQ-006",
            question="Comment voter aux elections en RDC?",
            answer=(
                "Vous devez etre inscrit sur les listes "
                "electorales de la CENI. Presentez-vous au "
                "centre d'inscription avec votre carte "
                "d'identite. L'inscription est gratuite et "
                "obligatoire pour tout Congolais de 18 ans."
            ),
            category="Elections",
        ),
        FAQ(
            code="FAQ-007",
            question="Qu'est-ce que le PDL-145 Territoires?",
            answer=(
                "Le Programme de Developpement Local des 145 "
                "Territoires est un programme presidentiel "
                "visant a construire des infrastructures de "
                "base (ecoles, centres de sante, routes de "
                "desserte agricole) dans chacun des 145 "
                "territoires de la RDC. Budget: environ "
                "2 Mds USD."
            ),
            category="Developpement",
        ),
    ]
    db.add_all(procedures + contacts + rights + faqs)
    db.flush()
