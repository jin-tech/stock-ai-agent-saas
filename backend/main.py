from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio
from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Stock AI Agent - PE Ratio API", version="1.0.0")

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class PERatioResponse(BaseModel):
    symbol: str
    pe_ratio: Optional[float]
    price: Optional[float]
    earnings_per_share: Optional[float]
    last_updated: datetime
    data_source: str

class StockInfoResponse(BaseModel):
    symbol: str
    company_name: Optional[str]
    pe_ratio: Optional[float]
    price: Optional[float]
    earnings_per_share: Optional[float]
    market_cap: Optional[str]
    last_updated: datetime
    error: Optional[str] = None

# In-memory cache for demo purposes (in production, use Redis)
pe_ratio_cache = {}
CACHE_EXPIRY = 3600  # 1 hour in seconds

class PERatioService:
    def __init__(self):
        self.api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")
        self.base_url = "https://www.alphavantage.co/query"
        
    async def get_company_overview(self, symbol: str) -> Dict[str, Any]:
        """Fetch company overview data from Alpha Vantage API"""
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "function": "OVERVIEW",
                    "symbol": symbol,
                    "apikey": self.api_key
                }
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                # Handle API errors
                if "Error Message" in data:
                    raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
                
                if "Note" in data:
                    raise HTTPException(status_code=429, detail="API rate limit exceeded")
                
                return data
        except httpx.HTTPError as e:
            raise HTTPException(status_code=503, detail=f"External API error: {str(e)}")

    async def get_pe_ratio(self, symbol: str) -> PERatioResponse:
        """Get PE ratio for a stock symbol"""
        # Check cache first
        cache_key = f"{symbol.upper()}_pe"
        if cache_key in pe_ratio_cache:
            cached_data, timestamp = pe_ratio_cache[cache_key]
            if datetime.now().timestamp() - timestamp < CACHE_EXPIRY:
                return cached_data
        
        # Fetch fresh data
        try:
            overview_data = await self.get_company_overview(symbol.upper())
            
            # Extract PE ratio and related data
            pe_ratio = overview_data.get("PERatio", "None")
            pe_ratio = float(pe_ratio) if pe_ratio != "None" and pe_ratio != "-" else None
            
            # Extract other financial data
            price = overview_data.get("AnalystTargetPrice", "None")
            price = float(price) if price != "None" and price != "-" else None
            
            eps = overview_data.get("EPS", "None")
            eps = float(eps) if eps != "None" and eps != "-" else None
            
            response = PERatioResponse(
                symbol=symbol.upper(),
                pe_ratio=pe_ratio,
                price=price,
                earnings_per_share=eps,
                last_updated=datetime.now(),
                data_source="Alpha Vantage"
            )
            
            # Cache the result
            pe_ratio_cache[cache_key] = (response, datetime.now().timestamp())
            
            return response
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Error fetching PE ratio: {str(e)}")

    async def get_stock_info(self, symbol: str) -> StockInfoResponse:
        """Get comprehensive stock information including PE ratio"""
        try:
            overview_data = await self.get_company_overview(symbol.upper())
            
            # Extract all relevant data
            pe_ratio = overview_data.get("PERatio", "None")
            pe_ratio = float(pe_ratio) if pe_ratio != "None" and pe_ratio != "-" else None
            
            price = overview_data.get("AnalystTargetPrice", "None")
            price = float(price) if price != "None" and price != "-" else None
            
            eps = overview_data.get("EPS", "None")
            eps = float(eps) if eps != "None" and eps != "-" else None
            
            market_cap = overview_data.get("MarketCapitalization", "N/A")
            company_name = overview_data.get("Name", "Unknown")
            
            return StockInfoResponse(
                symbol=symbol.upper(),
                company_name=company_name,
                pe_ratio=pe_ratio,
                price=price,
                earnings_per_share=eps,
                market_cap=market_cap,
                last_updated=datetime.now()
            )
            
        except Exception as e:
            error_message = str(e)
            if isinstance(e, HTTPException):
                error_message = e.detail
            
            return StockInfoResponse(
                symbol=symbol.upper(),
                company_name=None,
                pe_ratio=None,
                price=None,
                earnings_per_share=None,
                market_cap=None,
                last_updated=datetime.now(),
                error=error_message
            )

# Initialize service
pe_service = PERatioService()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Stock AI Agent - PE Ratio API", "status": "running"}

@app.get("/pe-ratio/{symbol}", response_model=PERatioResponse)
async def get_pe_ratio(symbol: str):
    """Get PE ratio for a specific stock symbol"""
    return await pe_service.get_pe_ratio(symbol)

@app.get("/stock-info/{symbol}", response_model=StockInfoResponse)
async def get_stock_info(symbol: str):
    """Get comprehensive stock information including PE ratio"""
    return await pe_service.get_stock_info(symbol)

@app.get("/pe-ratios/batch")
async def get_multiple_pe_ratios(symbols: str):
    """Get PE ratios for multiple stock symbols (comma-separated)"""
    symbol_list = [s.strip().upper() for s in symbols.split(",")]
    
    if len(symbol_list) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 symbols allowed per request")
    
    results = []
    tasks = [pe_service.get_stock_info(symbol) for symbol in symbol_list]
    
    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error responses
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(StockInfoResponse(
                    symbol=symbol_list[i],
                    company_name=None,
                    pe_ratio=None,
                    price=None,
                    earnings_per_share=None,
                    market_cap=None,
                    last_updated=datetime.now(),
                    error=str(result)
                ))
            else:
                processed_results.append(result)
        
        return {"symbols": processed_results}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing batch request: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)