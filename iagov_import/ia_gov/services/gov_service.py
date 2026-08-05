"""Government services business logic."""

from ia_gov.data.government_data import (
    CITIZEN_RIGHTS,
    CONTACTS,
    FAQ,
    PROCEDURES,
    get_all_categories,
    get_contact_by_id,
    get_procedure_by_id,
    search_contacts,
    search_faq,
    search_procedures,
    search_rights,
)


class GovService:
    """Service class for government data operations."""

    def list_procedures(self, category: str | None = None) -> list[dict]:
        """List all procedures, optionally filtered by category."""
        if category:
            return [p for p in PROCEDURES if p["category"].lower() == category.lower()]
        return PROCEDURES

    def get_procedure(self, proc_id: str) -> dict | None:
        """Get a single procedure by ID."""
        return get_procedure_by_id(proc_id)

    def find_procedures(self, query: str, category: str | None = None) -> list[dict]:
        """Search procedures by keyword."""
        return search_procedures(query, category)

    def list_contacts(self) -> list[dict]:
        """List all government contacts."""
        return CONTACTS

    def get_contact(self, contact_id: str) -> dict | None:
        """Get a single contact by ID."""
        return get_contact_by_id(contact_id)

    def find_contacts(self, query: str) -> list[dict]:
        """Search contacts by keyword."""
        return search_contacts(query)

    def list_rights(self, category: str | None = None) -> list[dict]:
        """List all citizen rights, optionally filtered by category."""
        if category:
            return [r for r in CITIZEN_RIGHTS if r["category"].lower() == category.lower()]
        return CITIZEN_RIGHTS

    def find_rights(self, query: str, category: str | None = None) -> list[dict]:
        """Search rights by keyword."""
        return search_rights(query, category)

    def list_faq(self) -> list[dict]:
        """List all FAQ items."""
        return FAQ

    def find_faq(self, query: str) -> list[dict]:
        """Search FAQ by keyword."""
        return search_faq(query)

    def get_categories(self) -> list[str]:
        """Get all procedure categories."""
        return get_all_categories()

    def get_statistics(self) -> dict:
        """Get platform statistics."""
        return {
            "total_procedures": len(PROCEDURES),
            "total_contacts": len(CONTACTS),
            "total_rights": len(CITIZEN_RIGHTS),
            "total_faq": len(FAQ),
            "categories": get_all_categories(),
        }
