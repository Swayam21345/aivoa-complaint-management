# AICCMS — API Reference

Base URL: `http://localhost:8000` (development)  
Auth: Bearer JWT token in `Authorization` header  
Interactive Docs: `http://localhost:8000/docs`

---

## Authentication

### POST `/api/auth/login`

Authenticate and receive a JWT token.

**Request:**
```json
{
  "email": "admin@aiccms.local",
  "password": "Admin@123"
}
```

**Response `200`:**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "full_name": "System Administrator",
    "email": "admin@aiccms.local",
    "role": "ADMIN"
  }
}
```

### GET `/api/auth/me`

Get current authenticated user. Requires bearer token.

---

## Health

### GET `/health`

```json
{ "status": "ok" }
```

---

## Complaints

### POST `/api/complaints`
Create a new complaint. Roles: ADMIN, QA_MANAGER, INVESTIGATOR.

**Body:**
```json
{
  "title": "Product contamination reported",
  "description": "Customer reported foreign material in batch X-123",
  "complaint_type": "PRODUCT_QUALITY",
  "priority": "HIGH",
  "customer_name": "Acme Pharma",
  "product_name": "Tablet X",
  "batch_number": "X-123",
  "lot_number": "LOT-001"
}
```

### GET `/api/complaints`
List complaints with pagination and filters.

Query params: `page`, `page_size`, `status`, `priority`, `search`, `assigned_to`

### GET `/api/complaints/{id}`
Get full complaint detail including signatures, CAPA links, history.

### PATCH `/api/complaints/{id}`
Update complaint fields or status.

### DELETE `/api/complaints/{id}`
Soft-delete. Roles: ADMIN, QA_MANAGER.

---

## Electronic Signatures (21 CFR Part 11)

### POST `/api/complaints/{id}/sign`
Sign a complaint action (e.g., QA Approval, Closure). Password re-authentication required.

**Body:**
```json
{
  "action": "QA_APPROVAL",
  "password": "Admin@123",
  "reason": "Complaint meets QA release criteria"
}
```

### GET `/api/complaints/{id}/signatures`
Get all electronic signatures for a complaint.

---

## CAPA Management

### POST `/api/capa`
Create a CAPA record. Roles: ADMIN, QA_MANAGER, INVESTIGATOR.

**Body:**
```json
{
  "title": "Process deviation CAPA",
  "description": "Root cause identified as calibration drift",
  "complaint_id": "uuid",
  "assigned_to": "uuid",
  "due_date": "2026-09-01",
  "priority": "HIGH"
}
```

### GET `/api/capa`
List CAPAs. Supports: `status`, `priority`, `search`, `page`, `page_size`.

### GET `/api/capa/{id}`
Get CAPA detail.

### PATCH `/api/capa/{id}`
Update CAPA fields or advance status.

### POST `/api/capa/{id}/effectiveness-review`
Submit effectiveness review. Requires electronic signature.

### POST `/api/capa/{id}/close`
Close CAPA. Requires electronic signature.

### GET `/api/capa/metrics/dashboard`
CAPA dashboard KPIs.

---

## RCA & FMEA

### POST `/api/rca`
Create an RCA with 5-Why analysis and optional FMEA.

**Body:**
```json
{
  "complaint_id": "uuid",
  "title": "Root Cause Analysis — Batch X-123",
  "method": "FIVE_WHY",
  "whys": [
    {"why_number": 1, "description": "Filter clogged"},
    {"why_number": 2, "description": "Scheduled maintenance skipped"},
    {"why_number": 3, "description": "Maintenance log not updated"},
    {"why_number": 4, "description": "No SOP for log verification"},
    {"why_number": 5, "description": "Training gap on SOP compliance"}
  ],
  "root_cause": "Training gap on SOP compliance",
  "fmea_items": [
    {
      "failure_mode": "Filter clog",
      "severity": 8,
      "occurrence": 4,
      "detection": 3
    }
  ]
}
```

### GET `/api/rca`
List RCAs. Filters: `status`, `search`, `complaint_id`.

### GET `/api/rca/{id}`
Get RCA detail with FMEA items.

### POST `/api/rca/{id}/approve`
Approve RCA. Requires electronic signature.

### GET `/api/rca/metrics/dashboard`
RCA dashboard KPIs.

---

## Document Control

### POST `/api/documents/upload`
Upload a document. Multipart form.

**Form fields:** `file`, `document_type`, `title`, `description`, `related_complaint_id` (optional)

Supported types: PDF, DOCX, XLSX, PNG, JPG, MP4, ZIP

### GET `/api/documents`
List documents. Filters: `document_type`, `status`, `search`.

### GET `/api/documents/{id}`
Get document detail including version history.

### POST `/api/documents/{id}/version`
Upload a new version of an existing document.

### POST `/api/documents/{id}/approve`
Approve document. Requires electronic signature.

### POST `/api/documents/{id}/archive`
Archive document.

### POST `/api/documents/{id}/restore`
Restore archived document.

### GET `/api/documents/{id}/download`
Download document file.

### GET `/api/documents/metrics/dashboard`
Document control dashboard KPIs.

---

## Internal Audits

### POST `/api/internal-audits`
Create an internal audit.

**Body:**
```json
{
  "title": "Annual GMP Audit Q3 2026",
  "scope": "Manufacturing floor, QC lab",
  "lead_auditor": "Jane Smith",
  "scheduled_start_date": "2026-09-01T09:00:00Z",
  "scheduled_end_date": "2026-09-03T17:00:00Z"
}
```

### GET `/api/internal-audits`
List audits. Filters: `status`, `search`.

### GET `/api/internal-audits/{id}`
Get audit detail with checklist items and findings.

### POST `/api/internal-audits/{id}/checklist`
Add a checklist item.

### PATCH `/api/internal-audits/{id}/checklist/{item_id}`
Update checklist item status.

### POST `/api/internal-audits/{id}/findings`
Log an audit finding.

### POST `/api/internal-audits/{id}/approve`
Approve and close audit. Requires electronic signature.

### POST `/api/internal-audits/{id}/inspection-readiness`
Generate inspection readiness package.

### GET `/api/internal-audits/metrics/dashboard`
Audit dashboard KPIs.

---

## Supplier Quality

### POST `/api/suppliers`
Create a supplier record.

**Body:**
```json
{
  "supplier_name": "BioShield Packaging Corp",
  "supplier_type": "PACKAGING",
  "risk_level": "MEDIUM",
  "email": "quality@bioshield.com",
  "country": "USA"
}
```

### GET `/api/suppliers`
List suppliers. Filters: `status`, `risk_level`, `approval_status`, `search`.

### GET `/api/suppliers/{id}`
Get supplier detail.

### POST `/api/suppliers/{id}/approve`
Approve supplier. Requires electronic signature.

### POST `/api/suppliers/{id}/audits`
Log a supplier audit.

### POST `/api/suppliers/{id}/scorecards`
Submit a supplier scorecard.

### POST `/api/suppliers/{id}/nonconformances`
Log a non-conformance against a supplier.

### GET `/api/suppliers/metrics/dashboard`
Supplier quality dashboard KPIs.

### GET `/api/suppliers/report`
Supplier quality PDF report.

---

## Training & LMS

### POST `/api/training/courses`
Create a training course.

### GET `/api/training/courses`
List courses.

### POST `/api/training/courses/{id}/quiz`
Create a quiz for a course.

### POST `/api/training/courses/{id}/quiz/attempt`
Submit a quiz attempt.

### POST `/api/training/courses/{id}/assign`
Assign a course to users.

### GET `/api/training/assignments`
List training assignments.

### GET `/api/training/competency`
Get competency matrix.

### POST `/api/training/competency`
Record a competency assessment.

### GET `/api/training/metrics/dashboard`
Training dashboard KPIs.

### GET `/api/training/report`
Training compliance report.

---

## Dashboard

### GET `/api/dashboard`
Returns aggregated KPIs across all modules:
- Total complaints by status
- Overdue CAPAs
- Open RCAs
- Document approval pending
- Audit findings
- Supplier risk summary
- Training compliance rate
- Signature activity (30 days)

---

## AI Copilot

### POST `/api/upload`
Upload a document for AI analysis. Returns parsed complaint data.

**Form fields:** `file` (PDF, image, or text)

**Response:**
```json
{
  "complaint_title": "AI-extracted title",
  "complaint_type": "PRODUCT_QUALITY",
  "priority": "HIGH",
  "description": "Extracted complaint description",
  "customer_name": "Extracted customer",
  "product_name": "Extracted product",
  "batch_number": "Extracted batch",
  "capa_recommendation": "Immediate quarantine of batch..."
}
```

---

## Role Permissions

| Endpoint Category | ADMIN | QA_MANAGER | INVESTIGATOR | VIEWER |
|-------------------|-------|------------|--------------|--------|
| Complaints (read) | ✅ | ✅ | ✅ | ✅ |
| Complaints (write) | ✅ | ✅ | ✅ | ❌ |
| Sign / approve | ✅ | ✅ | ❌ | ❌ |
| CAPA (write) | ✅ | ✅ | ✅ | ❌ |
| RCA (write) | ✅ | ✅ | ✅ | ❌ |
| Documents (upload) | ✅ | ✅ | ✅ | ❌ |
| Documents (approve) | ✅ | ✅ | ❌ | ❌ |
| Audits (write) | ✅ | ✅ | ❌ | ❌ |
| Suppliers (approve) | ✅ | ✅ | ❌ | ❌ |
| Training (admin) | ✅ | ✅ | ❌ | ❌ |
| Dashboard | ✅ | ✅ | ✅ | ✅ |

---

## Error Responses

All errors follow a consistent format:

```json
{
  "detail": "Human-readable error message"
}
```

| Status Code | Meaning |
|-------------|---------|
| `400` | Bad request / business rule violation |
| `401` | Unauthenticated or wrong password (for signatures) |
| `403` | Insufficient role permissions |
| `404` | Resource not found |
| `409` | Conflict (duplicate resource) |
| `422` | Validation error |
| `500` | Internal server error |
