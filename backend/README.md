# Stock AI Agent SaaS - Backend

FastAPI backend service for the Stock AI Agent SaaS platform with alert management functionality.

## Features

- **Alert API**: Create, read, update, and delete stock alerts
- **PostgreSQL Integration**: Persistent storage with SQLAlchemy ORM
- **Data Validation**: Pydantic models for request/response validation
- **Auto Documentation**: Swagger UI at `/docs` and ReDoc at `/redoc`
- **CORS Support**: Configured for frontend integration

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your database configuration
   ```

3. **Run the server**:
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Access the API**:
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## API Endpoints

### Alerts

- `POST /api/alerts` - Create a new alert
- `GET /api/alerts` - List alerts with optional filtering
- `GET /api/alerts/{id}` - Get specific alert
- `PUT /api/alerts/{id}` - Update alert
- `DELETE /api/alerts/{id}` - Delete alert

## Database Schema

### Alert Model

- `id` (int): Primary key
- `symbol` (str): Stock symbol (e.g., AAPL)
- `alert_type` (str): Type of alert (price, volume, news)
- `condition` (str): Alert condition (above, below, equals)
- `threshold_value` (float): Threshold value for the alert
- `message` (str): Alert description
- `is_active` (bool): Whether the alert is active
- `created_at` (datetime): Creation timestamp
- `updated_at` (datetime): Last update timestamp

## Development

The backend is structured as follows:

```
app/
├── main.py              # FastAPI application entry point
├── database.py          # Database configuration
├── models/
│   └── alert.py         # SQLAlchemy models
├── schemas/
│   └── alert.py         # Pydantic schemas
└── routers/
    └── alerts.py        # API endpoints
```