from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), nullable=False, index=True)  # Stock symbol (e.g., AAPL)
    alert_type = Column(String(50), nullable=False)  # price, volume, news, etc.
    condition = Column(String(20), nullable=False)  # above, below, equals
    threshold_value = Column(Float)  # Price or volume threshold
    message = Column(Text)  # Alert description/message
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Alert(id={self.id}, symbol={self.symbol}, type={self.alert_type})>"