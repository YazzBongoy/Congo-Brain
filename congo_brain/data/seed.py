"""Seed data — realistic DRC governance data for all modules."""

from __future__ import annotations

import json
from datetime import date, datetime

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
            role="admin", ministry="Presidence",
        ),
        User(
            username="analyste_budget",
            email="budget@congobrain.cd",
            password_hash=hash_password("budget123"),
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
            username="citoyen",
            email="citoyen@congobrain.cd",
            password_hash=hash_password("citoyen123"),
            role="viewer",
        ),
    ]
    db.add_all(users)
    db.flush()


def _seed_budgets(db: Session) -> None:
    if db.query(Budget).count() > 0:
        return
    budgets = [
        Budget(
            ministry="Ministere des Finances",
            sector="Administration",
            allocated_amount=500_000_000_000,
            spent_amount=350_000_000_000,
            fiscal_year=2025,
        ),
        Budget(
            ministry="Ministere de la Sante",
            sector="Sante Publique",
            allocated_amount=300_000_000_000,
            spent_amount=280_000_000_000,
            fiscal_year=2025,
        ),
        Budget(
            ministry="Ministere de l'Education",
            sector="Education Primaire",
            allocated_amount=450_000_000_000,
            spent_amount=200_000_000_000,
            fiscal_year=2025,
        ),
        Budget(
            ministry="Ministere des Infrastructures",
            sector="Routes Nationales",
            allocated_amount=800_000_000_000,
            spent_amount=600_000_000_000,
            fiscal_year=2025,
        ),
        Budget(
            ministry="Ministere de la Defense",
            sector="Defense Nationale",
            allocated_amount=600_000_000_000,
            spent_amount=580_000_000_000,
            fiscal_year=2025,
        ),
        Budget(
            ministry="Ministere de l'Agriculture",
            sector="Agriculture",
            allocated_amount=200_000_000_000,
            spent_amount=120_000_000_000,
            fiscal_year=2025,
        ),
        Budget(
            ministry="Ministere des Mines",
            sector="Exploitation Miniere",
            allocated_amount=350_000_000_000,
            spent_amount=100_000_000_000,
            fiscal_year=2025,
        ),
        Budget(
            ministry="Ministere de l'Interieur",
            sector="Administration Territoriale",
            allocated_amount=250_000_000_000,
            spent_amount=230_000_000_000,
            fiscal_year=2025,
        ),
    ]
    db.add_all(budgets)
    db.flush()

    transactions = [
        Transaction(
            budget_id=1, amount=50_000_000_000,
            description="Salaires fonctionnaires Q1",
            transaction_type="depense",
            beneficiary="Fonction Publique",
            reference_number="TXN-2025-001",
        ),
        Transaction(
            budget_id=1, amount=75_000_000_000,
            description="Equipement informatique",
            transaction_type="depense",
            beneficiary="SNEL",
            reference_number="TXN-2025-002",
        ),
        Transaction(
            budget_id=1, amount=500_000_000_000,
            description="Paiement suspect consultant",
            transaction_type="depense",
            beneficiary="Societe Ecran SARL",
            reference_number="TXN-2025-003",
        ),
        Transaction(
            budget_id=2, amount=80_000_000_000,
            description="Medicaments essentiels",
            transaction_type="depense",
            beneficiary="Pharma Congo",
            reference_number="TXN-2025-004",
        ),
        Transaction(
            budget_id=2, amount=40_000_000_000,
            description="Construction hopital Kinshasa",
            transaction_type="depense",
            beneficiary="BTP Congo",
            reference_number="TXN-2025-005",
        ),
        Transaction(
            budget_id=3, amount=60_000_000_000,
            description="Manuels scolaires",
            transaction_type="depense",
            beneficiary="Editions Congolaises",
            reference_number="TXN-2025-006",
        ),
        Transaction(
            budget_id=4, amount=200_000_000_000,
            description="Route Nationale No. 1",
            transaction_type="depense",
            beneficiary="China Roads",
            reference_number="TXN-2025-007",
        ),
        Transaction(
            budget_id=4, amount=150_000_000_000,
            description="Pont Matadi-Kinshasa",
            transaction_type="depense",
            beneficiary="Consortium BTP",
            reference_number="TXN-2025-008",
        ),
        Transaction(
            budget_id=5, amount=100_000_000_000,
            description="Equipement militaire",
            transaction_type="depense",
            beneficiary="Defense Systems",
            reference_number="TXN-2025-009",
        ),
        Transaction(
            budget_id=6, amount=30_000_000_000,
            description="Semences ameliorees",
            transaction_type="depense",
            beneficiary="AgroCongo",
            reference_number="TXN-2025-010",
        ),
    ]
    db.add_all(transactions)
    db.flush()


