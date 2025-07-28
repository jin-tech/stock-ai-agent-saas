import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_tables
from app.routers import alerts
from app.routers import news as news_router
from app.models import alert, news  # Import models to register them
from app.services.rss_service import rss_service

# Create database tables
create_tables()

# Initialize FastAPI app
app = FastAPI(
    title="Stock AI Agent SaaS - Alert API",
    description="FastAPI backend for stock alerts with PostgreSQL integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(alerts.router)
app.include_router(news_router.router)


# Background task for RSS feeds
async def rss_background_task():
    """Background task to fetch RSS news every 10 minutes"""
    while True:
        try:
            await rss_service.fetch_all_news()
        except Exception as e:
            print(f"Error in RSS background task: {e}")
        
        # Wait 10 minutes (600 seconds) before next fetch
        await asyncio.sleep(600)


@app.on_event("startup")
async def startup_event():
    """Start background tasks when the app starts"""
    # Start the RSS background task
    asyncio.create_task(rss_background_task())


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Stock AI Agent SaaS - Alert API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)