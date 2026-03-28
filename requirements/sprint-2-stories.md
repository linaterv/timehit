# Sprint 2 — Core Entities (Clients, Contractors, Placements)

## Story 2.1: Client CRUD API

**[Nyx] Client management endpoints**

As an admin/clerk, I want to manage clients so that we can track companies we contract with.

**Acceptance criteria:**
- [ ] Client model: name, contact_email, contact_phone, address, is_active, created_at, updated_at
- [ ] `GET /api/clients/` — list (admin, clerk)
- [ ] `POST /api/clients/` — create (admin, clerk)
- [ ] `GET /api/clients/{id}/` — detail
- [ ] `PATCH /api/clients/{id}/` — update
- [ ] `DELETE /api/clients/{id}/` — soft delete (deactivate)
- [ ] Audit log on all mutations
- [ ] Pagination + search by name

---

## Story 2.2: Contractor CRUD API

**[Nyx] Contractor management endpoints**

As an admin/clerk, I want to manage contractors so that we can track people we place at clients.

**Acceptance criteria:**
- [ ] Contractor model: linked to User (one-to-one), hourly_rate_default, phone, is_active, created_at
- [ ] `GET /api/contractors/` — list (admin, clerk)
- [ ] `POST /api/contractors/` — create (admin, clerk), also creates User with CONTRACTOR role
- [ ] `GET /api/contractors/{id}/` — detail
- [ ] `PATCH /api/contractors/{id}/` — update
- [ ] Audit log on all mutations

---

## Story 2.3: Placement CRUD API

**[Nyx] Placement management endpoints**

As an admin/clerk, I want to create placements linking contractors to clients with rates so that we can track active engagements.

**Acceptance criteria:**
- [ ] Placement model: contractor (FK), client (FK), client_rate, contractor_rate, start_date, end_date (nullable), approval_mode (AGENCY_ONLY for now), is_active, created_at
- [ ] `GET /api/placements/` — list with filters (client, contractor, active)
- [ ] `POST /api/placements/` — create (admin, clerk)
- [ ] `GET /api/placements/{id}/` — detail (includes client + contractor names)
- [ ] `PATCH /api/placements/{id}/` — update
- [ ] Margin auto-calculated in response (client_rate - contractor_rate)
- [ ] Audit log on all mutations

---

## Story 2.4: Clients UI

**[Eos] Client management page**

As an admin/clerk, I want a clients page so that I can manage client companies.

**Acceptance criteria:**
- [ ] Page at `/clients`
- [ ] Table with name, contact email, status
- [ ] Create/edit forms
- [ ] Search by name
- [ ] `data-testid` on key elements

---

## Story 2.5: Contractors UI

**[Eos] Contractor management page**

As an admin/clerk, I want a contractors page so that I can manage contractors.

**Acceptance criteria:**
- [ ] Page at `/contractors`
- [ ] Table with name, email, default rate, status
- [ ] Create form (creates user + contractor together)
- [ ] Edit form
- [ ] `data-testid` on key elements

---

## Story 2.6: Placements UI

**[Eos] Placement management page**

As an admin/clerk, I want a placements page so that I can manage contractor-client placements.

**Acceptance criteria:**
- [ ] Page at `/placements`
- [ ] Table with contractor name, client name, rates, margin, status
- [ ] Create form with dropdowns for contractor + client selection
- [ ] Edit form
- [ ] Filter by client, contractor, active status
- [ ] `data-testid` on key elements
