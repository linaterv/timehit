# S007 — Admin Manages Contracts & Documents

**Priority:** P0  
**Sprint:** 2  
**Assigned to:** Eos  
**Depends on:** S004, S005, S006

## Story

As an **admin**, I want to upload and manage signed contracts, NDAs, and other legal documents so that every placement has its paperwork tracked and accessible in the platform.

## Contract Model

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID | Primary key |
| `title` | CharField | e.g. "Service Agreement", "NDA", "Contractor Agreement" |
| `contract_type` | CharField (choices) | `service_agreement`, `nda`, `contractor_agreement`, `amendment`, `other` |
| `contractor` | FK → Contractor | Nullable — some docs are client-only |
| `client` | FK → Client | Nullable — some docs are contractor-only |
| `placement` | FK → Placement | Nullable — can link to a specific placement |
| `document` | FileField | The uploaded PDF/scan |
| `file_name` | CharField | Original filename |
| `file_size` | PositiveIntegerField | Bytes |
| `signed_date` | DateField | When the document was signed |
| `expiry_date` | DateField | Nullable — not all contracts expire |
| `status` | CharField (choices) | `draft`, `active`, `expired`, `superseded` |
| `notes` | TextField | Internal notes |
| `is_active` | BooleanField | Default True |
| Uses `AuditMixin` | | created_at, updated_at, created_by, updated_by |

## Contract Types

| Type | Description |
|------|-------------|
| `service_agreement` | Main contract between agency and client |
| `nda` | Non-disclosure agreement (any party combination) |
| `contractor_agreement` | Agreement between agency and contractor |
| `amendment` | Amendment to an existing contract |
| `other` | Catch-all for anything else |

## Acceptance Criteria

### UI — Contract List
- [ ] Admin navigates to "Contracts" section in nav
- [ ] List page: title, type, linked contractor/client, signed date, status
- [ ] Filterable by type, status, client, contractor
- [ ] Searchable by title, contractor name, client name
- [ ] Click a contract → detail view with download link

### UI — Upload Contract
- [ ] "Upload Contract" form: title, type (dropdown), contractor (dropdown, optional), client (dropdown, optional), placement (dropdown, optional), file upload, signed date, expiry date (optional), notes
- [ ] File upload accepts: PDF, JPG, PNG (scanned docs)
- [ ] Max file size: 10MB
- [ ] Validation: title required, file required, signed_date required
- [ ] Success → redirect to contract list

### UI — Contract Detail
- [ ] Shows all fields + download link for the document
- [ ] Preview for PDFs (embedded viewer or link)
- [ ] Edit button → edit form (can replace the file)
- [ ] Shows linked contractor, client, placement as clickable links

### UI — Edit Contract
- [ ] Admin can edit: title, type, dates, notes, status, linked entities
- [ ] Admin can upload a replacement file (old file is NOT deleted — keep history)
- [ ] Admin can mark contract as `superseded` or `expired`

### API
- [ ] `POST /api/contracts/` — create with file upload (multipart, admin only)
- [ ] `GET /api/contracts/` — list (admin only, filterable)
- [ ] `GET /api/contracts/{id}/` — detail (admin: full; contractor: own contracts only)
- [ ] `PATCH /api/contracts/{id}/` — update (admin only)
- [ ] `GET /api/contracts/{id}/download/` — download the file

### File Storage
- [ ] Store files in `MEDIA_ROOT/contracts/` organized by year/month
- [ ] File naming: `{uuid}_{original_filename}` to avoid collisions
- [ ] Configure MEDIA_ROOT and MEDIA_URL in Django settings
- [ ] Serve media files in dev via Django (production will use nginx/S3)

### Permissions
- [ ] Only admin can upload, edit, and delete contracts
- [ ] Contractors can view contracts linked to them (read-only, download only)
- [ ] Clerks can view all contracts (read-only)

### Audit
- [ ] Contract upload: actor, title, linked entities, timestamp
- [ ] Contract update: actor, fields changed, timestamp
- [ ] Contract download: actor, timestamp (track who accessed the document)
- [ ] File replacement: actor, old filename, new filename, timestamp

### Smoke Test (Dev Portal)
- [ ] Navigate to Contracts section — list page renders
- [ ] Upload a PDF contract linked to a contractor → appears in list
- [ ] Upload an NDA linked to a client → appears in list
- [ ] Click download — file downloads correctly
- [ ] Edit contract — change title and status → reflected in list
- [ ] Login as contractor — can see own contracts, cannot see others
- [ ] API: `GET /api/contracts/` returns list with admin token

## Notes

- This is about document management, not contract generation — users upload scanned/signed docs
- No document signing workflow (Phase 2 if ever)
- No version tracking beyond file replacement (Phase 2)
- Keep the file upload simple — Django's built-in FileField, no S3 yet

## Out of Scope
- Digital signature workflow
- Document versioning / change tracking
- OCR or text extraction from scanned docs
- S3/cloud storage (production concern, not MVP)
- Contract templates / generation
