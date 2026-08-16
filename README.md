# VORTIX AI Restaurant

AI-powered restaurant business intelligence and decision-support platform.

> This project currently uses synthetic/demo restaurant data and does not contain real Foodics restaurant data. Foodics integration will be implemented in a later phase.

## Tech Stack

- Python 3.12
- Django 5.2 LTS + Django REST Framework
- PostgreSQL 16
- Redis 7
- Celery (worker + beat)
- django-cors-headers
- Gunicorn
- Docker / Docker Compose

## Project Structure

```text
VORTIX-AI-RESTAURANT/
├── .gitignore
├── README.md
└── backend/
    ├── .env
    ├── .env.example
    ├── docker-compose.yml
    ├── Dockerfile
    ├── manage.py
    ├── requirements.txt
    ├── config/
    │   ├── settings/
    │   │   ├── base.py
    │   │   ├── development.py
    │   │   └── production.py
    │   ├── urls.py
    │   ├── celery.py
    │   ├── asgi.py
    │   └── wsgi.py
    ├── apps/
    │   └── core/          # shared/core app, no business models yet
    └── api/
        └── v1/
            └── health/    # GET /api/v1/health/
```

## Regional Configuration

The target restaurant operates in the UAE. Locale/timezone/currency are centralized in `config/settings/base.py`, not hard-coded across the app:

- `TIME_ZONE = "Asia/Dubai"`
- `LANGUAGE_CODE = "en-us"`
- `DEFAULT_CURRENCY = "AED"` (via `DEFAULT_CURRENCY` env var)

## Environment Setup

Copy the example env file and adjust values as needed:

```bash
cd backend
cp .env.example .env
```

`.env` is for local development only and is git-ignored. `.env.example` contains placeholders only.

## Running the Backend

```bash
cd backend
docker compose up --build
```

This starts:

- `backend` — Django API (http://localhost:8000)
- `db` — PostgreSQL
- `redis` — Redis (Celery broker/result backend, future cache)
- `celery` — Celery worker
- `celery-beat` — Celery beat scheduler

Database migrations run automatically on backend startup. To run them manually:

```bash
docker compose exec backend python manage.py migrate
```

Check service status:

```bash
docker compose ps
```

## Health Endpoint

```text
GET http://localhost:8000/api/v1/health/
```

```json
{
  "status": "ok",
  "service": "vortix-backend"
}
```

## Current Phase

**Phase 1 — Backend foundation.** Django + DRF + PostgreSQL + Redis + Celery running cleanly in Docker, with a working health endpoint. No business models, authentication, AI, or Foodics integration yet.

## Future Phases

- Phase 2: Core business models (branches, products, orders) and admin
- Phase 3: Authentication & RBAC
- Phase 4: Analytics endpoints (sales, AOV, growth, branch performance, best sellers)
- Phase 5: Synthetic/demo data generation
- Phase 6: AI Copilot (LLM-backed Q&A over restaurant data)
- Phase 7: Foodics POS integration
