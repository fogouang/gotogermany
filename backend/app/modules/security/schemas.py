"""
app/modules/security/schemas.py
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class SecurityUserInfo(BaseModel):
    id: uuid.UUID
    full_name: str
    email: str | None = None
    phone: str | None = None
    is_active: bool
    is_blocked: bool


class SecurityIncidentResponse(BaseModel):
    id: uuid.UUID
    user: SecurityUserInfo
    rule: str
    severity: str
    action: str
    ip: str | None
    user_agent: str | None
    status: str
    created_at: datetime
    resolved_at: datetime | None = None
    resolution_note: str | None = None
    details: dict = {}


class SecuritySummaryResponse(BaseModel):
    open_incidents: int
    open_high: int
    blocked_users: int


class SecurityBlockResponse(BaseModel):
    user: SecurityUserInfo
    reason: str
    incident_id: uuid.UUID | None
    blocked_at: datetime


class ResolveIncidentRequest(BaseModel):
    note: str | None = Field(default=None, max_length=2000)