# Sai Nursery API Backend

FastAPI backend service for Sai Nursery management system, including authentication, sugarcane nursery batch tracking, customer & sale workflows, payment tracking, geographic services, and reporting.

## Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL with SQLAlchemy (Async) & asyncpg
- **Migrations:** Alembic
- **Caching:** Redis
- **Authentication:** JWT (OAuth2 Password Bearer)
- **Validation:** Pydantic v2 & Pydantic Settings
- **Testing:** Pytest, pytest-asyncio, HTTPX

## Getting Started

### 1. Clone & Setup Virtual Environment

```bash
# Clone repository
git clone https://github.com/parth10498/sai-nursery-backend.git
cd sai-nursery-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy `.env.example` to `.env` and update credentials:

```bash
cp .env.example .env
```

### 3. Database Migrations

```bash
alembic upgrade head
```

### 4. Run Development Server

```bash
uvicorn app.main:app --reload --port 8000
```

The interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Running Tests

```bash
pytest
```
