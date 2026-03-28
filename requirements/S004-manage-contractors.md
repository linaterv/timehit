# S004 — Admin Creates Contractor Users

**Priority:** P0  
**Sprint:** 1  
**Assigned to:** TBD  
**Depends on:** S002, S003

## Story

As an **admin**, I want to create contractor accounts so that contractors can log in, submit timesheets, and view their invoices.

## Contractor Model

The contractor is a **User** with `role=contractor` plus additional contractor-specific data:

| Field | Type | Notes |
|-------|------|-------|
| `user` | OneToOne → User | The login account |
| `company_name` | CharField | Optional — if contractor operates via a company |
| `tax_id` | CharField | VAT or tax registration number, optional |
| `bank_name` | CharField | For payment |
| `bank_account` | CharField | IBAN or account number |
| `address` | TextField | Mailing/invoicing address |
| `notes` | TextField | Internal notes, not visible to contractor |

## Acceptance Criteria

### UI — Create Contractor
- [ ] Admin navigates to "Contractors" section
- [ ] "Create Contractor" form: user fields (email, name, phone) + contractor fields (company name, tax ID, bank details, address)
- [ ] Creating a contractor creates both the User (role=contractor) and the Contractor profile in one step
- [ ] Initial password: auto-generated, displayed once (or set by admin with forced change)
- [ ] Validation: email unique, bank account required

### UI — Contractor List
- [ ] List of all contractors: name, email, company name, active status
- [ ] Searchable by name, email, or company
- [ ] Click → view/edit contractor details

### UI — Edit Contractor
- [ ] Admin can edit all contractor fields
- [ ] Admin can deactivate contractor (deactivates the User)
- [ ] Changes to bank details require confirmation ("Are you sure?")

### API
- [ ] `POST /api/contractors/` — create (admin only)
- [ ] `GET /api/contractors/` — list (admin only)
- [ ] `GET /api/contractors/{id}/` — detail (admin: full view; contractor: own profile only)
- [ ] `PATCH /api/contractors/{id}/` — update (admin only)

### Contractor's Own View
- [ ] Contractor can view their own profile after login
- [ ] Contractor can edit: phone, address, bank details (changes flagged for admin review — Phase 2, for now just allow edits)
- [ ] Contractor cannot see other contractors or any admin data

### Audit
- [ ] Contractor creation: actor, contractor email, timestamp
- [ ] Contractor profile update: actor, fields changed, timestamp
- [ ] Bank detail changes: actor, old → new (masked), timestamp — **high sensitivity**

## Notes

- Contractor profile is a separate model linked 1:1 to User, not extra fields on User
- This keeps the User model clean for all roles
- Bank details are sensitive — consider field-level encryption later (Phase 2), but store them for now

### Smoke Test (Dev Portal)
- [ ] Navigate to Contractors section — list page renders
- [ ] Create a new contractor — form submits, contractor appears in list
- [ ] Edit the contractor — changes save, reflected in list
- [ ] Update bank details — changes save, audit log captures masked values
- [ ] Deactivate contractor — status updates
- [ ] Login as contractor — can see own profile, cannot see other contractors or admin pages
- [ ] API: `GET /api/contractors/` returns list with admin token
- [ ] API: contractor token returns only own profile

## Out of Scope
- Contractor self-registration
- Document uploads (contracts, certificates)
- Bank detail change approval workflow
