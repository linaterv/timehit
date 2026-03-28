# Sprint 1 — Foundation & Auth

## Story 1.1: Backend Scaffolding

**[Nyx] Django project scaffolding**

As a developer, I want a properly structured Django project so that we have a foundation to build on.

**Acceptance criteria:**
- [ ] Django project created in `back/` with app name `timehit`
- [ ] Settings configured for PostgreSQL (host=localhost, port=5432, db=timehit, user=timehit, password=a, schema=timehit)
- [ ] DRF installed and configured
- [ ] drf-spectacular configured with Swagger UI at `/api/docs/`
- [ ] CORS configured to allow localhost:3000
- [ ] Custom User model (email-based login, no username) with roles: ADMIN, CLERK, CONTRACTOR, CLIENT_APPROVER
- [ ] Initial migration runs cleanly
- [ ] `requirements.txt` or `pyproject.toml` with all dependencies
- [ ] Django runs on port 8000

**Notes:** Use `timehit` schema in PostgreSQL. Role field on User model as a CharField with choices.

---

## Story 1.2: Frontend Scaffolding

**[Eos] Next.js project scaffolding**

As a developer, I want a properly structured Next.js project so that we have a frontend foundation.

**Acceptance criteria:**
- [ ] Next.js 14+ (App Router) project created in `front/`
- [ ] TypeScript configured
- [ ] Shadcn/ui initialized with Tailwind
- [ ] Basic layout with sidebar navigation placeholder
- [ ] API client utility configured to hit `localhost:8000/api/`
- [ ] Environment variable for API base URL
- [ ] Runs on port 3000

---

## Story 1.3: JWT Authentication API

**[Nyx] JWT auth endpoints**

As a user, I want to log in with email and password so that I can access the system securely.

**Acceptance criteria:**
- [ ] `POST /api/auth/login/` — returns access + refresh tokens
- [ ] `POST /api/auth/refresh/` — refreshes access token
- [ ] `POST /api/auth/logout/` — blacklists refresh token
- [ ] `GET /api/auth/me/` — returns current user profile (email, role)
- [ ] All endpoints documented in Swagger
- [ ] Audit log entry on login (actor, timestamp, action)

**Notes:** Use simplejwt. Access token 30min, refresh token 1 day.

---

## Story 1.4: Login UI

**[Eos] Login page**

As a user, I want a login page so that I can authenticate and access the platform.

**Acceptance criteria:**
- [ ] Login page at `/login`
- [ ] Email + password form with validation
- [ ] Calls `POST /api/auth/login/`
- [ ] Stores tokens (httpOnly cookie or secure storage)
- [ ] Redirects to `/dashboard` on success
- [ ] Shows error message on invalid credentials
- [ ] `data-testid` on email input, password input, submit button, error message
- [ ] Loading state on submit button

---

## Story 1.5: Admin User Management API

**[Nyx] User CRUD for admins**

As an admin, I want to create and manage user accounts so that I can onboard team members and clients.

**Acceptance criteria:**
- [ ] `GET /api/users/` — list users (admin only), filterable by role
- [ ] `POST /api/users/` — create user (admin only) with email, password, role, first_name, last_name
- [ ] `GET /api/users/{id}/` — get user detail
- [ ] `PATCH /api/users/{id}/` — update user (admin only)
- [ ] `DELETE /api/users/{id}/` — soft delete / deactivate (admin only)
- [ ] Non-admin users get 403
- [ ] Audit log on create, update, delete (actor, timestamp, action, target user)
- [ ] Pagination on list endpoint

---

## Story 1.6: User Management UI

**[Eos] Admin user management page**

As an admin, I want a user management page so that I can create and manage users from the UI.

**Acceptance criteria:**
- [ ] Page at `/admin/users` (protected, admin only)
- [ ] Table listing users with columns: name, email, role, status
- [ ] "Create User" button → modal/form with email, password, role, first/last name
- [ ] Edit user via row action
- [ ] Deactivate user via row action with confirmation
- [ ] Role filter dropdown
- [ ] `data-testid` on key interactive elements
- [ ] Loading and empty states

---

## Story 1.7: Seed Admin User

**[Nyx] Management command for initial admin**

As a deployer, I want a management command to create the first admin user so that I can bootstrap the system.

**Acceptance criteria:**
- [ ] `python manage.py create_admin --email admin@timehit.local --password admin` creates an ADMIN user
- [ ] Skips if user already exists (idempotent)
- [ ] Prints confirmation message
