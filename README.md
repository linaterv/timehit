# TimeHit

A recruitment contracting agency platform for managing contractor placements, timesheets, and invoicing.

## What It Does

TimeHit runs the core business cycle of an IT contracting agency:

1. **Agency signs a client** — agrees on a billing rate (e.g. €80/hr)
2. **Agency places a contractor** — agrees on a pay rate (e.g. €60/hr)
3. **Contractor logs hours** — monthly timesheet with daily entries
4. **Agency approves timesheet** — review and approve/reject workflow
5. **Invoices auto-generate** — paired invoices (client invoice + contractor payment) created from approved timesheets
6. **Agency collects margin** — difference between client rate and contractor rate

## Core Functionality

### Placements
- Link one contractor to one client with billing rate, pay rate, and dates
- Margin is derived (client rate − contractor rate), never stored separately
- Configurable approval mode per placement (agency-only or dual)

### Timesheets
- One timesheet = one month × one placement
- Daily entries: date, hours worked, optional note
- Workflow: `DRAFT → SUBMITTED → AGENCY_APPROVED → INVOICED`
- Rejection sends back to DRAFT with a note

### Invoices
- **Always generated in pairs** from approved timesheets — never created manually
- Client invoice: hours × client billing rate
- Contractor invoice: hours × contractor pay rate
- Immutable once generated
- Line items trace back to individual timesheet days
- Downloadable as PDF

### Users & Roles
| Role | Can Do |
|------|--------|
| **Admin** | Full control — create clients, contractors, placements. Override approvals. |
| **Clerk** | Review/approve timesheets, handle invoice queries. |
| **Contractor** | Submit timesheets, view own invoices and payment status. |
| **Client Approver** | Approve timesheets for their contractors only (Phase 2). |

### Audit Trail
Non-negotiable from day one. Every state change records:
- Who performed the action
- When
- What changed
- Human user vs API agent (and which one)

## Tech Decisions

| Layer | Choice | Rationale |
|-------|--------|-----------|
| **Backend + Frontend** | Django + HTMX | Monolith, fast to build, HTMX for interactivity without SPA complexity |
| **API** | Django REST Framework | Token auth for agents, session auth for browser users |
| **Database** | PostgreSQL | Reliable, good with financial data, strong constraints |
| **CSS** | Tailwind CSS or Bootstrap 5 | Rapid UI development |
| **PDF Generation** | WeasyPrint or ReportLab | Invoice PDF export |
| **Task Queue** | Celery or django-q | Monthly invoice generation, reminders (Phase 2) |

These are final unless a developer raises a blocking technical issue.

## MVP Scope (Phase 1)

1. Admin creates clients, contractors, and placements
2. Contractor submits monthly timesheets
3. Agency staff approves/rejects timesheets with notes
4. Approved timesheets auto-generate paired invoices
5. Invoices viewable in UI and downloadable as PDF
6. REST API for all entities with token auth
7. Audit log on all state changes

## Phase 2 Backlog

- Dual approval workflow (client approver step)
- Email notifications and reminders
- Margin analytics dashboard
- Contractor self-registration
- Multi-currency support
- Accounting integrations (Xero, QuickBooks)
- Credit notes and invoice corrections
- Bulk timesheet operations
- Reporting and exports beyond invoice PDFs

## Project Structure

```
timehit/
├── README.md
└── requirements/       # Detailed requirements and specs
```
