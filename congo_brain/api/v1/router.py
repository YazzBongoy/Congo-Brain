"""Main v1 API router — assembles all sub-routers."""

from fastapi import APIRouter

from congo_brain.api.v1.auth import router as auth_router
from congo_brain.api.v1.budget import router as budget_router
from congo_brain.api.v1.citizen import router as citizen_router
from congo_brain.api.v1.economic import router as economic_router
from congo_brain.api.v1.geos import router as geos_router
from congo_brain.api.v1.ia_gov import router as ia_gov_router
from congo_brain.api.v1.investment import router as investment_router
from congo_brain.api.v1.security import router as security_router
from congo_brain.api.v1.transparency import router as transparency_router

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(auth_router)
v1_router.include_router(citizen_router)
v1_router.include_router(budget_router)
v1_router.include_router(economic_router)
v1_router.include_router(geos_router)
v1_router.include_router(ia_gov_router)
v1_router.include_router(investment_router)
v1_router.include_router(transparency_router)
v1_router.include_router(security_router)
