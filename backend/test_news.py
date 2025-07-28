import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock
from datetime import datetime

# Import models to ensure they're registered with Base metadata
from app.models.alert import Alert
from app.models.news import NewsItem  
from app.main import app
from app.database import get_db, Base
from app.services.rss_service import RSSService, RSSFeedConfig


def get_test_db():
    """Set up test database"""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables - make sure all models are loaded first
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    return TestingSessionLocal


class TestRSSService:
    """Test RSS service functionality"""
    
    def test_get_alert_keywords(self):
        """Test extracting keywords from alerts"""
        TestingSessionLocal = get_test_db()
        db = TestingSessionLocal()
        
        # Create test alerts
        alert1 = Alert(
            symbol="AAPL",
            alert_type="price",
            condition="above",
            threshold_value=150.0,
            message="Apple stock price alert",
            is_active=True
        )
        alert2 = Alert(
            symbol="TSLA",
            alert_type="news",
            condition="contains",
            message="Tesla earnings report",
            is_active=True
        )
        alert3 = Alert(
            symbol="GOOGL",
            alert_type="price",
            condition="below",
            threshold_value=100.0,
            message="Google price alert",
            is_active=False  # Inactive alert should be ignored
        )
        
        db.add_all([alert1, alert2, alert3])
        db.commit()
        
        rss_service = RSSService()
        keywords = rss_service.get_alert_keywords(db)
        
        # Should contain stock symbols and meaningful words from messages
        expected_keywords = {"AAPL", "TSLA", "APPLE", "TESLA", "EARNINGS", "REPORT"}
        assert "AAPL" in keywords
        assert "TSLA" in keywords
        assert "GOOGL" not in keywords  # Inactive alert
        assert "APPLE" in keywords
        assert "TESLA" in keywords
        
        db.close()
        app.dependency_overrides.clear()
    
    def test_matches_keywords(self):
        """Test keyword matching functionality"""
        rss_service = RSSService()
        keywords = {"AAPL", "TESLA", "EARNINGS"}
        
        # Test positive matches
        matches = rss_service.matches_keywords(
            "Apple Inc. reports strong earnings", 
            "AAPL stock rises after earnings report",
            keywords
        )
        assert "AAPL" in matches
        assert "EARNINGS" in matches
        
        # Test no matches
        matches = rss_service.matches_keywords(
            "Microsoft announces new product",
            "MSFT stock unchanged",
            keywords
        )
        assert len(matches) == 0
        
        # Test case insensitive matching
        matches = rss_service.matches_keywords(
            "tesla autopilot update",
            "Tesla stock news",
            keywords
        )
        assert "TESLA" in matches
    
    @pytest.mark.asyncio
    @patch('app.services.rss_service.feedparser.parse')
    async def test_process_feed(self, mock_feedparser):
        """Test processing a single RSS feed"""
        TestingSessionLocal = get_test_db()
        db = TestingSessionLocal()
        
        # Create test alert for keyword matching
        alert = Alert(
            symbol="AAPL",
            alert_type="news",
            condition="contains",
            message="Apple news alert",
            is_active=True
        )
        db.add(alert)
        db.commit()
        
        # Mock RSS feed data
        mock_feed = MagicMock()
        mock_feed.entries = [
            MagicMock(
                title="Apple Reports Strong Q4 Earnings",
                description="AAPL stock rises after earnings beat",
                link="https://example.com/apple-earnings",
                published_parsed=None
            ),
            MagicMock(
                title="Microsoft Azure Growth",
                description="MSFT cloud revenue increases",
                link="https://example.com/microsoft-azure",
                published_parsed=None
            )
        ]
        mock_feedparser.return_value = mock_feed
        
        rss_service = RSSService()
        feed_config = RSSFeedConfig(
            name="Test Feed",
            url="https://example.com/feed.xml",
            enabled=True
        )
        
        count = await rss_service.process_feed(feed_config, db)
        
        # Should process 1 item (Apple news matches AAPL keyword)
        assert count == 1
        
        # Check that news item was saved
        news_items = db.query(NewsItem).all()
        assert len(news_items) == 1
        assert "Apple" in news_items[0].title
        assert "AAPL" in news_items[0].keywords_matched
        
        db.close()
        app.dependency_overrides.clear()


