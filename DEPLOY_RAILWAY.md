# Deploy to Railway

This guide deploys the API, PostgreSQL, and a small Caddy service that serves
the built React app and proxies `/api` to the API.

The frontend calls a relative `/api` path and the login cookie is
`SameSite=Lax`, so the browser must see the frontend and the API on the same
domain. The Caddy service in step 3 does that.

## 1. Create the project and database

**New Project → Deploy from GitHub repo**, pick this repo, then
**+ New → Database → PostgreSQL** in the same project.

## 2. Backend service

- Root directory: `backend` (Python 3.11 is pinned by `backend/.python-version`)
- Custom start command:
  ```bash
  gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120 'app:create_app()'
  ```
  Keep the quotes around `app:create_app()`; unquoted, the shell rejects the parentheses.
- Healthcheck path: `/api/health`

Variables:
```bash
FLASK_ENV=production
SECRET_KEY=<python3 -c "import secrets; print(secrets.token_hex(32))">
DATABASE_URL=${{Postgres.DATABASE_URL}}
CORS_ORIGINS=https://your-domain.com
```

Under Networking, generate a public domain for this service. You need it in step 3.

## 3. Frontend service

Do not use `npm run dev` in production: it runs Vite's development server.
Instead, add these two files to `frontend/` and create a second service from
this repo with root directory `frontend`. Railway builds it from the Dockerfile.

`frontend/Dockerfile`:
```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM caddy:2-alpine
COPY Caddyfile /etc/caddy/Caddyfile
COPY --from=build /app/dist /srv
```

`frontend/Caddyfile`:
```
:{$PORT}

handle /api/* {
	reverse_proxy {$BACKEND_URL} {
		header_up Host {upstream_hostport}
	}
}

handle {
	root * /srv
	try_files {path} /index.html
	file_server
}
```

Frontend service variable:
```bash
BACKEND_URL=https://<backend-public-domain-from-step-2>
```

Attach your custom domain to the frontend service.

## 4. Verify

```bash
curl -s https://your-domain.com/api/health
# {"status": "ok", "timestamp": "..."}
```

- A 502 means `BACKEND_URL` is wrong or the backend is not healthy yet.
- Register, reload the page, and confirm you are still logged in.
- Open a report and export the PDF.
