"""
app/modules/plans/schemas.py
"""
import uuid
from pydantic import Field
from app.shared.schemas.base import BaseSchema


class PlanCreate(BaseSchema):
    name: str = Field(..., min_length=2, max_length=100)
    duration_days: int = Field(..., gt=0)
    price: int = Field(..., ge=0, description="Prix en FCFA")
    is_active: bool = True
    description: str | None = Field(default=None, max_length=500)
    display_order: int = Field(default=0, ge=0)


class PlanUpdate(BaseSchema):
    name: str | None = Field(None, min_length=2, max_length=100)
    duration_days: int | None = Field(None, gt=0)
    price: int | None = Field(None, ge=0)
    is_active: bool | None = None
    description: str | None = None
    display_order: int | None = None


class PlanResponse(BaseSchema):
    id: uuid.UUID
    name: str
    duration_days: int
    price: int
    is_active: bool
    description: str | None = None
    display_order: int