"""Government data store with procedures, documents, contacts, and citizen info."""

from typing import Optional

PROCEDURES: list[dict] = [
    {
        "id": "proc-001",
        "name": "Demande de Passeport",
        "category": "Identité",
        "description": "Procédure pour obtenir un passeport biométrique.",
        "steps": [
            "Se rendre au bureau communal avec les documents requis",
            "Remplir le formulaire de demande",
            "Payer les frais de passeport",
            "Prise de photo et empreintes digitales",
            "Retirer le passeport après 30 jours ouvrables",
        ],
        "documents_required": [
            "Carte d'identité",
            "Acte de naissance",
            "Photos d'identité (4x4)",
            "Quittance de paiement",
        ],
        "fees": "50 USD",
        "processing_time": "30 jours ouvrables",
        "authority": "Direction Générale de Migration (DGM)",
    },
    {
        "id": "proc-002",
        "name": "Carte d'Identité Nationale",
        "category": "Identité",
        "description": "Procédure pour obtenir la carte d'identité nationale.",
        "steps": [
            "Se présenter au bureau d'état civil de la commune",
            "Fournir les documents requis",
            "Remplir le formulaire de demande",
            "Payer les frais d'établissement",
            "Retirer la carte après traitement",
        ],
        "documents_required": ["Acte de naissance", "Attestation de résidence", "Photos d'identité (4x4)"],
        "fees": "5 USD",
        "processing_time": "14 jours ouvrables",
        "authority": "Office National d'Identification de la Population (ONIP)",
    },
    {
        "id": "proc-003",
        "name": "Permis de Conduire",
        "category": "Transport",
        "description": "Procédure pour obtenir un permis de conduire.",
        "steps": [
            "S'inscrire dans une auto-école agréée",
            "Suivre la formation théorique et pratique",
            "Passer l'examen théorique",
            "Passer l'examen pratique de conduite",
            "Retirer le permis au ministère des Transports",
        ],
        "documents_required": [
            "Carte d'identité",
            "Certificat médical",
            "Attestation de formation auto-école",
            "Photos d'identité",
        ],
        "fees": "80 USD",
        "processing_time": "21 jours ouvrables",
        "authority": "Ministère des Transports et Voies de Communication",
    },
    {
        "id": "proc-004",
        "name": "Enregistrement d'Entreprise",
        "category": "Commerce",
        "description": "Procédure pour créer et enregistrer une entreprise.",
        "steps": [
            "Choisir la forme juridique de l'entreprise",
            "Rédiger les statuts de l'entreprise",
            "Déposer le dossier au Guichet Unique de Création d'Entreprise",
            "Payer les frais d'enregistrement",
            "Obtenir le numéro d'identification nationale (NIF)",
            "S'immatriculer au Registre du Commerce (RCCM)",
        ],
        "documents_required": [
            "Statuts notariés",
            "Carte d'identité du fondateur",
            "Attestation de compte bancaire",
            "Plan de localisation du siège social",
        ],
        "fees": "120 USD",
        "processing_time": "3 jours ouvrables",
        "authority": "Guichet Unique de Création d'Entreprise (GUCE)",
    },
    {
        "id": "proc-005",
        "name": "Acte de Naissance",
        "category": "État Civil",
        "description": "Procédure pour obtenir un acte de naissance.",
        "steps": [
            "Se présenter au bureau d'état civil de la commune de naissance",
            "Fournir les informations nécessaires (noms des parents, date de naissance)",
            "Payer les frais d'établissement",
            "Retirer l'acte de naissance",
        ],
        "documents_required": ["Attestation de l'hôpital ou de la maternité", "Carte d'identité des parents"],
        "fees": "2 USD",
        "processing_time": "1 jour ouvrable",
        "authority": "Bureau d'État Civil Communal",
    },
    {
        "id": "proc-006",
        "name": "Visa de Sortie",
        "category": "Migration",
        "description": "Procédure pour obtenir un visa de sortie du territoire.",
        "steps": [
            "Préparer les documents requis",
            "Se présenter à la Direction Générale de Migration",
            "Remplir le formulaire de demande",
            "Payer les frais de visa",
            "Retirer le visa de sortie",
        ],
        "documents_required": [
            "Passeport valide",
            "Billet d'avion",
            "Lettre d'invitation ou réservation d'hôtel",
            "Photos d'identité",
        ],
        "fees": "55 USD",
        "processing_time": "5 jours ouvrables",
        "authority": "Direction Générale de Migration (DGM)",
    },
    {
        "id": "proc-007",
        "name": "Certificat de Nationalité",
        "category": "Identité",
        "description": "Procédure pour obtenir un certificat de nationalité congolaise.",
        "steps": [
            "Constituer le dossier avec les documents requis",
            "Déposer le dossier au Tribunal de Grande Instance",
            "Payer les frais judiciaires",
            "Attendre la décision du tribunal",
            "Retirer le certificat de nationalité",
        ],
        "documents_required": [
            "Acte de naissance",
            "Carte d'identité des parents",
            "Attestation de résidence",
            "Casier judiciaire",
        ],
        "fees": "15 USD",
        "processing_time": "30 jours ouvrables",
        "authority": "Tribunal de Grande Instance",
    },
    {
        "id": "proc-008",
        "name": "Déclaration d'Impôts",
        "category": "Fiscalité",
        "description": "Procédure pour déclarer ses impôts annuels.",
        "steps": [
            "Rassembler tous les documents financiers de l'année",
            "Remplir la déclaration fiscale",
            "Déposer la déclaration à la Direction Générale des Impôts",
            "Payer les impôts dus",
            "Conserver le reçu de paiement",
        ],
        "documents_required": [
            "Bilan comptable",
            "Relevés bancaires",
            "Numéro d'Identification Fiscale (NIF)",
            "Attestation fiscale précédente",
        ],
        "fees": "Variable selon le montant imposable",
        "processing_time": "Avant le 31 mars de chaque année",
        "authority": "Direction Générale des Impôts (DGI)",
    },
]

