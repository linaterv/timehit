# S003 — Admin Creates Agency Users (Admins & Clerks)

**Priority:** P0  
**Sprint:** 1  
**Assigned to:** TBD  
**Depends on:** S001, S002

## Story

As an **admin**, I want to create other admin and clerk accounts so that agency staff can access the platform and manage daily operations.

## Acceptance Criteria

### UI — Create Agency User
- [ ] Admin sees "Users" section in navigation
- [ ] "Create User" form with fields: email, first name, last name, role (admin or clerk), phone (optional)
- [ ] Password is auto-generated and shown once on creation (or sent via email — Phase 2)
- [ ] Alternatively: admin sets initial password, user must change on first login
- [ ] Validation: email must be unique, all required fields present
- [ ] Success → redirect to user list with confirmation message

### UI — User List
- [ ] Admin sees a list of all users with: name, email, role, active status, created date
- [ ] Filterable by role
- [ ] Searchable by name or email
- [ ] Click a user → view/edit details

### UI — Edit User
- [ ] Admin can edit: first name, last name, phone, role, active status
- [ ] Admin can deactivate a user (soft delete — `is_active=False`)
- [ ] Admin cannot edit their own role (prevent locking yourself out)
- [ ] Admin can reset another user's password

### API
- [ ] `POST /api/users/` — create user (admin only)
- [ ] `GET /api/users/` — list users (admin only)
- [ ] `GET /api/users/{id}/` — user detail (admin only)
- [ ] `PATCH /api/users/{id}/` — update user (admin only)
- [ ] No `DELETE` — deactivate instead

### Permissions
- [ ] Only users with `role=admin` can access user management
- [ ] Clerks, contractors, client approvers get 403 on these endpoints
- [ ] API enforces same permissions via token auth

### Audit
- [ ] User creation: actor, new user email, role, timestamp
- [ ] User update: actor, fields changed (old → new), timestamp
- [ ] User deactivation: actor, target user, timestamp
- [ ] Password reset: actor, target user, timestamp (never log passwords)

## Notes

- HTMX for form submission and list filtering — no full page reloads
- Use Django messages framework for success/error feedback
- Keep the UI simple — table layout, no fancy components yet

### Smoke Test (Dev Portal)
- [ ] Navigate to Users section — list page renders
- [ ] Create a new clerk user — form submits, user appears in list
- [ ] Edit the clerk — changes save, reflected in list
- [ ] Deactivate the clerk — status updates in list
- [ ] Search/filter users — results update (HTMX)
- [ ] API: `GET /api/users/` returns user list with token auth
- [ ] Non-admin user cannot access Users section (403)

## Out of Scope
- Bulk user creation
- User invitations via email (Phase 2)
- Role-specific dashboards (separate story)
