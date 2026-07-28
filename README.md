# AICCMS — AI-Powered Complaint Management System

> **Enterprise-grade Pharmaceutical Quality Management System (QMS)**  
> Built with FastAPI · React · LangGraph · PostgreSQL

[![Tests](https://img.shields.io/badge/tests-72%20passed-brightgreen)](.)
[![mypy](https://img.shields.io/badge/mypy-86%20files%20clean-brightgreen)](.)
[![TypeScript](https://img.shields.io/badge/TypeScript-strict-blue)](.)
[![Docker](https://img.shields.io/badge/docker-compose-ready-blue)](.)

---

## Overview

AICCMS is a production-ready, AI-powered Quality Management System designed for pharmaceutical manufacturing environments. It automates complaint intake, investigation, root cause analysis, CAPA management, document control, supplier qualification, training management, and internal audits — all with 21 CFR Part 11 compliant electronic signatures and a full audit trail.

---

## Feature Matrix

| Module | Description | 21 CFR Part 11 |
|--------|-------------|----------------|
| **Complaint Management** | Full CRUD, status workflow, reviewer notes, SLA tracking | ✅ |
| **AI Copilot** | LangGraph + Groq: auto-parses PDFs/images/emails, classifies risk, drafts CAPA | — |
| **CAPA Management** | Create, assign, track, close CAPAs; effectiveness review | ✅ |
| **RCA & FMEA** | 5-Why analysis, Fishbone, FMEA risk matrix; RPN scoring | ✅ |
| **Document Control** | Upload, version, approve, archive documents (PDF, DOCX, XLSX, images, video) | ✅ |
| **Internal Audit** | Audit planning, checklists, findings, inspection readiness packages | ✅ |
| **Supplier Quality** | Supplier approval, audit scorecards, non-conformance, corrective actions | ✅ |
| **Training & LMS** | Courses, quizzes, assignments, competency matrix, training records | ✅ |
| **Electronic Signatures** | SHA-256 signed with password re-auth, full audit log | ✅ |
| **Audit Trail** | Immutable event log for every state change and signature | ✅ |
| **RBAC** | ADMIN, QA_MANAGER, INVESTIGATOR, VIEWER roles | ✅ |
| **Dashboard** | KPI cards, trend charts, overdue alerts, metrics across all modules | — |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18 · Vite 6 · TypeScript 5 · Redux Toolkit · React Router 6 · Recharts · Tailwind CSS |
| **Backend** | Python 3.12 · FastAPI · SQLAlchemy 2 (async) · Alembic · Pydantic v2 |
| **AI** | LangGraph · Groq API (`gemma2-9b-it`) · Pytesseract OCR |
| **Database** | PostgreSQL 15 (production) · SQLite (testing) |
| **Auth** | JWT (HS256) · bcrypt password hashing |
| **Container** | Docker · docker-compose |

---

## Quick Start — Docker (Recommended)

```bash
# 1. Clone and enter the project
cd aiccms

# 2. Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 3. Edit backend/.env and set:
#    JWT_SECRET=<strong-random-secret>
#    GROQ_API_KEY=<your-groq-api-key>

# 4. Start all services
docker-compose up --build

# Services:
#   Frontend  →  http://localhost:5173
#   Backend   →  http://localhost:8000
#   API Docs  →  http://localhost:8000/docs
#   Health    →  http://localhost:8000/health
```

**Default credentials** (seed users created on first migration):

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@aiccms.local | Admin@123 |
| QA Manager | qa@aiccms.local | QAManager@123 |
| Investigator | investigator@aiccms.local | Investigator@123 |
| Viewer | viewer@aiccms.local | Viewer@123 |

> ⚠️ Change all default passwords before deploying to production.

---

## Manual Local Setup

See [INSTALL.md](INSTALL.md) for detailed step-by-step installation.

---

## Project Structure

```
aiccms/
├── docker-compose.yml
├── .gitignore
├── README.md
├── INSTALL.md
├── DEPLOYMENT.md
├── API.md
├── ARCHITECTURE.md
├── CHANGELOG.md
│
├── frontend/                        # React SPA (Vite + TypeScript)
│   ├── src/
│   │   ├── App.tsx                  # Root component + routing
│   │   ├── pages/                   # Route-level page components
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── ComplaintsListPage.tsx
│   │   │   ├── ComplaintDetailPage.tsx
│   │   │   ├── ComplaintFormPage.tsx
│   │   │   ├── CAPAListPage.tsx
│   │   │   ├── CAPADetailPage.tsx
│   │   │   ├── RCAListPage.tsx
│   │   │   ├── RCADetailPage.tsx
│   │   │   ├── DocumentLibraryPage.tsx
│   │   │   ├── DocumentDetailPage.tsx
│   │   │   ├── InternalAuditPage.tsx
│   │   │   ├── InternalAuditDetailPage.tsx
│   │   │   ├── SupplierPage.tsx
│   │   │   ├── SupplierDetailPage.tsx
│   │   │   ├── TrainingPage.tsx
│   │   │   ├── TrainingDetailPage.tsx
│   │   │   ├── CompetencyPage.tsx
│   │   │   ├── UploadPage.tsx
│   │   │   └── LoginPage.tsx
│   │   ├── components/              # Reusable UI components
│   │   ├── services/                # Axios API clients
│   │   ├── store/                   # Redux Toolkit slices
│   │   ├── types/                   # TypeScript domain types
│   │   └── utils/                   # Helpers (dates, formatting)
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── vite.config.ts
│   └── package.json
│
└── backend/                         # FastAPI application
    ├── app/
    │   ├── main.py                  # App factory + router registration
    │   ├── config.py                # Settings (pydantic-settings)
    │   ├── api/
    │   │   ├── deps.py              # Auth + RBAC dependencies
    │   │   └── routes/
    │   │       ├── auth.py
    │   │       ├── complaints.py
    │   │       ├── capa.py
    │   │       ├── rca.py
    │   │       ├── documents.py
    │   │       ├── internal_audits.py
    │   │       ├── suppliers.py
    │   │       ├── training.py
    │   │       ├── signatures.py
    │   │       ├── dashboard.py
    │   │       └── upload.py
    │   ├── models/                  # SQLAlchemy ORM models (16 tables)
    │   ├── schemas/                 # Pydantic request/response models
    │   ├── services/                # Business logic layer
    │   ├── ai/                      # LangGraph workflow + Groq integration
    │   ├── core/                    # RBAC, audit logging
    │   └── db/                      # Database session management
    ├── alembic/                     # 13 database migrations
    ├── tests/                       # 72 pytest tests
    ├── Dockerfile
    ├── entrypoint.sh
    └── requirements.txt
```

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ✅ | — | PostgreSQL connection string |
| `JWT_SECRET` | ✅ | — | Secret key for JWT signing (min 32 chars) |
| `GROQ_API_KEY` | ✅ | — | Groq API key for AI features |
| `JWT_EXPIRE_MINUTES` | No | `60` | JWT token expiry in minutes |
| `APP_ENV` | No | `production` | `development` or `production` |
| `GROQ_MODEL` | No | `gemma2-9b-it` | Groq model name |
| `CORS_ORIGINS` | No | `["http://localhost:5173"]` | Allowed CORS origins (JSON array) |
| `MAX_PDF_SIZE_MB` | No | `20` | Maximum PDF upload size |
| `MAX_IMAGE_SIZE_MB` | No | `10` | Maximum image upload size |

### Frontend (`frontend/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_BASE_URL` | No | `http://localhost:8000` | Backend API base URL |

---

## Available Scripts

### Backend

| Command | Description |
|---------|-------------|
| `uvicorn app.main:app --reload` | Start development server |
| `alembic upgrade head` | Apply all migrations |
| `alembic downgrade -1` | Roll back last migration |
| `pytest -vv` | Run test suite (72 tests) |
| `mypy app` | Type checking |
| `ruff check .` | Linting |
| `ruff format .` | Formatting |

### Frontend

| Command | Description |
|---------|-------------|
| `npm run dev` | Start Vite dev server |
| `npm run build` | Type-check and build for production |
| `npm run typecheck` | TypeScript type checking |
| `npm run lint` | ESLint |
| `npm run format` | Prettier formatting |

---

## API Documentation

Interactive Swagger UI: `http://localhost:8000/docs`  
ReDoc: `http://localhost:8000/redoc`  
Full endpoint reference: [API.md](API.md)

---

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for full deployment instructions (Docker, Railway, Render, DigitalOcean).

---

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for system design, database schema, and data flow diagrams.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and feature log.

---

## Test Coverage

```
72 tests · 0 failures · 1 warning (third-party Pydantic deprecation)
mypy: 0 issues found in 86 source files
TypeScript: 0 errors
```

---

## License

This project was built as an enterprise internship assignment for AI Product Engineering.

---

*AICCMS v5.8 — Enterprise AI Pharmaceutical Quality Management System*
