# Deploy to Render

This guide shows how to deploy the app on Render.

## 1. Prepare the backend

Create a new Web Service in Render and connect your GitHub repo.

Set:
- Build command: `pip install -r backend/requirements.txt`
- Start command: `gunicorn --bind 0.0.0.0:$PORT app:create_app() --chdir backend`

Environment variables:
```bash
FLASK_ENV=production
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@host:5432/dbname
CORS_ORIGINS=https://your-frontend-domain.onrender.com
```

## 2. Add PostgreSQL

Create a PostgreSQL database on Render and attach it to the service.

Use the connection string from Render in `DATABASE_URL`.

## 3. Deploy frontend

If using a separate frontend service:
- build command: `npm install && npm run build`
- publish directory: `frontend/dist`
- set environment or proxy to your backend URL

## 4. Health checks

Verify:
- `https://your-backend-url.onrender.com/api/health`

## 5. Final notes

- Use HTTPS
- Restrict CORS to your frontend domain
- Rotate environment secrets in production























