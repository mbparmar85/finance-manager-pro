# Deploy to a VPS

This guide covers deployment on Ubuntu/Debian VPS with Nginx + Gunicorn + PostgreSQL.

## 1. Install system dependencies

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv nginx postgresql postgresql-contrib git
```

## 2. Create app user

```bash
sudo useradd -m -s /bin/bash financeapp
sudo su - financeapp
```

## 3. Clone repository

```bash
git clone https://github.com/your-user/finance-manager-pro.git
cd finance-manager-pro
```

## 4. Set up Python environment

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Update `.env` for production:
```bash
FLASK_ENV=production
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost:5432/finance_db
CORS_ORIGINS=https://your-domain.com
```

## 5. Set up PostgreSQL

```bash
sudo -u postgres psql
CREATE DATABASE finance_db;
CREATE USER financeuser WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE finance_db TO financeuser;
```

## 6. Start Gunicorn

```bash
cd backend
source venv/bin/activate
gunicorn --bind 0.0.0.0:8000 app:create_app() --workers 3
```

Use a service manager like `systemd` for production reliability.

## 7. Configure Nginx

Example config:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable it:
```bash
sudo ln -s /etc/nginx/sites-available/finance /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 8. Frontend deployment

Build and serve the React frontend from a static host or a second Nginx site.

For Vite:
```bash
cd frontend
npm install
npm run build
```

Then serve the `dist` directory using Nginx or host it separately.

## 9. Final checks

- Verify `https://your-domain.com/api/health`
- Test login/register flow
- Test PDF export and reports
- Run database migrations if needed























