# S006 — Admin Creates Placements

**Priority:** P0  
**Sprint:** 2  
**Assigned to:** TBD  
**Depends on:** S004, S005

## Story

As an **admin**, I want to create placements that link a contractor to a client with agreed rates so that timesheets and invoices can be generated for that engagement.

## Placement Model

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID | Primary key |
| `contractor` | FK → Contractor | Required |
| `client` | FK → Client | Required |
| `title` | CharField | Description of the role, e.g. "Senior Java Developer" |
| `client_rate` | DecimalField(10,2) | What the client pays per hour |
| `contractor_rate` | DecimalField(10,2) | What the contractor gets paid per hour |
| `currency` | CharField | Default `EUR`, fixed for MVP |
| `start_date` | DateField | Required |
| `end_date` | DateField | Nullable — open-ended placements allowed |
| `approval_mode` | CharField | `agency_only` for MVP. `dual` modeled but not active. |
| `is_active` | BooleanField | Default True |
| `notes` | TextField | Internal |
| `created_at` | DateTimeField | Auto |
| `updated_at` | DateTimeField | Auto |
| `created_by` | FK → User | |

**Derived:** `margin = client_rate - contractor_rate` — never stored, always calculated.

## Acceptance Criteria

### UI — Create Placement
- [ ] Admin navigates to "Placements" section
- [ ] "Create Placement" form: select contractor (dropdown), select client (dropdown), title, both rates, start date, end date (optional)
- [ ] Validation: contractor_rate must be < client_rate (warn if margin < 10%, block if negative)
- [ ] Validation: start_date required, end_date must be after start_date if provided
- [ ] Cannot create placement for inactive contractor or inactive client
- [ ] Success → redirect to placement detail

### UI — Placement List
- [ ] List: contractor name, client name, title, rates, margin (calculated), status (active/ended), start date
- [ ] Filterable by client, contractor, active status
- [ ] Searchable by contractor name, client name, or title

### UI — Placement Detail
- [ ] Shows all fields + calculated margin + margin percentage
- [ ] Shows linked timesheets (empty for now, wired up in timesheet stories)
- [ ] Edit button → edit form

### UI — Edit Placement
- [ ] Admin can edit: title, rates, end date, notes, active status
- [ ] Cannot change contractor or client after creation (create a new placement instead)
- [ ] Rate changes only apply to future timesheets — flag this clearly in UI
- [ ] Closing a placement: set end_date + is_active=False

### API
- [ ] `POST /api/placements/` — create (admin only)
- [ ] `GET /api/placements/` — list (admin: all; contractor: own only)
- [ ] `GET /api/placements/{id}/` — detail (admin: full; contractor: own, rates hidden except contractor_rate)
- [ ] `PATCH /api/placements/{id}/` — update (admin only)

### Permissions
- [ ] Contractors can see their own placements but NOT the client_rate or margin
- [ ] Clerks can view placements but not create/edit

### Audit
- [ ] Placement creation: actor, contractor, client, both rates, timestamp
- [ ] Rate changes: actor, old rate → new rate, timestamp — **high sensitivity**
- [ ] Placement closure: actor, end date, timestamp

## Notes

- This is where the money lives. Rate changes are the most sensitive operation in the system.
- One contractor can have multiple active placements (different clients or even same client, different roles)
- `approval_mode` defaults to `agency_only` for MVP. Model the field, don't build dual approval logic yet.

### Smoke Test (Dev Portal)
- [ ] Navigate to Placements section — list page renders
- [ ] Create a new placement — form submits, placement appears in list with correct margin
- [ ] Edit placement rates — changes save, margin recalculates
- [ ] Close a placement — end date set, status updates
- [ ] Login as contractor — can see own placements, cannot see client rate or margin
- [ ] API: `GET /api/placements/` returns list with admin token
- [ ] Negative margin blocked, low margin warned

## Out of Scope
- Dual approval workflow activation
- Placement templates
- Automatic placement renewal
