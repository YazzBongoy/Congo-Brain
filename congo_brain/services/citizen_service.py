"""Citizen services — procedures, contacts, rights, FAQ."""

import json

from sqlalchemy.orm import Session

from congo_brain.models.citizen import FAQ, CitizenRight, Contact, Procedure


class CitizenService:
    def __init__(self, db: Session) -> None:
        self.db = db

    # -- Procedures --

    def list_procedures(self, category: str | None = None) -> list[dict]:
        q = self.db.query(Procedure)
        if category:
            q = q.filter(Procedure.category.ilike(f"%{category}%"))
        return [self._proc_to_dict(p) for p in q.all()]

    def get_procedure(self, code: str) -> dict | None:
        p = self.db.query(Procedure).filter(Procedure.code == code).first()
        return self._proc_to_dict(p) if p else None

    def search_procedures(self, query: str, category: str | None = None) -> list[dict]:
        q = self.db.query(Procedure).filter(
            Procedure.name.ilike(f"%{query}%")
            | Procedure.description.ilike(f"%{query}%")
            | Procedure.category.ilike(f"%{query}%")
        )
        if category:
            q = q.filter(Procedure.category.ilike(f"%{category}%"))
        return [self._proc_to_dict(p) for p in q.all()]

    # -- Contacts --

    def list_contacts(self) -> list[dict]:
        return [self._contact_to_dict(c) for c in self.db.query(Contact).all()]

    def get_contact(self, code: str) -> dict | None:
        c = self.db.query(Contact).filter(Contact.code == code).first()
        return self._contact_to_dict(c) if c else None

    def search_contacts(self, query: str) -> list[dict]:
        q = self.db.query(Contact).filter(
            Contact.institution.ilike(f"%{query}%") | Contact.services.ilike(f"%{query}%")
        )
        return [self._contact_to_dict(c) for c in q.all()]

    # -- Rights --

    def list_rights(self, category: str | None = None) -> list[dict]:
        q = self.db.query(CitizenRight)
        if category:
            q = q.filter(CitizenRight.category.ilike(f"%{category}%"))
        return [self._right_to_dict(r) for r in q.all()]

    def search_rights(self, query: str, category: str | None = None) -> list[dict]:
        q = self.db.query(CitizenRight).filter(
            CitizenRight.title.ilike(f"%{query}%") | CitizenRight.description.ilike(f"%{query}%")
        )
        if category:
            q = q.filter(CitizenRight.category.ilike(f"%{category}%"))
        return [self._right_to_dict(r) for r in q.all()]

    # -- FAQ --

    def list_faq(self) -> list[dict]:
        return [self._faq_to_dict(f) for f in self.db.query(FAQ).all()]

    def search_faq(self, query: str) -> list[dict]:
        q = self.db.query(FAQ).filter(
            FAQ.question.ilike(f"%{query}%") | FAQ.answer.ilike(f"%{query}%")
        )
        return [self._faq_to_dict(f) for f in q.all()]

    # -- Categories & Stats --

    def get_categories(self) -> list[str]:
        rows = self.db.query(Procedure.category).distinct().all()
        return sorted([r[0] for r in rows])

    def get_statistics(self) -> dict:
        return {
            "total_procedures": self.db.query(Procedure).count(),
            "total_contacts": self.db.query(Contact).count(),
            "total_rights": self.db.query(CitizenRight).count(),
            "total_faq": self.db.query(FAQ).count(),
            "categories": self.get_categories(),
        }

    # -- Helpers --

    @staticmethod
    def _proc_to_dict(p: Procedure) -> dict:
        return {
            "id": p.code,
            "name": p.name,
            "category": p.category,
            "description": p.description,
            "steps": json.loads(p.steps),
            "documents_required": json.loads(p.documents_required),
            "fees": p.fees,
            "processing_time": p.processing_time,
            "authority": p.authority,
        }

    @staticmethod
    def _contact_to_dict(c: Contact) -> dict:
        return {
            "id": c.code,
            "institution": c.institution,
            "address": c.address,
            "phone": c.phone,
            "email": c.email,
            "services": json.loads(c.services),
            "hours": c.hours,
        }

    @staticmethod
    def _right_to_dict(r: CitizenRight) -> dict:
        return {
            "id": r.code,
            "title": r.title,
            "article": r.article,
            "description": r.description,
            "category": r.category,
        }

    @staticmethod
    def _faq_to_dict(f: FAQ) -> dict:
        return {
            "id": f.code,
            "question": f.question,
            "answer": f.answer,
            "category": f.category,
        }
