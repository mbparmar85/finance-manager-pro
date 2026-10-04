# Deploy to Railway

This guide shows how to deploy the application on Railway.

## 1. Create a project

Create a project in Railway and add your GitHub repository.

## 2. Backend service

Add a new service for the backend.

Use:
- root directory: `backend`
- build command: `pip install -r requirements.txt`
- start command: `gunicorn --bind 0.0.0.0:$PORT app:create_app()`

Set environment variables:
```bash
FLASK_ENV=production
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://postgres:password@host:port/dbname
CORS_ORIGINS=https://your-frontend-url.up.railway.app
```

## 3. Add PostgreSQL

Railway can provision a PostgreSQL service. Connect it to the backend service and use the generated URL.

## 4. Frontend service

Create a second service for the frontend.

Use:
- root directory: `frontend`
- build command: `npm install && npm run build`
- start command: `npm run dev -- --host 0.0.0.0`

For production static hosting, instead use a static output service or nginx configuration.

## 5. Verify deployment

Test:
- backend health: `/api/health`
- login/register flow
- report generation and PDF export

## 6. Production tweaks

- Set secure cookies and HTTPS headers
- Keep `SECRET_KEY` and `DATABASE_URL` in Railway environment variables
- Use a real PostgreSQL database instead of SQLite























