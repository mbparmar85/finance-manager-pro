# Deploy to Render

This guide deploys the API as a Render Web Service, the React app as a Render
Static Site, and PostgreSQL as a Render database.

The frontend calls a relative `/api` path and the login cookie is
`SameSite=Lax`, so the browser must see the frontend and the API on the same
domain. The static site's rewrite rule in step 3 does that.

## 1. Create PostgreSQL

Dashboard → **New → Postgres**, in the same region you will use for the web
service. Copy its **Internal Database URL**.

If the URL starts with `postgres://`, change it to `postgresql://`
(SQLAlchemy rejects the short scheme).

## 2. Backend web service

Create a **Web Service** from this repo (Python runtime).

- Root directory: (blank)
- Build command: `pip install -r backend/requirements.txt`
- Start command:
  ```bash
  gunicorn --chdir backend --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120 'app:create_app()'
  ```
  Keep the quotes around `app:create_app()`; unquoted, the shell rejects the parentheses.
- Health check path: `/api/health`

Environment variables:
```bash
PYTHON_VERSION=3.11.9
FLASK_ENV=production
SECRET_KEY=<python3 -c "import secrets; print(secrets.token_hex(32))">
DATABASE_URL=<Internal Database URL from step 1>
CORS_ORIGINS=https://your-domain.com
```

## 3. Frontend static site

Create a **Static Site** from this repo.

- Root directory: `frontend`
- Build command: `npm install && npm run build`
- Publish directory: `dist`

Under **Redirects/Rewrites**, add these rules in this order:

| Source   | Destination                                   | Action  |
|----------|-----------------------------------------------|---------|
| `/api/*` | `https://<your-backend>.onrender.com/api/*`   | Rewrite |
| `/*`     | `/index.html`                                 | Rewrite |

Attach your custom domain to the static site, not to the backend.

## 4. Verify

```bash
curl -s https://your-domain.com/api/health
# {"status": "ok", "timestamp": "..."}
```

- If the health check returns HTML, the `/api/*` rule is below the `/*` rule.
- Register, reload the page, and confirm you are still logged in.
- Open a report and export the PDF.
