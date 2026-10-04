# Personal Finance Manager

A full-stack personal finance application with:
- Multi-user login and registration
- Accounts with USD/EUR support
- Expense tracking and categorization
- Monthly budgets
- Loan management
- Transaction history
- Monthly reports
- PDF export support
- React frontend + Bootstrap
- Flask backend + SQLAlchemy + PostgreSQL-ready config
- Gunicorn deployment setup

## Tech stack

- Frontend: React + Bootstrap + Vite
- Backend: Flask + Flask-Login + Flask-SQLAlchemy + Flask-CORS
- Database: PostgreSQL (production) / SQLite (local dev fallback)
- Deployment: Gunicorn

## Project structure

- `backend/` — Flask API
- `frontend/` — React UI
- `docker-compose.yml` — PostgreSQL + app container setup
- `Dockerfile` — container image for backend
- `gunicorn.conf.py` — Gunicorn configuration
- `.gitignore`

## Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

## Production deployment

```bash
docker compose up --build
```

## Default development URLs

- Frontend: http://localhost:5173
- Backend: http://localhost:5000

## Environment variables

See `backend/.env.example` for configuration.
