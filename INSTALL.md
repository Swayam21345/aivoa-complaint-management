# AICCMS — Installation Guide

## System Requirements

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.12+ | https://python.org |
| Node.js | 20+ | https://nodejs.org |
| PostgreSQL | 15+ | https://postgresql.org |
| Docker | 24+ (optional) | https://docker.com |
| Tesseract OCR | 5+ | `brew install tesseract` (macOS) |
| Git | Any | https://git-scm.com |

---

## Option A — Docker (Fastest)

### Prerequisites
- Docker Desktop installed and running

### Steps

```bash
# 1. Navigate to the project
cd aiccms

# 2. Copy environment templates
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 3. Edit backend/.env — fill in required values:
#    JWT_SECRET=<at-least-32-character-random-string>
#    GROQ_API_KEY=<your-key-from-console.groq.com>
nano backend/.env

# 4. Start all services
docker-compose up --build

# First run takes 2–3 minutes (downloads images, installs deps, runs migrations)
```

Services after startup:

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |

### Stop

```bash
docker-compose down           # Stop containers
docker-compose down -v        # Stop + delete DB volume (full reset)
```

---

## Option B — Manual Local Development

### Step 1 — PostgreSQL

**Via Docker (easiest):**
```bash
docker-compose up postgres -d
```

**Via local install:**
```bash
# macOS
brew install postgresql@15
brew services start postgresql@15

# Create the database
psql -U postgres -c "CREATE DATABASE aiccms;"
```

---

### Step 2 — Backend

```bash
cd backend

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Tesseract (required for OCR on image uploads)
# macOS:
brew install tesseract
# Ubuntu/Debian:
sudo apt-get install tesseract-ocr

# Copy and configure environment
cp .env.example .env
# Edit .env:
#   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/aiccms
#   JWT_SECRET=<random-32-char-string>
#   GROQ_API_KEY=<your-groq-key>

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --port 8000
```

Verify: http://localhost:8000/health should return `{"status": "ok"}`

---

### Step 3 — Frontend

```bash
cd frontend

# Install Node dependencies
npm install

# Copy environment file
cp .env.example .env
# VITE_API_BASE_URL is already set to http://localhost:8000 — no changes needed for local dev

# Start dev server
npm run dev
```

Verify: http://localhost:5173 — login page should appear.

---

## Default Login Credentials

| Role | Email | Password |
|------|-------|----------|
| ADMIN | admin@aiccms.local | Admin@123 |
| QA_MANAGER | qa@aiccms.local | QAManager@123 |
| INVESTIGATOR | investigator@aiccms.local | Investigator@123 |
| VIEWER | viewer@aiccms.local | Viewer@123 |

> ⚠️ These are development seed users. Change all passwords before production deployment.

---

## Generating a GROQ API Key

1. Go to https://console.groq.com
2. Sign up / log in
3. Navigate to **API Keys**
4. Click **Create API Key**
5. Copy the key into `backend/.env` as `GROQ_API_KEY=gsk_...`

The AI Copilot feature requires this key. The rest of the application works without it.

---

## Running Tests

```bash
cd backend

# Activate venv
source venv/bin/activate

# Run all tests (SQLite in-memory — no PostgreSQL needed for tests)
pytest -vv

# Expected: 72 passed, 1 warning
```

---

## Type Checking

```bash
# Backend
cd backend
./venv/bin/mypy app
# Expected: Success: no issues found in 86 source files

# Frontend
cd frontend
npm run typecheck
# Expected: no output (zero errors)
```

---

## Common Issues

### `alembic upgrade head` fails — "connection refused"
PostgreSQL is not running. Start it:
```bash
docker-compose up postgres -d
# or
brew services start postgresql@15
```

### `ModuleNotFoundError: No module named 'pytesseract'`
Tesseract binary not installed:
```bash
brew install tesseract   # macOS
```

### `GROQ_API_KEY not set` warning in logs
AI Copilot will be disabled. Set `GROQ_API_KEY` in `backend/.env`.

### Frontend shows "Network Error"
Backend is not running, or `VITE_API_BASE_URL` in `frontend/.env` is wrong.

### Docker: `port 5432 already in use`
A local PostgreSQL instance is using port 5432. Stop it or change the port in `docker-compose.yml`.
