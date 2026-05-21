from fastapi import APIRouter

from app.api.v1.routes.ingest import router as ingest_router
from app.api.v1.routes.devices import router as devices_router

router = APIRouter()

router.include_router(ingest_router, prefix="/ingest")
router.include_router(devices_router, prefix="/devices")
