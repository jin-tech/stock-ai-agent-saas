from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Stock AI Agent API",
    description="API for Stock AI Agent SaaS platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Stock AI Agent API is running!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api/stocks")
async def get_stocks():
    return {"stocks": ["AAPL", "GOOGL", "MSFT", "TSLA"]}