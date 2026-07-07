# pydantic schema for data serialization and api req/resp validation 

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectOut(ProjectBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True


class ActivityBase(BaseModel):
    name: str
    scheduled_start: datetime
    scheduled_end: datetime
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    is_critical_path: bool = False
    status: str = "NOT_STARTED"


class ActivityOut(ActivityBase):
    id: int
    project_id: int
    class Config:
        from_attributes = True


class ActivityRelationCreate(BaseModel):
    predecessor_id: int
    successor_id: int
    relation_type: str = "FS"


class MaterialBase(BaseModel):
    sku: str
    description: Optional[str] = None
    quantity: float = 1.0
    status: str = "ORDERED"
    current_location: Optional[str] = None
    vendor_name: Optional[str] = None
    promised_delivery_date: datetime
    activity_id: Optional[int] = None


class MaterialOut(MaterialBase):
    id: int
    forecast_delivery_date: Optional[datetime] = None
    delay_probability: float
    confidence_score: float
    class Config:
        from_attributes = True


class SignalCreate(BaseModel):
    source: str
    raw_content: str
    parsed_status: Optional[str] = None
    confidence_weight: Optional[float] = 1.0


class AlertOut(BaseModel):
    id: int
    project_id: int
    material_id: Optional[int]
    message: str
    severity: str
    is_resolved: bool
    created_at: datetime
    class Config:
        from_attributes = True


class ActionOut(BaseModel):
    id: int
    alert_id: int
    action_type: str
    draft_content: str
    status: str
    created_at: datetime
    class Config:
        from_attributes = True
