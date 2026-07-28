# AICCMS — Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT BROWSER                          │
│                                                                 │
│   React 18 + Vite + TypeScript + Redux Toolkit                  │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│   │Dashboard │ │Complaints│ │CAPA/RCA  │ │Documents/Audits  │  │
│   │          │ │          │ │          │ │Suppliers/Training│  │
│   └──────────┘ └──────────┘ └──────────┘ └──────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │ HTTPS / REST JSON
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       FASTAPI BACKEND                           │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   API Layer (Routes)                     │   │
│  │  auth  complaints  capa  rca  documents  audits          │   │
│  │  suppliers  training  signatures  dashboard  upload      │   │
│  └──────────────────┬──────────────────────────────────────┘   │
│                     │                                           │
│  ┌──────────────────▼──────────────────────────────────────┐   │
│  │                 Service Layer                            │   │
│  │  ComplaintService  CAPAService  RCAService               │   │
│  │  DocumentService   AuditService SupplierService          │   │
│  │  TrainingService   SignatureService                      │   │
│  └──────────────────┬──────────────────────────────────────┘   │
│                     │                                           │
│  ┌──────────────────▼──────────────────────────────────────┐   │
│  │          SQLAlchemy 2 Async ORM + Alembic                │   │
│  └──────────────────┬──────────────────────────────────────┘   │
│                     │                                           │
│  ┌──────────────────▼──────────────────────────────────────┐   │
│  │                 AI Layer (LangGraph)                     │   │
│  │  DocumentParser → ExtractNode → ClassifyNode             │   │
│  │  CAPANode → GroqLLM (gemma2-9b-it)                       │   │
│  └──────────────────┬──────────────────────────────────────┘   │
└─────────────────────┼───────────────────────────────────────────┘
                      │
          ┌───────────┴──────────┐
          │                      │
          ▼                      ▼
┌─────────────────┐    ┌──────────────────┐
│  PostgreSQL 15  │    │    Groq API       │
│  (13 tables)    │    │  (gemma2-9b-it)   │
└─────────────────┘    └──────────────────┘
```

---

## Layer Responsibilities

### Frontend (React SPA)

| Directory | Responsibility |
|-----------|---------------|
| `pages/` | Route-level components — one per module |
| `components/` | Reusable UI (modals, badges, skeleton loaders, charts) |
| `services/` | Axios API calls — one service per backend module |
| `store/` | Redux Toolkit slices for auth state |
| `types/` | TypeScript interfaces mirroring backend Pydantic schemas |
| `utils/` | Date formatting, risk color mapping |

### Backend (FastAPI)

| Directory | Responsibility |
|-----------|---------------|
| `api/routes/` | HTTP request handling, input validation, response shaping |
| `api/deps.py` | JWT auth dependency, RBAC `require_roles()` |
| `services/` | Business logic, workflow state machines |
| `models/` | SQLAlchemy ORM table definitions |
| `schemas/` | Pydantic request/response models |
| `ai/` | LangGraph workflow, document parser, Groq integration |
| `core/` | Audit logging helpers |
| `db/` | Async session factory, database init |

---

## Database Schema (13 Migrations, 16 Tables)

### Core Tables

```
users
├── id (UUID PK)
├── full_name
├── email (unique)
├── password_hash (bcrypt)
├── role (ADMIN | QA_MANAGER | INVESTIGATOR | VIEWER)
└── is_active

complaints
├── id (UUID PK)
├── complaint_number (unique, auto-generated CMP-YYYYMMDD-NNNN)
├── title
├── description
├── status (SUBMITTED → UNDER_INVESTIGATION → ROOT_CAUSE_IDENTIFIED
│           → CAPA_IN_PROGRESS → PENDING_QA_APPROVAL → CLOSED | REJECTED)
├── priority (LOW | MEDIUM | HIGH | CRITICAL)
├── complaint_type
├── customer_name / product_name / batch_number / lot_number
├── assigned_to → users.id
├── ai_summary / risk_classification / capa_recommendation
└── sla_due_date / closed_at / overdue

complaint_history  (immutable status change log)
reviewer_notes     (soft-delete notes per complaint)
audit_events       (immutable global audit trail)
electronic_signatures (SHA-256 signed, 21 CFR Part 11)
upload_records
uploaded_documents (SHA-256 file hash, versioned)
```

### Module Tables

```
capa_records
├── id, capa_number
├── complaint_id → complaints.id
├── status (OPEN → IN_PROGRESS → EFFECTIVENESS_REVIEW → CLOSED)
├── priority, assigned_to, due_date
└── effectiveness_notes

rca_records
├── id, complaint_id
├── method (FIVE_WHY | FISHBONE | FAULT_TREE)
├── root_cause, contributing_factors
└── status (DRAFT → APPROVED)

rca_why_items    (5-Why chain)
fmea_items       (failure mode, severity, occurrence, detection, RPN)