def _seed_investments(db: Session) -> None:
    if db.query(Investment).count() > 0:
        return
    investments = [
        Investment(
            project_name="Barrage Inga III",
            sector="Energie",
            province="Kongo Central",
            description="Centrale hydroelectrique de 11 GW",
            total_budget=14_000_000_000_000,
            spent_amount=2_000_000_000_000,
            start_date=date(2024, 1, 1),
            expected_end_date=date(2030, 12, 31),
            status="in_progress", roi_score=85.0,
            efficiency_score=70.0,
            social_impact_score=95.0,
        ),
        Investment(
            project_name="Fibre Optique Nationale",
            sector="Telecoms", province="Kinshasa",
            description=(
                "Reseau fibre optique couvrant "
                "les 26 provinces"
            ),
            total_budget=500_000_000_000,
            spent_amount=150_000_000_000,
            start_date=date(2024, 6, 1),
            expected_end_date=date(2027, 12, 31),
            status="in_progress", roi_score=90.0,
            efficiency_score=80.0,
            social_impact_score=85.0,
        ),
        Investment(
            project_name=(
                "Port en Eau Profonde de Banana"
            ),
            sector="Transport",
            province="Kongo Central",
            description=(
                "Construction du port en eau profonde"
            ),
            total_budget=3_000_000_000_000,
            spent_amount=500_000_000_000,
            start_date=date(2025, 1, 1),
            expected_end_date=date(2029, 6, 30),
            status="planned", roi_score=75.0,
            efficiency_score=65.0,
            social_impact_score=80.0,
        ),
        Investment(
            project_name=(
                "Zone Economique Speciale de Maluku"
            ),
            sector="Industrie", province="Kinshasa",
            description="Parc industriel et zone franche",
            total_budget=1_200_000_000_000,
            spent_amount=300_000_000_000,
            start_date=date(2024, 3, 1),
            expected_end_date=date(2028, 12, 31),
            status="in_progress", roi_score=80.0,
            efficiency_score=75.0,
            social_impact_score=70.0,
        ),
        Investment(
            project_name=(
                "Universite Numerique du Congo"
            ),
            sector="Education", province="Kinshasa",
            description=(
                "Plateforme d\'enseignement en ligne"
            ),
            total_budget=100_000_000_000,
            spent_amount=20_000_000_000,
            start_date=date(2025, 1, 1),
            expected_end_date=date(2026, 12, 31),
            status="planned", roi_score=70.0,
            efficiency_score=85.0,
            social_impact_score=90.0,
        ),
        Investment(
            project_name="Hopitaux Provinciaux Modernes",
            sector="Sante", province="Haut-Katanga",
            description=(
                "Construction de 10 hopitaux modernes"
            ),
            total_budget=800_000_000_000,
            spent_amount=100_000_000_000,
            start_date=date(2025, 6, 1),
            expected_end_date=date(2029, 12, 31),
            status="planned", roi_score=60.0,
            efficiency_score=55.0,
            social_impact_score=95.0,
        ),
        Investment(
            project_name=(
                "Chemin de Fer Kinshasa-Ilebo"
            ),
            sector="Transport", province="Kasai",
            description=(
                "Rehabilitation de la ligne "
                "ferroviaire"
            ),
            total_budget=2_500_000_000_000,
            spent_amount=0,
            start_date=date(2026, 1, 1),
            expected_end_date=date(2031, 12, 31),
            status="planned", roi_score=65.0,
            efficiency_score=50.0,
            social_impact_score=75.0,
        ),
        Investment(
            project_name=(
                "Parc Agro-Industriel Bukanga Lonzo"
            ),
            sector="Agriculture", province="Kwango",
            description=(
                "Relance du parc agro-industriel"
            ),
            total_budget=400_000_000_000,
            spent_amount=50_000_000_000,
            start_date=date(2025, 3, 1),
            expected_end_date=date(2028, 3, 31),
            status="in_progress", roi_score=55.0,
            efficiency_score=45.0,
            social_impact_score=80.0,
        ),
    ]
    db.add_all(investments)
    db.flush()


