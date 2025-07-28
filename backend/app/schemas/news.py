from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime


class NewsItemBase(BaseModel):
    """Base schema for NewsItem"""
    title: str = Field(..., min_length=1, max_length=500, description="News article title")
    description: Optional[str] = Field(None, description="News article description")
    link: str = Field(..., description="URL to the full news article")
    published_date: Optional[datetime] = Field(None, description="When the article was published")
    source: Optional[str] = Field(None, max_length=100, description="RSS feed source name")
    keywords_matched: Optional[str] = Field(None, description="Comma-separated matched keywords")
    is_relevant: bool = Field(True, description="Whether this news matches any alerts")


class NewsItemCreate(NewsItemBase):
    """Schema for creating a new news item"""
    pass


class NewsItemResponse(NewsItemBase):
    """Schema for news item response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class NewsItemListResponse(BaseModel):
    """Schema for list of news items response"""
    news_items: List[NewsItemResponse]
    total: int
    page: int = 1
    page_size: int = 10


class RSSFeedConfig(BaseModel):
    """Schema for RSS feed configuration"""
    name: str = Field(..., description="Feed name")
    url: str = Field(..., description="RSS feed URL")
    enabled: bool = Field(True, description="Whether this feed is active")