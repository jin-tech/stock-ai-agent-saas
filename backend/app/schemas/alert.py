from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AlertBase(BaseModel):
    """Base schema for Alert"""
    symbol: str = Field(..., min_length=1, max_length=10, description="Stock symbol (e.g., AAPL)")
    alert_type: str = Field(..., min_length=1, max_length=50, description="Type of alert (price, volume, news)")
    condition: str = Field(..., min_length=1, max_length=20, description="Alert condition (above, below, equals)")
    threshold_value: Optional[float] = Field(None, description="Threshold value for the alert")
    message: Optional[str] = Field(None, description="Alert message or description")
    is_active: bool = Field(True, description="Whether the alert is active")


class AlertCreate(AlertBase):
    """Schema for creating a new alert"""
    pass


class AlertUpdate(BaseModel):
    """Schema for updating an existing alert"""
    symbol: Optional[str] = Field(None, min_length=1, max_length=10)
    alert_type: Optional[str] = Field(None, min_length=1, max_length=50)
    condition: Optional[str] = Field(None, min_length=1, max_length=20)
    threshold_value: Optional[float] = None
    message: Optional[str] = None
    is_active: Optional[bool] = None


class AlertResponse(AlertBase):
    """Schema for alert response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AlertListResponse(BaseModel):
    """Schema for list of alerts response"""
    alerts: list[AlertResponse]
    total: int
    page: int = 1
    page_size: int = 10