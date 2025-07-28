from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base


class NewsItem(Base):
    __tablename__ = "news_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text)
    link = Column(String(500), nullable=False, unique=True)  # RSS link should be unique
    published_date = Column(DateTime)
    source = Column(String(100))  # RSS feed source name
    keywords_matched = Column(Text)  # Store comma-separated matched keywords
    is_relevant = Column(Boolean, default=True)  # Whether this news matches any alerts
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<NewsItem(id={self.id}, title='{self.title[:50]}...', source={self.source})>"