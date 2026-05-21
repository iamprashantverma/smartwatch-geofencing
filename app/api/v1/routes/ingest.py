from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.device_data import DeviceDataSchema
from app.services.ingestion_service import ingest_device_data

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def ingest_device(payload: DeviceDataSchema, db: Session = Depends(get_db)) -> dict:

    return await ingest_device_data(payload, db)