def _seed_security_alerts(db: Session) -> None:
    if db.query(SecurityAlert).count() > 0:
        return
    alerts = [
        SecurityAlert(
            alert_type="conflit_arme",
            severity="critical",
            province="Nord-Kivu",
            territory="Rutshuru",
            description=(
                "Affrontements entre FARDC et "
                "groupes armes dans le territoire "
                "de Rutshuru"
            ),
            risk_score=9.2,
            recommended_action=(
                "Deploiement de casques bleus "
                "MONUSCO et renforcement FARDC"
            ),
        ),
        SecurityAlert(
            alert_type="conflit_arme",
            severity="critical",
            province="Ituri", territory="Djugu",
            description=(
                "Attaques de milices CODECO "
                "contre des villages civils"
            ),
            risk_score=8.8,
            recommended_action=(
                "Operation militaire conjointe "
                "et protection des civils"
            ),
        ),
        SecurityAlert(
            alert_type="tension_sociale",
            severity="high",
            province="Kinshasa",
            territory="Kinshasa",
            description=(
                "Manifestations contre la hausse "
                "des prix des denrees alimentaires"
            ),
            risk_score=7.5,
            recommended_action=(
                "Dialogue avec les syndicats "
                "et controle des prix"
            ),
        ),
        SecurityAlert(
            alert_type="catastrophe_naturelle",
            severity="high",
            province="Sud-Kivu",
            territory="Kalehe",
            description=(
                "Glissement de terrain suite "
                "aux fortes pluies"
            ),
            risk_score=7.0,
            recommended_action=(
                "Evacuation des populations "
                "et aide humanitaire"
            ),
        ),
        SecurityAlert(
            alert_type="tension_ethnique",
            severity="medium",
            province="Tanganyika",
            territory="Kalemie",
            description=(
                "Tensions entre communautes "
                "Twa et Bantou"
            ),
            risk_score=6.0,
            recommended_action=(
                "Mediation intercommunautaire "
                "et presence securitaire"
            ),
        ),
        SecurityAlert(
            alert_type="criminalite",
            severity="medium",
            province="Haut-Katanga",
            territory="Lubumbashi",
            description=(
                "Augmentation des vols et "
                "cambriolages dans la ville"
            ),
            risk_score=5.5,
            recommended_action=(
                "Renforcement des patrouilles "
                "de police"
            ),
        ),
        SecurityAlert(
            alert_type="epidemie",
            severity="high",
            province="Equateur",
            territory="Mbandaka",
            description=(
                "Resurgence du virus Ebola "
                "dans la region"
            ),
            risk_score=8.0,
            recommended_action=(
                "Activation du protocole "
                "de riposte Ebola"
            ),
        ),
        SecurityAlert(
            alert_type="conflit_foncier",
            severity="low",
            province="Kasai Central",
            territory="Kananga",
            description=(
                "Litige foncier entre "
                "chefs coutumiers"
            ),
            risk_score=3.5, is_resolved=True,
            recommended_action=(
                "Mediation par les autorites "
                "provinciales"
            ),
            resolved_at=datetime(2025, 3, 15),
        ),
    ]
    db.add_all(alerts)
    db.flush()


