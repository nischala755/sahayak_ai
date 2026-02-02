"""
============================================
SAHAYAK AI - API Router
============================================

📌 WHAT IS THIS FILE?
Combines all API v1 routers into a single router.
This is included in the main FastAPI app.

🎓 LEARNING POINT:
FastAPI uses routers to organize endpoints.
Each router handles a specific domain (auth, sos, dashboard).
The main router combines them all with a version prefix.
============================================
"""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.sos import router as sos_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.knowledge import router as knowledge_router


# Create the main API v1 router
api_router = APIRouter(prefix="/api/v1")

# Include all sub-routers
api_router.include_router(auth_router)
api_router.include_router(sos_router)
api_router.include_router(dashboard_router)
api_router.include_router(knowledge_router)

