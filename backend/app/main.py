from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_tables
from app.routers import alerts
from app.models import alert  # Import models to register them

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