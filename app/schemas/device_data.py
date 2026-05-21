from pydantic import BaseModel, Field
from datetime import datetime


class LocationSchema(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="Latitude must be between -90 and 90")
    lng: float = Field(..., ge=-180, le=180, description="Longitude must be between -180 and 180")


class DeviceDataSchema(BaseModel):
    device_id: str = Field(..., min_length=3, max_length=50)
    heart_rate: int = Field(..., ge=30, le=220, description="Valid human heart rate range")
    steps: int = Field(..., ge=0, description="Steps cannot be negative")
    location: LocationSchema
    timestamp: datetime
    event_type: str | None = Field(None, description="Event type: ENTRY, EXIT, STAY, or None")