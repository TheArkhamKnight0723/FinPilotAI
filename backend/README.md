# FinPilot AI – Backend

FastAPI-based backend service for the FinPilot AI financial intelligence platform.

## Tech Stack
- **Framework**: FastAPI 0.141+
- **Server**: Uvicorn (ASGI)
- **Validation**: Pydantic v2 + pydantic-settings
- **Language**: Python 3.14+

## Quick Start

```bash
# 1. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate       # Windows
source .venv/bin/activate    # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy and configure environment
cp .env.example .env

# 4. Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Key Endpoints
| Method | Path      | Description     |
|--------|-----------|-----------------|
| GET    | `/`       | API root info   |
| GET    | `/health` | Health check    |
| GET    | `/docs`   | Swagger UI      |
| GET    | `/redoc`  | ReDoc UI        |

## Architecture

```
backend/
├── app/
│   ├── api/v1/          # Versioned API routes
│   ├── auth/            # Authentication & JWT
│   ├── portfolio/       # Portfolio management
│   ├── market/          # Market data integration
│   ├── ai/              # AI agent services
│   ├── news/            # News aggregation
│   ├── notifications/   # Push notifications
│   ├── database/        # DB session & engine
│   ├── models/          # SQLAlchemy ORM models
│   ├── schemas/         # Pydantic request/response schemas
│   ├── services/        # Shared business services
│   ├── middleware/       # CORS, logging middleware
│   ├── core/            # Settings, logging config
│   ├── config/          # App configuration
│   ├── utils/           # Helper utilities
│   ├── exceptions/      # Custom exceptions & handlers
│   └── main.py          # Application entry point
└── tests/               # Test suites
```
