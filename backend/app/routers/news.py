from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.database import get_db
from app.models.news import NewsItem
from app.schemas.news import NewsItemResponse, NewsItemListResponse
from app.services.rss_service import rss_service

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/", response_model=NewsItemListResponse)
async def get_news(
    skip: int = 0,
    limit: int = 20,
    source: str = None,
    keywords: str = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve news items with optional filtering.
    
    - **skip**: Number of items to skip (pagination)
    - **limit**: Maximum number of items to return  
    - **source**: Filter by news source
    - **keywords**: Filter by keywords (comma-separated)
    """
    query = db.query(NewsItem).filter(NewsItem.is_relevant == True)
    
    # Apply filters
    if source:
        query = query.filter(NewsItem.source.ilike(f"%{source}%"))
    
    if keywords:
        # Split keywords and check if any are present in keywords_matched
        keyword_list = [k.strip().upper() for k in keywords.split(',')]
        for keyword in keyword_list:
            query = query.filter(NewsItem.keywords_matched.ilike(f"%{keyword}%"))
    
    # Get total count
    total = query.count()
    
    # Apply pagination and ordering (newest first)
    news_items = query.order_by(NewsItem.created_at.desc()).offset(skip).limit(limit).all()
    
    return NewsItemListResponse(
        news_items=news_items,
        total=total,
        page=(skip // limit) + 1 if limit > 0 else 1,
        page_size=limit
    )


@router.get("/{news_id}", response_model=NewsItemResponse)
async def get_news_item(news_id: int, db: Session = Depends(get_db)):
    """
    Get a specific news item by ID.
    """
    news_item = db.query(NewsItem).filter(NewsItem.id == news_id).first()
    if not news_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News item not found"
        )
    return news_item


@router.post("/fetch", status_code=status.HTTP_202_ACCEPTED)
async def trigger_news_fetch(background_tasks: BackgroundTasks):
    """
    Manually trigger RSS news fetch process.
    This runs as a background task and returns immediately.
    """
    background_tasks.add_task(rss_service.fetch_all_news)
    return {"message": "News fetch triggered successfully"}


@router.get("/sources/list")
async def get_news_sources(db: Session = Depends(get_db)):
    """
    Get list of available news sources with counts.
    """
    # Get distinct sources with counts
    sources = db.query(
        NewsItem.source, 
        func.count(NewsItem.id).label('count')
    ).filter(
        NewsItem.is_relevant == True
    ).group_by(NewsItem.source).all()
    
    return {
        "sources": [
            {"name": source, "count": count} 
            for source, count in sources
        ]
    }


@router.delete("/{news_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_news_item(news_id: int, db: Session = Depends(get_db)):
    """
    Delete a news item (or mark as not relevant).
    """
    news_item = db.query(NewsItem).filter(NewsItem.id == news_id).first()
    if not news_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News item not found"
        )
    
    # Instead of deleting, mark as not relevant
    news_item.is_relevant = False
    db.commit()
    return None