def _seed_transparency_reports(db: Session) -> None:
    if db.query(TransparencyReport).count() > 0:
        return
    reports = [
        TransparencyReport(
            ministry="Ministere des Finances",
            period="2025-Q1",
            transparency_score=72.5,
            compliance_rate=68.0,
            audit_findings=(
                "Irregularites dans les depenses "
                "de fonctionnement"
            ),
            recommendations=(
                "Renforcer les controles internes"
            ),
            status="published",
        ),
        TransparencyReport(
            ministry="Ministere de la Sante",
            period="2025-Q1",
            transparency_score=65.0,
            compliance_rate=60.0,
            audit_findings=(
                "Manque de tracabilite "
                "des medicaments"
            ),
            recommendations=(
                "Mise en place d'un systeme "
                "de suivi pharmaceutique"
            ),
            status="published",
        ),
        TransparencyReport(
            ministry="Ministere de l'Education",
            period="2025-Q1",
            transparency_score=80.0,
            compliance_rate=75.0,
            audit_findings=(
                "Bonne gestion des fonds UNICEF"
            ),
            recommendations=(
                "Etendre le modele "
                "aux fonds nationaux"
            ),
            status="published",
        ),
        TransparencyReport(
            ministry="Ministere des Infrastructures",
            period="2025-Q1",
            transparency_score=55.0,
            compliance_rate=50.0,
            audit_findings=(
                "Surfacturation sur plusieurs "
                "contrats routiers"
            ),
            recommendations=(
                "Audit approfondi des contrats BTP"
            ),
            status="draft",
        ),
        TransparencyReport(
            ministry="Ministere des Mines",
            period="2025-Q1",
            transparency_score=45.0,
            compliance_rate=40.0,
            audit_findings=(
                "Opacite dans l'attribution "
                "des permis miniers"
            ),
            recommendations=(
                "Publication obligatoire "
                "des contrats miniers"
            ),
            status="draft",
        ),
        TransparencyReport(
            ministry="Ministere de la Defense",
            period="2025-Q1",
            transparency_score=35.0,
            compliance_rate=30.0,
            audit_findings=(
                "Budget non detaille, "
                "depenses classifiees"
            ),
            recommendations=(
                "Audit parlementaire "
                "des depenses de defense"
            ),
            status="draft",
        ),
    ]
    db.add_all(reports)
    db.flush()


