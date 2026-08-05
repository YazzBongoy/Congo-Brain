"""Citizen-facing schemas."""

from pydantic import BaseModel


class ProcedureOut(BaseModel):
    id: int
    code: str
    name: str
    category: str
    description: str
    steps: list[str]
    documents_required: list[str]
    fees: str
    processing_time: str
    authority: str

    model_config = {"from_attributes": True}


class ContactOut(BaseModel):
    id: int
    code: str
    institution: str
    address: str
    phone: str
    email: str
    services: list[str]
    hours: str

    model_config = {"from_attributes": True}


class CitizenRightOut(BaseModel):
    id: int
    code: str
    title: str
    article: str
    description: str
    category: str

    model_config = {"from_attributes": True}


class FAQOut(BaseModel):
    id: int
    code: str
    question: str
    answer: str
    category: str

    model_config = {"from_attributes": True}
