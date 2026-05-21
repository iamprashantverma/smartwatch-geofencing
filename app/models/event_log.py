from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func

from app.db.base import Base

class EventLog(Base):
    __tablename__ = "event_logs"

    id = Column(Integer, primary_key=True, index=True)

    device_id = Column(String, nullable=False)

    event_type = Column(String, nullable=False)

    severity = Column(String, nullable=True)

    status = Column(String, nullable=True)

    zone = Column(String, nullable=True)

    reason = Column(String, nullable=True)

    heart_rate = Column(Integer, nullable=True)

    latitude = Column(Float, nullable=True)

    longitude = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())