class TestNewsAPI:
    """Test news API endpoints"""
    
    def test_get_news_empty(self):
        """Test getting news when none exist"""
        TestingSessionLocal = get_test_db()
        client = TestClient(app)
        
        response = client.get("/api/news/")
        assert response.status_code == 200
        
        data = response.json()
        assert "news_items" in data
        assert "total" in data
        assert data["total"] == 0
        assert len(data["news_items"]) == 0
        
        app.dependency_overrides.clear()
    
    def test_get_news_with_items(self):
        """Test getting news when items exist"""
        TestingSessionLocal = get_test_db()
        db = TestingSessionLocal()
        
        # Create test news items
        news1 = NewsItem(
            title="Apple Earnings Report",
            description="AAPL reports strong earnings",
            link="https://example.com/apple-earnings",
            source="Test Source",
            keywords_matched="AAPL,EARNINGS",
            is_relevant=True
        )
        news2 = NewsItem(
            title="Tesla Production Update",
            description="TSLA increases production",
            link="https://example.com/tesla-production",
            source="Test Source",
            keywords_matched="TSLA,PRODUCTION",
            is_relevant=True
        )
        
        db.add_all([news1, news2])
        db.commit()
        
        client = TestClient(app)
        response = client.get("/api/news/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 2
        assert len(data["news_items"]) == 2
        
        # Check data structure
        news_item = data["news_items"][0]
        assert "id" in news_item
        assert "title" in news_item
        assert "keywords_matched" in news_item
        assert "created_at" in news_item
        
        db.close()
        app.dependency_overrides.clear()
    
    def test_get_news_with_filters(self):
        """Test news filtering by keywords and source"""
        TestingSessionLocal = get_test_db()
        db = TestingSessionLocal()
        
        # Create test news items
        news1 = NewsItem(
            title="Apple Earnings",
            link="https://example.com/1",
            source="Yahoo Finance",
            keywords_matched="AAPL",
            is_relevant=True
        )
        news2 = NewsItem(
            title="Tesla News",
            link="https://example.com/2",
            source="MarketWatch",
            keywords_matched="TSLA",
            is_relevant=True
        )
        
        db.add_all([news1, news2])
        db.commit()
        
        client = TestClient(app)
        
        # Test keyword filter
        response = client.get("/api/news/?keywords=AAPL")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert "Apple" in data["news_items"][0]["title"]
        
        # Test source filter
        response = client.get("/api/news/?source=Yahoo")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        
        db.close()
        app.dependency_overrides.clear()
    
    def test_get_news_item_by_id(self):
        """Test getting a specific news item"""
        TestingSessionLocal = get_test_db()
        db = TestingSessionLocal()
        
        news_item = NewsItem(
            title="Test News",
            link="https://example.com/test",
            source="Test Source",
            keywords_matched="TEST",
            is_relevant=True
        )
        db.add(news_item)
        db.commit()
        
        client = TestClient(app)
        response = client.get(f"/api/news/{news_item.id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Test News"
        assert data["id"] == news_item.id
        
        # Test non-existent ID
        response = client.get("/api/news/999")
        assert response.status_code == 404
        
        db.close()
        app.dependency_overrides.clear()
    
    def test_trigger_news_fetch(self):
        """Test manual news fetch trigger"""
        get_test_db()
        client = TestClient(app)
        
        response = client.post("/api/news/fetch")
        assert response.status_code == 202
        
        data = response.json()
        assert "message" in data
        assert "triggered" in data["message"].lower()
        
        app.dependency_overrides.clear()
    
    def test_get_news_sources(self):
        """Test getting news sources"""
        TestingSessionLocal = get_test_db()
        db = TestingSessionLocal()
        
        # Create news items from different sources
        news1 = NewsItem(
            title="News 1", link="https://example.com/1",
            source="Yahoo Finance", is_relevant=True
        )
        news2 = NewsItem(
            title="News 2", link="https://example.com/2",
            source="Yahoo Finance", is_relevant=True
        )
        news3 = NewsItem(
            title="News 3", link="https://example.com/3",
            source="MarketWatch", is_relevant=True
        )
        
        db.add_all([news1, news2, news3])
        db.commit()
        
        client = TestClient(app)
        response = client.get("/api/news/sources/list")
        assert response.status_code == 200
        
        data = response.json()
        assert "sources" in data
        assert len(data["sources"]) == 2
        
        # Check source counts
        sources = {s["name"]: s["count"] for s in data["sources"]}
        assert sources["Yahoo Finance"] == 2
        assert sources["MarketWatch"] == 1
        
        db.close()
        app.dependency_overrides.clear()


if __name__ == "__main__":
    pytest.main([__file__])