from datetime import date
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional

class RatingEntryCreate(BaseModel):
    employee_id: UUID
    metric_id: UUID
    period: date
    score: Decimal = Field(ge=0, le=10)
    category: str
    comment: Optional[str] = None

