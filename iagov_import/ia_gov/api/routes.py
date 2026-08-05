"""FastAPI routes for the Government AI API."""

from fastapi import APIRouter, HTTPException, Query

from ia_gov.services.gov_service import GovService

router = APIRouter()
service = GovService()


@router.get("/procedures", tags=["Procedures"])
def list_procedures(category: str | None = Query(None, description="Filter by category")) -> dict:
    """List all administrative procedures."""
    procedures = service.list_procedures(category)
    return {"count": len(procedures), "procedures": procedures}


@router.get("/procedures/search/", tags=["Procedures"])
def search_procedures(
    q: str = Query(..., description="Search query"),
    category: str | None = Query(None, description="Filter by category"),
) -> dict:
    """Search procedures by keyword."""
    results = service.find_procedures(q, category)
    return {"query": q, "count": len(results), "results": results}


@router.get("/procedures/{proc_id}", tags=["Procedures"])
def get_procedure(proc_id: str) -> dict:
    """Get details of a specific procedure."""
    proc = service.get_procedure(proc_id)
    if not proc:
        raise HTTPException(status_code=404, detail=f"Procedure '{proc_id}' not found")
    return proc


@router.get("/contacts", tags=["Contacts"])
def list_contacts() -> dict:
    """List all government institution contacts."""
    contacts = service.list_contacts()
    return {"count": len(contacts), "contacts": contacts}


@router.get("/contacts/search/", tags=["Contacts"])
def search_contacts(q: str = Query(..., description="Search query")) -> dict:
    """Search contacts by keyword."""
    results = service.find_contacts(q)
    return {"query": q, "count": len(results), "results": results}


@router.get("/contacts/{contact_id}", tags=["Contacts"])
def get_contact(contact_id: str) -> dict:
    """Get details of a specific contact."""
    contact = service.get_contact(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail=f"Contact '{contact_id}' not found")
    return contact


@router.get("/rights", tags=["Citizen Rights"])
def list_rights(category: str | None = Query(None, description="Filter by category")) -> dict:
    """List all citizen rights and obligations."""
    rights = service.list_rights(category)
    return {"count": len(rights), "rights": rights}


@router.get("/rights/search/", tags=["Citizen Rights"])
def search_rights(
    q: str = Query(..., description="Search query"),
    category: str | None = Query(None, description="Filter by category"),
) -> dict:
    """Search citizen rights by keyword."""
    results = service.find_rights(q, category)
    return {"query": q, "count": len(results), "results": results}


@router.get("/faq", tags=["FAQ"])
def list_faq() -> dict:
    """List all frequently asked questions."""
    items = service.list_faq()
    return {"count": len(items), "faq": items}


@router.get("/faq/search/", tags=["FAQ"])
def search_faq(q: str = Query(..., description="Search query")) -> dict:
    """Search FAQ by keyword."""
    results = service.find_faq(q)
    return {"query": q, "count": len(results), "results": results}


@router.get("/categories", tags=["Categories"])
def list_categories() -> dict:
    """List all procedure categories."""
    categories = service.get_categories()
    return {"count": len(categories), "categories": categories}


@router.get("/stats", tags=["Statistics"])
def get_statistics() -> dict:
    """Get platform statistics."""
    return service.get_statistics()
