# AICCMS — Changelog

All notable changes are documented in this file.

Format: [Version] — Date  
Types: Added · Changed · Fixed · Security · Removed

---

## [5.8] — 2026-07-28

### Added
- **Enterprise Internal Audit Management & Inspection Readiness**
  - Internal audit planning with lead auditor, scope, and scheduled dates
  - Checklist item management with pass/fail/observation status
  - Audit finding logging with severity levels and corrective action tracking
  - Electronic signature-based audit approval and closure
  - Inspection readiness package generation
  - Internal audit dashboard with KPI metrics
  - 5 new pytest tests (72 total)

---

## [5.7] — 2026-07-27

### Added
- **Enterprise Supplier Quality Management (SQM)**
  - Supplier master data with type, category, and risk level classification
  - Electronic signature-based supplier approval workflow
  - Supplier audit scheduling and scoring
  - Supplier scorecard with weighted KPI scoring
  - Non-conformance tracking and corrective action management
  - Supplier quality dashboard and compliance reports
  - 5 new pytest tests (67 total)

---

## [5.6] — 2026-07-26

### Added
- **Enterprise Training & Competency Management (LMS)**
  - Training course management with categories and passing scores
  - Quiz creation with multiple-choice questions and automated grading
  - Training assignments to individual users or all active users
  - Competency record tracking per user/course
  - Competency matrix view across all staff
  - Training dashboard with compliance rates and overdue assignments
  - Training compliance reports
  - 5 new pytest tests (62 total)

---

## [5.5] — 2026-07-25

### Added
- **Enterprise Document Control & Evidence Management**
  - Document upload with SHA-256 file hash integrity verification
  - Document versioning (each upload creates a new version)
  - Electronic signature-based document approval
  - Document archiving and restoration
  - Secure file download endpoint
  - Document types: COMPLAINT_EVIDENCE, RCA_EVIDENCE, CAPA_EVIDENCE, INVESTIGATION_REPORT, LAB_REPORT, CUSTOMER_ATTACHMENT, SUPPLIER_DOCUMENT, CALIBRATION_CERT, and more
  - Supported formats: PDF, DOCX, XLSX, PNG, JPG, MP4, ZIP
  - Document control dashboard metrics
  - 7 new pytest tests (57 total)

---

## [5.4] — 2026-07-24

### Added
- **Enterprise RCA & FMEA Module**
  - Root Cause Analysis with 5-Why, Fishbone, and Fault Tree methods
  - FMEA (Failure Mode and Effects Analysis) with RPN scoring
    - Severity × Occurrence × Detection = RPN
  - Electronic signature for RCA approval
  - RCA approval gate on complaint workflow (blocks transition without approved RCA)
  - RCA dashboard metrics
  - 6 new pytest tests (50 total)

---

## [5.3] — 2026-07-23

### Added
- **Enterprise CAPA Management**
  - CAPA creation linked to complaints
  - Full status lifecycle: OPEN → IN_PROGRESS → EFFECTIVENESS_REVIEW → CLOSED
  - Electronic signature for effectiveness review and CAPA closure
  - CAPA gate on QA Approval (all linked CAPAs must be CLOSED before complaint can be approved)
  - CAPA dashboard KPIs (overdue count, closure rate, by priority)
  - 10 new pytest tests (44 total)

---

## [5.2] — 2026-07-22

### Added
- **21 CFR Part 11 Electronic Signatures**
  - SHA-256 cryptographic hash per signature event
  - Password re-authentication required for every signature
  - Supported actions: QA_APPROVAL, COMPLAINT_CLOSURE, CAPA_EFFECTIVENESS, RCA_APPROVAL, DOCUMENT_APPROVAL, AUDIT_CLOSURE
  - Signature history endpoint per complaint
  - Audit event created on every signature
  - 12 new pytest tests

### Security
- bcrypt password hashing with cost factor 12
- JWT HS256 tokens with configurable expiry

---

## [5.1] — 2026-07-21

### Added
- **Enterprise Workflow Engine**
  - Complaint status state machine with enforced transition rules
  - SLA tracking with due dates and overdue flagging
  - RBAC permission checks on every state transition
  - Complaint assignment to investigators
  - Investigator dashboard (my assigned complaints)

---

## [5.0] — 2026-07-20

### Added
- **Role-Based Access Control (RBAC)**
  - Four roles: ADMIN, QA_MANAGER, INVESTIGATOR, VIEWER
  - Role-based endpoint guards via FastAPI dependency injection
  - Seed users created on first migration

- **Audit Trail**
  - Immutable `audit_events` table
  - Every status change, signature, and assignment logged

- **Dashboard**
  - KPI cards: total complaints, open, overdue, high priority
  - Trend charts: complaints by status, by month
  - Signature activity metrics

---

## [4.0] — 2026-07-18

### Added
- AI Copilot — LangGraph workflow
- Document parser: PDF (PyPDF2), images (Pytesseract OCR), plain text/email
- 3-node LangGraph pipeline: Extract → Classify → CAPA Recommendation
- Groq API integration (gemma2-9b-it model)
- Upload endpoint returning pre-filled complaint data

---

## [3.0] — 2026-07-15

### Added
- Complaint management CRUD (create, list, get, update, soft-delete)
- Reviewer notes (create, list, soft-delete)
- Complaint status history log
- Search and filtering on complaint list
- Pagination support

---

## [2.0] — 2026-07-12

### Added
- Document upload API (multipart/form-data)
- Backend: FastAPI + SQLAlchemy 2 async + Alembic
- Frontend: React 18 + Vite + TypeScript + Redux Toolkit
- Initial database schema (Alembic migrations)
- Docker Compose with PostgreSQL + backend + frontend services

---

## [1.0] — 2026-07-10

### Added
- Project scaffolding
- Backend: FastAPI with health endpoint
- Frontend: React SPA shell with routing
- docker-compose.yml
- README.md, .gitignore, .env.example files