CONTACTS: list[dict] = [
    {
        "id": "contact-001",
        "institution": "Direction Générale de Migration (DGM)",
        "address": "Avenue des Aviateurs, Kinshasa/Gombe",
        "phone": "+243 81 555 0001",
        "email": "info@dgm.gouv.cd",
        "services": ["Passeport", "Visa de sortie", "Titre de séjour"],
        "hours": "Lundi - Vendredi: 8h00 - 15h30",
    },
    {
        "id": "contact-002",
        "institution": "Office National d'Identification de la Population (ONIP)",
        "address": "Boulevard du 30 Juin, Kinshasa/Gombe",
        "phone": "+243 81 555 0002",
        "email": "contact@onip.gouv.cd",
        "services": ["Carte d'identité nationale", "Recensement"],
        "hours": "Lundi - Vendredi: 8h00 - 16h00",
    },
    {
        "id": "contact-003",
        "institution": "Guichet Unique de Création d'Entreprise (GUCE)",
        "address": "Avenue Colonel Lukusa, Kinshasa/Gombe",
        "phone": "+243 81 555 0003",
        "email": "info@guce.gouv.cd",
        "services": ["Création d'entreprise", "RCCM", "NIF"],
        "hours": "Lundi - Vendredi: 8h30 - 15h00",
    },
    {
        "id": "contact-004",
        "institution": "Direction Générale des Impôts (DGI)",
        "address": "Avenue des Marais, Kinshasa/Gombe",
        "phone": "+243 81 555 0004",
        "email": "fiscalite@dgi.gouv.cd",
        "services": ["Déclaration d'impôts", "NIF", "Attestation fiscale"],
        "hours": "Lundi - Vendredi: 8h00 - 15h30",
    },
    {
        "id": "contact-005",
        "institution": "Ministère des Transports et Voies de Communication",
        "address": "Boulevard Triomphal, Kinshasa/Gombe",
        "phone": "+243 81 555 0005",
        "email": "info@transports.gouv.cd",
        "services": ["Permis de conduire", "Immatriculation véhicule", "Contrôle technique"],
        "hours": "Lundi - Vendredi: 8h00 - 15h00",
    },
    {
        "id": "contact-006",
        "institution": "Ministère de la Justice",
        "address": "Avenue de Lemera, Kinshasa/Gombe",
        "phone": "+243 81 555 0006",
        "email": "cabinet@justice.gouv.cd",
        "services": ["Casier judiciaire", "Certificat de nationalité", "Légalisation de documents"],
        "hours": "Lundi - Vendredi: 8h30 - 15h30",
    },
]