def _seed_citizen_data(db: Session) -> None:
    if db.query(Procedure).count() > 0:
        return

    proc_steps_1 = json.dumps([
        "Se rendre au bureau communal",
        "Remplir le formulaire",
        "Fournir les documents requis",
        "Payer les frais",
        "Attendre la delivrance",
    ])
    proc_docs_1 = json.dumps([
        "Attestation de naissance",
        "2 photos d'identite",
        "Attestation de residence",
    ])
    proc_steps_2 = json.dumps([
        "Rediger les statuts",
        "Notarier les statuts",
        "Deposer au Guichet Unique",
        "Obtenir le RCCM",
        "S'enregistrer a la DGI",
    ])
    proc_docs_2 = json.dumps([
        "Statuts notaries",
        "Piece d'identite du fondateur",
        "Plan d'affaires",
        "Preuve de capital",
    ])
    proc_steps_3 = json.dumps([
        "Se rendre a la DGM",
        "Remplir le formulaire",
        "Fournir les documents",
        "Prise d'empreintes et photo",
        "Payer les frais",
        "Retirer le passeport",
    ])
    proc_docs_3 = json.dumps([
        "Carte d'identite",
        "Acte de naissance",
        "4 photos",
        "Ancien passeport (si renouvellement)",
    ])

    procedures = [
        Procedure(
            code="PROC-001",
            name=(
                "Obtention de la carte "
                "d'identite nationale"
            ),
            category="Etat Civil",
            description=(
                "Procedure pour obtenir "
                "une carte d'identite"
            ),
            steps=proc_steps_1,
            documents_required=proc_docs_1,
            fees="25 000 FC",
            processing_time="30 jours",
            authority="Bureau communal",
        ),
        Procedure(
            code="PROC-002",
            name=(
                "Enregistrement "
                "d'une entreprise"
            ),
            category="Commerce",
            description=(
                "Procedure pour enregistrer "
                "une nouvelle entreprise au RCCM"
            ),
            steps=proc_steps_2,
            documents_required=proc_docs_2,
            fees="250 000 FC",
            processing_time="14 jours",
            authority=(
                "Guichet Unique de "
                "Creation d'Entreprises"
            ),
        ),
        Procedure(
            code="PROC-003",
            name="Obtention du passeport",
            category="Voyages",
            description=(
                "Procedure pour obtenir "
                "un passeport biometrique"
            ),
            steps=proc_steps_3,
            documents_required=proc_docs_3,
            fees="185 USD",
            processing_time="21 jours",
            authority=(
                "Direction Generale de Migration"
            ),
        ),
    ]

    cont_svc_1 = json.dumps([
        "Cabinet du President",
        "Secretariat General",
    ])
    cont_svc_2 = json.dumps([
        "Bureau de l'Assemblee",
        "Commissions parlementaires",
    ])
    cont_svc_3 = json.dumps([
        "Greffe",
        "Contentieux electoral",
        "Controle de constitutionnalite",
    ])

    contacts = [
        Contact(
            code="CONT-001",
            institution=(
                "Presidence de la Republique"
            ),
            address=(
                "Palais de la Nation, "
                "Kinshasa/Gombe"
            ),
            phone="+243 81 555 0001",
            email="info@presidence.cd",
            services=cont_svc_1,
            hours="Lun-Ven 08h00-16h00",
        ),
        Contact(
            code="CONT-002",
            institution="Assemblee Nationale",
            address=(
                "Palais du Peuple, "
                "Kinshasa/Lingwala"
            ),
            phone="+243 81 555 0002",
            email="info@assemblee-nationale.cd",
            services=cont_svc_2,
            hours="Lun-Ven 09h00-17h00",
        ),
        Contact(
            code="CONT-003",
            institution="Cour Constitutionnelle",
            address=(
                "Boulevard du 30 Juin, "
                "Kinshasa/Gombe"
            ),
            phone="+243 81 555 0003",
            email=(
                "greffe@courconstitutionnelle.cd"
            ),
            services=cont_svc_3,
            hours="Lun-Ven 08h30-15h30",
        ),
    ]
    rights = [
        CitizenRight(
            code="DROIT-001",
            title="Droit a la vie",
            article="Article 16",
            description=(
                "Tout individu a droit a la vie "
                "et a l'integrite physique. Nul "
                "ne peut etre prive de la vie."
            ),
            category="Droits Fondamentaux",
        ),
        CitizenRight(
            code="DROIT-002",
            title="Liberte d'expression",
            article="Article 23",
            description=(
                "Toute personne a droit a la "
                "liberte d'expression. Ce droit "
                "implique la liberte d'exprimer "
                "ses opinions."
            ),
            category="Libertes Publiques",
        ),
        CitizenRight(
            code="DROIT-003",
            title="Droit a l'education",
            article="Article 43",
            description=(
                "L'enseignement primaire est "
                "obligatoire et gratuit dans les "
                "etablissements publics."
            ),
            category="Droits Sociaux",
        ),
        CitizenRight(
            code="DROIT-004",
            title="Droit a la sante",
            article="Article 47",
            description=(
                "Le droit a la sante et a la "
                "securite alimentaire est garanti."
            ),
            category="Droits Sociaux",
        ),
    ]
    faqs = [
        FAQ(
            code="FAQ-001",
            question=(
                "Comment obtenir un extrait "
                "de casier judiciaire?"
            ),
            answer=(
                "Rendez-vous au Parquet de "
                "Grande Instance de votre "
                "ressort avec votre carte "
                "d'identite. Les frais sont "
                "de 10 000 FC et le delai est "
                "de 7 jours ouvrables."
            ),
            category="Justice",
        ),
        FAQ(
            code="FAQ-002",
            question=(
                "Comment voter aux elections?"
            ),
            answer=(
                "Vous devez etre inscrit sur "
                "les listes electorales de la "
                "CENI. Presentez-vous au centre "
                "d'inscription avec votre carte "
                "d'identite. Le jour du vote, "
                "rendez-vous au bureau de vote "
                "avec votre carte d'electeur."
            ),
            category="Elections",
        ),
        FAQ(
            code="FAQ-003",
            question=(
                "Comment declarer "
                "une naissance?"
            ),
            answer=(
                "La declaration doit etre faite "
                "dans les 90 jours suivant la "
                "naissance au bureau de l'etat "
                "civil de la commune. Presentez "
                "le certificat de naissance "
                "delivre par la maternite et "
                "les pieces d'identite "
                "des parents."
            ),
            category="Etat Civil",
        ),
    ]
    db.add_all(procedures + contacts + rights + faqs)
    db.flush()