documents
├── id, document_number
├── document_type (COMPLAINT_EVIDENCE | RCA_EVIDENCE | CAPA_EVIDENCE |
│                  INVESTIGATION_REPORT | LAB_REPORT | CALIBRATION_CERT | ...)
├── file_hash (SHA-256), file_size, version_number
└── status (DRAFT | UNDER_REVIEW | APPROVED | ARCHIVED)

internal_audits
├── id, audit_number
├── lead_auditor, scope
├── scheduled/actual start/end dates
└── status (PLANNED → IN_PROGRESS → FINDINGS_REVIEW → CLOSED)

audit_checklist_items
audit_findings

suppliers
├── id, supplier_number
├── supplier_type, category, risk_level
├── approval_status (PENDING | QUALIFIED | APPROVED | SUSPENDED | DISQUALIFIED)
└── contact info

supplier_audits
supplier_scorecards
supplier_nonconformances
supplier_corrective_actions

training_courses
├── id, course_number
├── course_type, mandatory, passing_score
└── status (DRAFT | ACTIVE | ARCHIVED)

training_quizzes / quiz_questions / quiz_attempts
training_assignments
competency_records
```

---

## Authentication & Authorization Flow

```
1. POST /api/auth/login
   → password verified with bcrypt
   → JWT signed with HS256 + JWT_SECRET
   → JWT contains: sub (user_id), role, exp

2. Every protected endpoint:
   → Authorization: Bearer <token>
   → FastAPI dependency: get_current_user()
     → verifies JWT signature
     → loads user from DB
     → checks is_active

3. RBAC:
   → require_roles(["ADMIN", "QA_MANAGER"]) dependency
   → raises HTTP 403 if role not in allowed list

4. Electronic Signatures:
   → user re-submits their password
   → bcrypt.verify(password, user.password_hash)
   → SHA-256 hash = sha256(user_id + action + timestamp + reason)
   → stored in electronic_signatures table
   → audit_event created
```

---

## AI Workflow (LangGraph)

```
User uploads file (PDF / image / email text)
          │
          ▼
┌─────────────────┐
│  Document Parser │  pytesseract OCR for images
│                  │  PyPDF2 for PDFs
└────────┬─────────┘
         │  raw_text
         ▼
┌─────────────────┐
│  Extract Node    │  Groq API (gemma2-9b-it)
│                  │  Extracts: title, type, product,
│                  │  batch, customer, description
└────────┬─────────┘
         │  structured_data
         ▼
┌─────────────────┐
│  Classify Node   │  Groq API
│                  │  Determines: risk level,
│                  │  complaint category, urgency
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│  CAPA Node       │  Groq API
│                  │  Generates: initial CAPA
│                  │  recommendation draft
└────────┬─────────┘
         │
         ▼
   Complaint form pre-filled → user reviews and submits
```

---

## Status Workflows

### Complaint Status Machine
```
SUBMITTED
  → UNDER_INVESTIGATION  (assign investigator)
  → ROOT_CAUSE_IDENTIFIED  (requires approved RCA)
  → CAPA_IN_PROGRESS       (requires linked CAPA)
  → PENDING_QA_APPROVAL    (CAPA must be CLOSED)
  → CLOSED                 (electronic signature required)
  → REJECTED               (QA_MANAGER / ADMIN only)
```

### CAPA Status Machine
```
OPEN → IN_PROGRESS → EFFECTIVENESS_REVIEW → CLOSED
```

### RCA Status Machine
```
DRAFT → APPROVED  (electronic signature required)
```

### Document Status Machine
```
DRAFT → UNDER_REVIEW → APPROVED → ARCHIVED
```

### Audit Status Machine
```
PLANNED → IN_PROGRESS → FINDINGS_REVIEW → CLOSED
```

### Supplier Approval
```
PENDING → QUALIFIED → APPROVED → SUSPENDED | DISQUALIFIED
```

---

## Security Architecture

| Control | Implementation |
|---------|---------------|
| Authentication | JWT HS256, configurable expiry |
| Password storage | bcrypt (cost factor 12) |
| Electronic signatures | SHA-256 hash + password re-auth |
| CORS | Configurable origins via `CORS_ORIGINS` env var |
| File validation | MIME type + extension check before storage |
| SQL injection | SQLAlchemy ORM with parameterized queries |
| RBAC | Dependency injection per route |
| Audit immutability | INSERT-only `audit_events` table |
| Secrets | All secrets via environment variables only |

---

## Migration History

| Migration | Description |
|-----------|-------------|
| `001` | Initial schema (complaints, upload_records) |
| `002` | Upload records |
| `003` | Complaint management (status, history, notes) |
| `004` | Users table + RBAC |
| `005` | Workflow, SLA, escalation |
| `006` | Enterprise QMS (audit events) |
| `007` | Electronic signatures |
| `008` | CAPA records |
| `009` | RCA & FMEA |
| `010` | Document management |
| `011` | Training & LMS |
| `012` | Supplier Quality Management |
| `013` | Internal Audit Management |