CITIZEN_RIGHTS: list[dict] = [
    {
        "id": "right-001",
        "title": "Droit à l'Identité",
        "article": "Article 12 - Constitution de la RDC",
        "description": (
            "Tout Congolais a droit à un nom, un prénom et une nationalité. "
            "L'État a l'obligation de garantir l'identité de chaque citoyen."
        ),
        "category": "Droits Civils",
    },
    {
        "id": "right-002",
        "title": "Droit à l'Éducation",
        "article": "Article 43 - Constitution de la RDC",
        "description": "L'enseignement primaire est obligatoire et gratuit dans les établissements publics.",
        "category": "Droits Sociaux",
    },
    {
        "id": "right-003",
        "title": "Droit à la Santé",
        "article": "Article 47 - Constitution de la RDC",
        "description": (
            "Le droit à la santé et à la sécurité alimentaire est garanti. "
            "L'État veille à la prévention et au traitement des maladies."
        ),
        "category": "Droits Sociaux",
    },
    {
        "id": "right-004",
        "title": "Liberté d'Expression",
        "article": "Article 23 - Constitution de la RDC",
        "description": (
            "Toute personne a droit à la liberté d'expression. "
            "Ce droit implique la liberté d'exprimer ses opinions et ses convictions."
        ),
        "category": "Libertés Fondamentales",
    },
    {
        "id": "right-005",
        "title": "Droit de Vote",
        "article": "Article 5 - Constitution de la RDC",
        "description": (
            "La souveraineté nationale appartient au peuple. "
            "Tout Congolais majeur jouit de ses droits civiques et politiques."
        ),
        "category": "Droits Politiques",
    },
    {
        "id": "right-006",
        "title": "Droit au Travail",
        "article": "Article 36 - Constitution de la RDC",
        "description": (
            "Le travail est un droit et un devoir sacré pour chaque Congolais. "
            "L'État garantit le droit au travail et la protection contre le chômage."
        ),
        "category": "Droits Économiques",
    },
    {
        "id": "right-007",
        "title": "Droit à la Propriété",
        "article": "Article 34 - Constitution de la RDC",
        "description": (
            "Toute personne a droit à la propriété individuelle ou collective. "
            "Nul ne peut être privé de sa propriété que pour cause d'utilité publique."
        ),
        "category": "Droits Économiques",
    },
    {
        "id": "right-008",
        "title": "Droit à un Procès Équitable",
        "article": "Article 19 - Constitution de la RDC",
        "description": (
            "Toute personne a droit à un procès équitable. "
            "Nul ne peut être condamné pour une action qui ne constituait pas une infraction "
            "au moment où elle a été commise."
        ),
        "category": "Droits Judiciaires",
    },
]

