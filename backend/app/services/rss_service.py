import asyncio
import feedparser
import logging
from datetime import datetime, timezone
from typing import List, Set, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal
from app.models.alert import Alert
from app.models.news import NewsItem
from app.schemas.news import RSSFeedConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Default RSS feeds - in production this could come from database or config
DEFAULT_RSS_FEEDS = [
    RSSFeedConfig(name="Yahoo Finance", url="https://feeds.finance.yahoo.com/rss/2.0/headline", enabled=True),
    RSSFeedConfig(name="MarketWatch", url="https://feeds.marketwatch.com/marketwatch/marketpulse/", enabled=True),
    RSSFeedConfig(name="Reuters Business", url="https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best", enabled=True),
]


class RSSService:
    """Service for fetching and processing RSS feeds"""
    
    def __init__(self, feeds: List[RSSFeedConfig] = None):
        self.feeds = feeds or DEFAULT_RSS_FEEDS
        
    async def fetch_feed(self, feed_url: str) -> Dict:
        """Fetch a single RSS feed asynchronously"""
        try:
            # feedparser is synchronous, so we run it in executor
            loop = asyncio.get_event_loop()
            feed_data = await loop.run_in_executor(None, feedparser.parse, feed_url)
            return feed_data
        except Exception as e:
            logger.error(f"Error fetching feed {feed_url}: {e}")
            return {}
    
    def get_alert_keywords(self, db: Session) -> Set[str]:
        """Get all keywords from active alerts to filter news"""
        try:
            alerts = db.query(Alert).filter(Alert.is_active == True).all()
            keywords = set()
            
            for alert in alerts:
                # Add stock symbol
                if alert.symbol:
                    keywords.add(alert.symbol.upper())
                    
                # Add words from message (if contains useful keywords)
                if alert.message:
                    # Extract meaningful words (length > 3, exclude common words)
                    words = alert.message.lower().split()
                    for word in words:
                        if len(word) > 3 and word not in ['alert', 'price', 'above', 'below', 'when', 'stock']:
                            keywords.add(word.upper())
            
            logger.info(f"Found {len(keywords)} keywords from {len(alerts)} alerts")
            return keywords
            
        except Exception as e:
            logger.error(f"Error getting alert keywords: {e}")
            return set()
    
    def matches_keywords(self, title: str, description: str, keywords: Set[str]) -> List[str]:
        """Check if news item matches any keywords and return matched ones"""
        if not keywords:
            return []
            
        text = f"{title} {description or ''}".upper()
        matched = []
        
        for keyword in keywords:
            if keyword in text:
                matched.append(keyword)
                
        return matched
    
    def parse_published_date(self, entry) -> Optional[datetime]:
        """Parse published date from RSS entry"""
        try:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                # Convert time.struct_time to datetime
                import time
                timestamp = time.mktime(entry.published_parsed)
                return datetime.fromtimestamp(timestamp, tz=timezone.utc)
            elif hasattr(entry, 'published'):
                # Try to parse string date
                from email.utils import parsedate_to_datetime
                return parsedate_to_datetime(entry.published)
        except Exception as e:
            logger.warning(f"Could not parse date: {e}")
        
        return None
    
    async def process_feed(self, feed: RSSFeedConfig, db: Session) -> int:
        """Process a single RSS feed and store relevant news items"""
        if not feed.enabled:
            return 0
            
        logger.info(f"Processing feed: {feed.name}")
        
        # Fetch feed data
        feed_data = await self.fetch_feed(feed.url)
        if not feed_data or not hasattr(feed_data, 'entries'):
            logger.warning(f"No data or entries found for feed: {feed.name}")
            return 0
        
        # Get current keywords from alerts
        keywords = self.get_alert_keywords(db)
        if not keywords:
            logger.info("No active alert keywords found, skipping news processing")
            return 0
        
        processed_count = 0
        
        for entry in feed_data.entries:
            try:
                # Extract basic information
                title = getattr(entry, 'title', '').strip()
                description = getattr(entry, 'description', '') or getattr(entry, 'summary', '')
                link = getattr(entry, 'link', '').strip()
                
                if not title or not link:
                    continue
                
                # Check if we already have this news item
                existing = db.query(NewsItem).filter(NewsItem.link == link).first()
                if existing:
                    continue
                
                # Check if this news matches any keywords
                matched_keywords = self.matches_keywords(title, description, keywords)
                
                # Only store news that matches at least one keyword
                if matched_keywords:
                    published_date = self.parse_published_date(entry)
                    
                    news_item = NewsItem(
                        title=title[:500],  # Truncate if too long
                        description=description[:2000] if description else None,  # Limit description length
                        link=link[:500],  # Truncate if too long
                        published_date=published_date,
                        source=feed.name,
                        keywords_matched=','.join(matched_keywords),
                        is_relevant=True
                    )
                    
                    db.add(news_item)
                    processed_count += 1
                    logger.info(f"Added news: {title[:100]}... (matched: {matched_keywords})")
                
            except IntegrityError:
                # Duplicate link, skip
                db.rollback()
                continue
            except Exception as e:
                logger.error(f"Error processing entry: {e}")
                db.rollback()
                continue
        
        try:
            db.commit()
            logger.info(f"Successfully processed {processed_count} news items from {feed.name}")
        except Exception as e:
            logger.error(f"Error committing news items: {e}")
            db.rollback()
            processed_count = 0
        
        return processed_count
    
    async def fetch_all_news(self) -> int:
        """Fetch news from all configured RSS feeds"""
        logger.info("Starting RSS news fetch process")
        total_processed = 0
        
        db = SessionLocal()
        try:
            for feed in self.feeds:
                count = await self.process_feed(feed, db)
                total_processed += count
                
            logger.info(f"RSS fetch complete. Total items processed: {total_processed}")
            return total_processed
            
        except Exception as e:
            logger.error(f"Error in fetch_all_news: {e}")
            return 0
        finally:
            db.close()


# Global RSS service instance
rss_service = RSSService()