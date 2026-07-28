# AICCMS — Deployment Guide

## Production Checklist

Before deploying, ensure:

- [ ] `JWT_SECRET` is a strong random secret (≥ 32 characters)
- [ ] `GROQ_API_KEY` is set
- [ ] `DATABASE_URL` points to a production PostgreSQL instance
- [ ] `APP_ENV=production` is set
- [ ] Default seed passwords are changed in the database
- [ ] CORS origins restricted to your actual frontend domain
- [ ] HTTPS is configured on the reverse proxy or load balancer
- [ ] Database backups are scheduled

---

## Option 1 — Docker Compose (Self-hosted / VPS)

### Supported Platforms
- DigitalOcean Droplet
- AWS EC2
- Azure VM
- Any Linux VPS with Docker installed

### Steps

```bash
# On your server:
git clone <your-repo-url> aiccms
cd aiccms

# Create production env file
cp backend/.env.example backend/.env
nano backend/.env
```

**Production `backend/.env`:**
```env
APP_ENV=production
DATABASE_URL=postgresql+asyncpg://postgres:<DB_PASSWORD>@postgres:5432/aiccms
JWT_SECRET=<minimum-32-character-random-string>
JWT_EXPIRE_MINUTES=60
GROQ_API_KEY=gsk_<your-groq-key>
CORS_ORIGINS=["https://yourdomain.com"]
```

**Create `docker-compose.override.yml`** (never commit this):
```yaml
version: "3.9"
services:
  postgres:
    environment:
      POSTGRES_PASSWORD: <strong-db-password>
  frontend:
    build:
      args:
        VITE_API_BASE_URL: https://api.yourdomain.com
```

```bash
# Start production stack
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d --build

# Check logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Verify health
curl http://localhost:8000/health
```

---

## Option 2 — Railway (Free Tier, Recommended for College Projects)

### Backend Deployment

1. Go to https://railway.app and sign up
2. Click **New Project** → **Deploy from GitHub Repo**
3. Select your repository
4. Set **Root Directory** to `backend`
5. Railway auto-detects the Dockerfile
6. Add environment variables in Railway dashboard:
   ```
   APP_ENV=production
   DATABASE_URL=<railway-postgresql-url>
   JWT_SECRET=<your-secret>
   GROQ_API_KEY=<your-key>
   ```
7. Add a PostgreSQL plugin from Railway's plugin marketplace
8. Copy the `DATABASE_URL` from the PostgreSQL plugin into your service variables

### Frontend Deployment

**Option A — Vercel:**
1. Go to https://vercel.com
2. Import your GitHub repository
3. Set **Root Directory** to `frontend`
4. Add environment variable: `VITE_API_BASE_URL=https://<your-railway-backend-url>`
5. Deploy

**Option B — Netlify:**
1. Go to https://netlify.com
2. Connect GitHub repo, set base directory to `frontend`
3. Build command: `npm run build`
4. Publish directory: `dist`
5. Add env var: `VITE_API_BASE_URL=https://<backend-url>`

---

## Option 3 — Render (Free Tier)

### Backend

1. Go to https://render.com
2. New → **Web Service**
3. Connect GitHub repo, root directory: `backend`
4. Runtime: **Docker**
5. Set environment variables (same as Railway above)
6. Create a **PostgreSQL** database on Render and link it

### Frontend

1. New → **Static Site**
2. Connect repo, root: `frontend`
3. Build command: `npm install && npm run build`
4. Publish directory: `dist`
5. Add env var: `VITE_API_BASE_URL=https://<render-backend-url>`

---

## Option 4 — Manual Production (Ubuntu Server)

```bash
# Install dependencies
sudo apt update
sudo apt install python3.12 python3.12-venv nginx postgresql postgresql-contrib nodejs npm tesseract-ocr

# Clone project
git clone <repo> /var/www/aiccms
cd /var/www/aiccms/backend

# Setup Python
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup environment
cp .env.example .env
nano .env   # fill in production values

# Setup database
sudo -u postgres psql -c "CREATE DATABASE aiccms;"
sudo -u postgres psql -c "CREATE USER aiccms_user WITH PASSWORD '<password>';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE aiccms TO aiccms_user;"
alembic upgrade head

# Build frontend
cd /var/www/aiccms/frontend
npm install
VITE_API_BASE_URL=https://api.yourdomain.com npm run build

# Setup systemd service for backend
sudo nano /etc/systemd/system/aiccms.service
```

**`/etc/systemd/system/aiccms.service`:**
```ini
[Unit]
Description=AICCMS FastAPI Backend
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/aiccms/backend
Environment=PATH=/var/www/aiccms/backend/venv/bin
EnvironmentFile=/var/www/aiccms/backend/.env
ExecStart=/var/www/aiccms/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable aiccms
sudo systemctl start aiccms
```

**Nginx config** (`/etc/nginx/sites-available/aiccms`):
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Frontend (React SPA)
    location / {
        root /var/www/aiccms/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Backend health + docs
    location ~ ^/(health|docs|redoc|openapi.json) {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }

    # File upload size
    client_max_body_size 25M;
}
```

```bash
sudo ln -s /etc/nginx/sites-available/aiccms /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**HTTPS with Let's Encrypt:**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

---

## Database Backups

```bash
# Manual backup
pg_dump -U postgres aiccms > aiccms_backup_$(date +%Y%m%d).sql

# Automated daily backup (cron)
echo "0 2 * * * pg_dump -U postgres aiccms > /backups/aiccms_$(date +\%Y\%m\%d).sql" | crontab -

# Restore
psql -U postgres aiccms < aiccms_backup_20260728.sql
```

---

## Security Hardening

```bash
# Generate a strong JWT secret
python3 -c "import secrets; print(secrets.token_hex(32))"

# Restrict PostgreSQL to localhost only (postgresql.conf)
listen_addresses = 'localhost'

# Enable firewall (UFW)
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw deny 5432/tcp     # Block PostgreSQL from internet
sudo ufw enable
```

---

## Environment Variable Reference (Production)

```env
# Required
APP_ENV=production
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/aiccms
JWT_SECRET=<minimum-32-character-random-secret>
GROQ_API_KEY=gsk_<your-groq-api-key>

# Recommended for production
JWT_EXPIRE_MINUTES=30
CORS_ORIGINS=["https://yourdomain.com"]
MAX_PDF_SIZE_MB=20
MAX_IMAGE_SIZE_MB=10

# Optional
GROQ_MODEL=gemma2-9b-it
```