FAQ: list[dict] = [
    {
        "id": "faq-001",
        "question": "Comment obtenir un passeport en RDC ?",
        "answer": (
            "Rendez-vous à la Direction Générale de Migration (DGM) avec votre carte d'identité, "
            "acte de naissance, 4 photos d'identité et la quittance de paiement de 50 USD. "
            "Le délai est de 30 jours ouvrables."
        ),
        "category": "Passeport",
    },
    {
        "id": "faq-002",
        "question": "Quel est le coût d'une carte d'identité nationale ?",
        "answer": "La carte d'identité nationale coûte 5 USD. Elle est délivrée par l'ONIP sous 14 jours ouvrables.",
        "category": "Identité",
    },
    {
        "id": "faq-003",
        "question": "Comment créer une entreprise en RDC ?",
        "answer": (
            "Adressez-vous au Guichet Unique de Création d'Entreprise (GUCE). "
            "Les frais sont de 120 USD et le délai est de 3 jours ouvrables. "
            "Vous devez fournir les statuts notariés, votre carte d'identité, "
            "une attestation bancaire et le plan de localisation."
        ),
        "category": "Commerce",
    },
    {
        "id": "faq-004",
        "question": "Quand faut-il déclarer ses impôts ?",
        "answer": (
            "La déclaration fiscale annuelle doit être déposée avant le 31 mars "
            "de chaque année auprès de la Direction Générale des Impôts (DGI)."
        ),
        "category": "Fiscalité",
    },
    {
        "id": "faq-005",
        "question": "Comment obtenir un acte de naissance ?",
        "answer": (
            "Présentez-vous au bureau d'état civil de votre commune de naissance "
            "avec l'attestation de l'hôpital/maternité et la carte d'identité des parents. "
            "Coût: 2 USD, délivré en 1 jour ouvrable."
        ),
        "category": "État Civil",
    },
    {
        "id": "faq-006",
        "question": "Quels sont les documents nécessaires pour un visa de sortie ?",
        "answer": (
            "Il faut un passeport valide, un billet d'avion, une lettre d'invitation "
            "ou réservation d'hôtel, et des photos d'identité. "
            "Coût: 55 USD, délivré sous 5 jours ouvrables."
        ),
        "category": "Migration",
    },
]


def search_procedures(query: str, category: Optional[str] = None) -> list[dict]:
    """Search procedures by keyword and optional category."""
    query_lower = query.lower()
    results = []
    for proc in PROCEDURES:
        if category and proc["category"].lower() != category.lower():
            continue
        if (
            query_lower in proc["name"].lower()
            or query_lower in proc["description"].lower()
            or query_lower in proc["category"].lower()
        ):
            results.append(proc)
    return results


def get_procedure_by_id(proc_id: str) -> Optional[dict]:
    """Get a specific procedure by ID."""
    for proc in PROCEDURES:
        if proc["id"] == proc_id:
            return proc
    return None


def search_contacts(query: str) -> list[dict]:
    """Search contacts by institution name or service."""
    query_lower = query.lower()
    results = []
    for contact in CONTACTS:
        if query_lower in contact["institution"].lower() or any(
            query_lower in service.lower() for service in contact["services"]
        ):
            results.append(contact)
    return results


def get_contact_by_id(contact_id: str) -> Optional[dict]:
    """Get a specific contact by ID."""
    for contact in CONTACTS:
        if contact["id"] == contact_id:
            return contact
    return None


def search_rights(query: str, category: Optional[str] = None) -> list[dict]:
    """Search citizen rights by keyword and optional category."""
    query_lower = query.lower()
    results = []
    for right in CITIZEN_RIGHTS:
        if category and right["category"].lower() != category.lower():
            continue
        if (
            query_lower in right["title"].lower()
            or query_lower in right["description"].lower()
            or query_lower in right["category"].lower()
        ):
            results.append(right)
    return results


def search_faq(query: str) -> list[dict]:
    """Search FAQ by keyword."""
    query_lower = query.lower()
    results = []
    for item in FAQ:
        if query_lower in item["question"].lower() or query_lower in item["answer"].lower():
            results.append(item)
    return results


def get_all_categories() -> list[str]:
    """Get all unique procedure categories."""
    return sorted(set(proc["category"] for proc in PROCEDURES))
