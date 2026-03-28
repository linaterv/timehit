# S002 — User Model & Roles

**Priority:** P0 — Foundation  
**Sprint:** 1  
**Assigned to:** TBD  
**Depends on:** None (built alongside S001)

## Story

As a **platform**, I need a user model with role-based access so that different user types see and do only what they're allowed to.

## User Model

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID | Primary key |
| `email` | EmailField | Unique, used as login identifier |
| `first_name` | CharField | |
| `last_name` | CharField | |
| `role` | CharField (choices) | `admin`, `clerk`, `contractor`, `client_approver` |
| `is_active` | BooleanField | Default True, soft-disable accounts |
| `phone` | CharField | Optional |
| `created_at` | DateTimeField | Auto |
| `updated_at` | DateTimeField | Auto |
| `created_by` | FK → User | Nullable (for bootstrap admin) |

## Roles & Permissions

| Role | Description |
|------|-------------|
| `admin` | Full control. Creates all other users, clients, contractors, placements. Can override approvals. |
| `clerk` | Agency staff. Reviews/approves timesheets, handles invoice queries. Cannot create placements. |
| `contractor` | Submits timesheets, views own invoices. Sees nothing else. |
| `client_approver` | Approves timesheets for their contractors only. Phase 2 — model the role now, restrict access later. |

## Acceptance Criteria

- [ ] Custom User model extends `AbstractBaseUser` (email as USERNAME_FIELD)
- [ ] `role` field with choices: `admin`, `clerk`, `contractor`, `client_approver`
- [ ] Role is required, no default — must be set on creation
- [ ] `is_active=False` blocks login
- [ ] All user fields exposed via DRF serializer (password excluded from reads)
- [ ] User creation via API requires admin role token auth
- [ ] `created_by` auto-populated from the requesting user

### Audit
- [ ] User creation logged: who created whom, when, role assigned
- [ ] User deactivation logged: who, when, by whom
- [ ] Role changes logged: old role → new role, who changed it, when

## Notes

- Use Django's `AbstractBaseUser` + `PermissionsMixin` for flexibility
- Custom manager with `create_user()` and `create_superuser()`
- Email normalization (lowercase)
- Don't use Django groups/permissions for role logic — keep it simple with the `role` field and a custom permission mixin or decorator

### Smoke Test (Dev Portal)
- [ ] Create user via Django admin or API — no errors
- [ ] Verify user appears in database (pgAdmin or API list)
- [ ] Login with newly created user — works
- [ ] Deactivated user cannot log in

## Out of Scope
- Self-registration (Phase 2)
- Profile pictures (Phase 2)
