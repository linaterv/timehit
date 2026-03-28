# S005 — Admin Creates Clients

**Priority:** P0  
**Sprint:** 1–2  
**Assigned to:** TBD  
**Depends on:** S002, S003

## Story

As an **admin**, I want to create client companies so that I can later assign contractors to them via placements.

## Client Model

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID | Primary key |
| `company_name` | CharField | Required |
| `billing_address` | TextField | Required — used on invoices |
| `tax_id` | CharField | VAT number, optional |
| `contact_name` | CharField | Primary contact person at the client |
| `contact_email` | EmailField | Primary contact email |
| `contact_phone` | CharField | Optional |
| `payment_terms` | IntegerField | Days until payment due (default: 30) |
| `notes` | TextField | Internal notes |
| `is_active` | BooleanField | Default True |
| `created_at` | DateTimeField | Auto |
| `updated_at` | DateTimeField | Auto |
| `created_by` | FK → User | |

## Acceptance Criteria

### UI — Create Client
- [ ] Admin navigates to "Clients" section
- [ ] "Create Client" form with all fields above
- [ ] Validation: company name and billing address required
- [ ] Success → redirect to client list

### UI — Client List
- [ ] List of all clients: company name, contact name, active status, number of active placements (can be 0 for now)
- [ ] Searchable by company name or contact name
- [ ] Filterable by active/inactive

### UI — Edit Client
- [ ] Admin can edit all fields
- [ ] Admin can deactivate client
- [ ] Deactivating a client does NOT auto-close placements — admin gets a warning if active placements exist

### API
- [ ] `POST /api/clients/` — create (admin only)
- [ ] `GET /api/clients/` — list (admin only)
- [ ] `GET /api/clients/{id}/` — detail (admin only)
- [ ] `PATCH /api/clients/{id}/` — update (admin only)

### Audit
- [ ] Client creation: actor, company name, timestamp
- [ ] Client update: actor, fields changed, timestamp
- [ ] Client deactivation: actor, company name, timestamp

## Notes

- Client approver users (for dual approval) are Phase 2 — don't model the link yet
- `payment_terms` will be used for invoice due dates when we build invoicing
- One client can have many placements (modeled in S006)

### Smoke Test (Dev Portal)
- [ ] Navigate to Clients section — list page renders
- [ ] Create a new client — form submits, client appears in list
- [ ] Edit the client — changes save, reflected in list
- [ ] Deactivate client — status updates
- [ ] Search/filter clients — results update
- [ ] API: `GET /api/clients/` returns client list with admin token
- [ ] Non-admin user cannot access Clients section (403)

## Out of Scope
- Client portal / client login
- Multiple billing addresses per client
- Client approver accounts (Phase 2)
