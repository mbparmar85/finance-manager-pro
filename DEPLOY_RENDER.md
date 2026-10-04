# Finance Manager

A modern personal finance management application with:
- multi-user authentication
- account and wallet tracking
- expense logging and category analysis
- monthly budget management
- loan tracking
- financial reporting and PDF export
- React + Bootstrap-inspired UI
- Flask backend with SQLite/PostgreSQL support
- Gunicorn-ready deployment setup

## Tech stack

- Frontend: React + Vite + Bootstrap + Chart.js
- Backend: Flask + Flask-Login + SQLAlchemy
- Database: SQLite for local development, PostgreSQL for production
- Deployment: Gunicorn + Docker optional

## Local setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open the UI at:
- http://localhost:5173

API will run at:
- http://localhost:5000

## Production deployment guides

- Render: `DEPLOY_RENDER.md`
- Railway: `DEPLOY_RAILWAY.md`
- VPS: `DEPLOY_VPS.md`

## Default user flow

1. Register a new account
2. Create one or more financial accounts
3. Add expenses and budgets
4. Track loans and payments
5. View monthly reports and export PDF

## Project structure

```text
finance-manager-pro/
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── models.py
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
├── DEPLOY_RENDER.md
├── DEPLOY_RAILWAY.md
├── DEPLOY_VPS.md
├── Dockerfile
├── docker-compose.yml
├── gunicorn.conf.py
├── README.md
├── .gitignore
└── .env
```

## Notes

- Local development uses SQLite by default.
- Production should use PostgreSQL for better performance and reliability.
- `gunicorn.conf.py` is included for deployment to modern hosting platforms.























