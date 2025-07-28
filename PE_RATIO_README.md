# PE Ratio Implementation

This implementation provides PE (Price-to-Earnings) ratio calculation and display functionality for the Stock AI Agent SaaS platform.

## Features

### Backend (FastAPI)
- **PE Ratio API**: RESTful endpoints to fetch PE ratios for individual stocks or in batches
- **Data Source Integration**: Uses Alpha Vantage API for real-time financial data
- **Caching System**: In-memory caching to reduce API calls and improve performance
- **Error Handling**: Comprehensive error handling for API failures and invalid symbols
- **CORS Support**: Configured for frontend integration

### Frontend (Next.js)
- **PE Ratio Dashboard**: Interactive dashboard displaying PE ratios for multiple stocks
- **Stock Search**: Search functionality to add new stocks to the dashboard
- **Responsive Design**: Mobile-friendly interface using Tailwind CSS
- **Real-time Updates**: Ability to refresh stock data on demand
- **Visual Indicators**: Color-coded PE ratios to indicate potential valuation levels

## API Endpoints

### GET /pe-ratio/{symbol}
Fetch PE ratio for a specific stock symbol.

**Response:**
```json
{
  "symbol": "AAPL",
  "pe_ratio": 28.5,
  "price": 175.43,
  "earnings_per_share": 6.15,
  "last_updated": "2024-01-15T10:30:00",
  "data_source": "Alpha Vantage"
}
```

### GET /stock-info/{symbol}
Fetch comprehensive stock information including PE ratio.

**Response:**
```json
{
  "symbol": "AAPL",
  "company_name": "Apple Inc.",
  "pe_ratio": 28.5,
  "price": 175.43,
  "earnings_per_share": 6.15,
  "market_cap": "2750000000000",
  "last_updated": "2024-01-15T10:30:00"
}
```

### GET /pe-ratios/batch?symbols=AAPL,GOOGL,MSFT
Fetch PE ratios for multiple stocks (up to 10 symbols).

**Response:**
```json
{
  "symbols": [
    {
      "symbol": "AAPL",
      "company_name": "Apple Inc.",
      "pe_ratio": 28.5,
      // ... other fields
    }
  ]
}
```

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- Alpha Vantage API key (free at https://www.alphavantage.co/support/#api-key)

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env and add your Alpha Vantage API key
   ```

4. Run the backend:
   ```bash
   uvicorn main:app --reload
   ```

The backend will be available at http://localhost:8000

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the frontend:
   ```bash
   npm run dev
   ```

The frontend will be available at http://localhost:3000

### Docker Setup
Run both frontend and backend with Docker Compose:

```bash
# Set your Alpha Vantage API key
export ALPHA_VANTAGE_API_KEY=your_api_key_here

# Start all services
docker-compose up --build
```

## Usage

1. **Access the Dashboard**: Open http://localhost:3000 in your browser
2. **View Popular Stocks**: The dashboard loads PE ratios for popular stocks (AAPL, GOOGL, MSFT, etc.)
3. **Search for Stocks**: Use the search bar to add new stocks to the dashboard
4. **Interpret PE Ratios**:
   - Green (Low P/E < 15): Potentially undervalued
   - Blue (Moderate P/E 15-30): Reasonable valuation
   - Red (High P/E > 30): Potentially overvalued

## PE Ratio Analysis

The application provides automatic interpretation of PE ratios:

- **Low PE (< 15)**: May indicate an undervalued stock, but could also suggest underlying issues
- **Moderate PE (15-30)**: Generally considered a reasonable valuation range
- **High PE (> 30)**: May indicate overvaluation, but could be justified by high growth expectations

**Important Note**: PE ratios should always be compared within the same industry for meaningful analysis.

## Error Handling

The application handles various error scenarios:
- Invalid stock symbols
- API rate limiting
- Network connectivity issues
- Missing financial data

## Limitations

1. **Data Source**: Relies on Alpha Vantage API which has rate limits (5 requests/minute for free tier)
2. **Demo API Key**: The default "demo" key has limited functionality
3. **Cache Duration**: PE ratios are cached for 1 hour to reduce API calls
4. **Real-time Data**: Data may not be truly real-time due to API limitations

## Future Enhancements

1. **Database Storage**: Persist PE ratio data in PostgreSQL
2. **Multiple Data Sources**: Integrate additional financial data providers
3. **Advanced Analytics**: Add PE ratio trends and historical analysis
4. **User Accounts**: Allow users to save custom stock portfolios
5. **Alerts**: Notify users when PE ratios reach certain thresholds
6. **Industry Comparison**: Compare PE ratios within the same industry sector

## Architecture

```
Frontend (Next.js)  ←→  Backend (FastAPI)  ←→  Alpha Vantage API
      ↓                        ↓
  Dashboard UI           PE Ratio Service
  Stock Search           Caching Layer
  Data Display          Error Handling
```

The implementation follows a clean separation of concerns with the frontend handling user interaction and display, while the backend manages data fetching, caching, and API integration.