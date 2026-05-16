"""Citizen services API routes — procedures, contacts, rights, FAQ."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from congo_brain.core.database import get_db
from congo_brain.services.citizen_service import CitizenService

router = APIRouter(tags=["Citizen Services"])


def _svc(db: Session = Depends(get_db)) -> CitizenService:
    return CitizenService(db)


@router.get("/procedures")
def list_procedures(category: str | None = Query(None), svc: CitizenService = Depends(_svc)) -> dict:
    procs = svc.list_procedures(category)
    return {"count": len(procs), "procedures": procs}


@router.get("/procedures/search/")
def search_procedures(
    q: str = Query(...),
    category: str | None = Query(None),
    svc: CitizenService = Depends(_svc),
) -> dict:
    results = svc.search_procedures(q, category)
    return {"query": q, "count": len(results), "results": results}


@router.get("/procedures/{proc_id}")
def get_procedure(proc_id: str, svc: CitizenService = Depends(_svc)) -> dict:
    proc = svc.get_procedure(proc_id)
    if not proc:
        raise HTTPException(status_code=404, detail=f"Procedure '{proc_id}' not found")
    return proc


@router.get("/contacts")
def list_contacts(svc: CitizenService = Depends(_svc)) -> dict:
    contacts = svc.list_contacts()
    return {"count": len(contacts), "contacts": contacts}


@router.get("/contacts/search/")
def search_contacts(q: str = Query(...), svc: CitizenService = Depends(_svc)) -> dict:
    results = svc.search_contacts(q)
    return {"query": q, "count": len(results), "results": results}


@router.get("/contacts/{contact_id}")
def get_contact(contact_id: str, svc: CitizenService = Depends(_svc)) -> dict:
    contact = svc.get_contact(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail=f"Contact '{contact_id}' not found")
    return contact


@router.get("/rights")
def list_rights(category: str | None = Query(None), svc: CitizenService = Depends(_svc)) -> dict:
    rights = svc.list_rights(category)
    return {"count": len(rights), "rights": rights}


@router.get("/rights/search/")
def search_rights(
    q: str = Query(...),
    category: str | None = Query(None),
    svc: CitizenService = Depends(_svc),
) -> dict:
    results = svc.search_rights(q, category)
    return {"query": q, "count": len(results), "results": results}


@router.get("/faq")
def list_faq(svc: CitizenService = Depends(_svc)) -> dict:
    items = svc.list_faq()
    return {"count": len(items), "faq": items}


@router.get("/faq/search/")
def search_faq(q: str = Query(...), svc: CitizenService = Depends(_svc)) -> dict:
    results = svc.search_faq(q)
    return {"query": q, "count": len(results), "results": results}


@router.get("/categories")
def list_categories(svc: CitizenService = Depends(_svc)) -> dict:
    cats = svc.get_categories()
    return {"count": len(cats), "categories": cats}


@router.get("/stats")
def get_statistics(svc: CitizenService = Depends(_svc)) -> dict:
    return svc.get_statistics()
