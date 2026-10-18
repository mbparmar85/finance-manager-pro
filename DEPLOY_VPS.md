# Deploy to a VPS

This guide covers Ubuntu 24.04 / Debian 12 with Nginx, Gunicorn under systemd,
and PostgreSQL. Nginx serves the built React app and proxies `/api` to
Gunicorn, so both are on one domain (required by the `SameSite=Lax` login
cookie). Point DNS for your domain at the server before step 7.

## 1. Install system packages

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv nginx postgresql git nodejs npm certbot python3-certbot-nginx
```

Vite 5 needs Node 18 or newer (`node -v`).

## 2. Create the app user and clone

```bash
sudo useradd -m -s /bin/bash financeapp
sudo -u financeapp git clone https://github.com/your-user/finance-manager-pro.git /home/financeapp/finance-manager-pro
```

## 3. Create the database

Make the app user the database owner. On PostgreSQL 15+,
`GRANT ALL PRIVILEGES ON DATABASE` is not enough to create tables.

```bash
sudo -u postgres psql <<'SQL'
CREATE USER financeuser WITH PASSWORD 'change-this-password';
CREATE DATABASE finance_db OWNER financeuser;
SQL
```

## 4. Python environment and settings

```bash
sudo -iu financeapp
cd ~/finance-manager-pro/backend
python3 -m venv venv
venv/bin/pip install -r requirements.txt
cp .env.example .env && chmod 600 .env
```

Edit `backend/.env`:
```bash
FLASK_ENV=production
SECRET_KEY=<python3 -c "import secrets; print(secrets.token_hex(32))">
DATABASE_URL=postgresql://financeuser:change-this-password@localhost:5432/finance_db
CORS_ORIGINS=https://your-domain.com
```

## 5. Run Gunicorn under systemd

`/etc/systemd/system/finance.service`:
```ini
[Unit]
Description=Finance Manager API
After=network.target postgresql.service

[Service]
User=financeapp
WorkingDirectory=/home/financeapp/finance-manager-pro/backend
EnvironmentFile=/home/financeapp/finance-manager-pro/backend/.env
ExecStart=/home/financeapp/finance-manager-pro/backend/venv/bin/gunicorn --config /home/financeapp/finance-manager-pro/gunicorn.conf.py --bind 127.0.0.1:8000 app:create_app()
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now finance
curl -s http://127.0.0.1:8000/api/health
```

Gunicorn binds to `127.0.0.1` so port 8000 is not exposed publicly.

## 6. Build the frontend

Nginx cannot read `/home/financeapp` on current Ubuntu, so copy the build to `/var/www`.

```bash
cd /home/financeapp/finance-manager-pro/frontend
sudo -u financeapp npm ci
sudo -u financeapp npm run build
sudo mkdir -p /var/www/finance
sudo cp -r dist/. /var/www/finance/
```

## 7. Configure Nginx and HTTPS

`/etc/nginx/sites-available/finance`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /var/www/finance;
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }

    location / {
        try_files $uri /index.html;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/finance /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d your-domain.com
```

## 8. Verify

```bash
curl -s https://your-domain.com/api/health
# {"status": "ok", "timestamp": "..."}
```

- Register, reload the page, and confirm you are still logged in.
- Open a report and export the PDF.
- Errors: `journalctl -u finance -n 50`.
