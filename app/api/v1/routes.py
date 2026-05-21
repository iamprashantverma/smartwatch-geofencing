from fastapi import APIRouter

from app.api.v1.routes.ingest import router as ingest_router
from app.api.v1.routes.events import router as events_router

router = APIRouter()

router.include_router(ingest_router, prefix="/ingest")
router.include_router(events_router, prefix="/events")