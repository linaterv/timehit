# S001 — Admin Login & Logout

**Priority:** P0 — Must be first  
**Sprint:** 1  
**Assigned to:** TBD

## Story

As an **admin**, I want to log into the platform with my credentials so that I can access the admin dashboard and manage the system.

As a **logged-in user**, I want to log out so that my session is terminated securely.

## Acceptance Criteria

### Login
- [ ] Login page at `/login/` with email and password fields
- [ ] Successful login redirects to dashboard (`/dashboard/`)
- [ ] Failed login shows error message — no leaking whether email exists
- [ ] Session-based auth for browser users (Django sessions)
- [ ] Login is rate-limited (5 attempts per minute per IP)
- [ ] Password stored as hashed (Django default bcrypt/PBKDF2)

### Logout
- [ ] Logout button visible on all authenticated pages
- [ ] Logout terminates the session and redirects to `/login/`
- [ ] POST-only logout (no GET logout to prevent CSRF tricks)

### Admin Bootstrap
- [ ] First admin account created via `manage.py createsuperuser`
- [ ] Admin user sees the dashboard after login (can be a placeholder page for now)
- [ ] Unauthenticated users are redirected to `/login/` on any protected route

### Audit
- [ ] Login success logged: who, when, IP
- [ ] Login failure logged: attempted email, when, IP
- [ ] Logout logged: who, when

## Notes

- No registration flow — admin accounts are created via CLI or by other admins (see S003)
- Django's built-in auth is fine here, extend the User model with a `role` field
- User model: `email` as username (not a separate username field)

### Smoke Test (Dev Portal)
- [ ] Navigate to `/login/` — page renders without errors
- [ ] Login with valid credentials — redirects to dashboard
- [ ] Login with invalid credentials — shows error, no crash
- [ ] Click logout — redirected to login page
- [ ] Access `/dashboard/` while logged out — redirected to login

## Out of Scope
- Password reset flow (Phase 2)
- Two-factor authentication (Phase 2)
- OAuth / SSO (Phase 2)
