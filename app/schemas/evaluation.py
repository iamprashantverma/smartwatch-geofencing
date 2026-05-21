from pydantic import BaseModel
from datetime import datetime
from app.core.constants import Severity, Status


class EvaluationResultSchema(BaseModel):
    event: str
    severity: Severity
    status: Status
    reason: str
    timestamp: datetime