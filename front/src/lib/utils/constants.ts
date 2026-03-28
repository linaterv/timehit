import type { TimesheetStatus, UserRole } from "@/lib/api/types";

export const TIMESHEET_STATUS_COLORS: Record<TimesheetStatus, string> = {
  draft: "bg-gray-100 text-gray-700",
  submitted: "bg-blue-100 text-blue-700",
  agency_approved: "bg-amber-100 text-amber-700",
  client_approved: "bg-green-100 text-green-700",
  invoiced: "bg-purple-100 text-purple-700",
};

export const TIMESHEET_STATUS_LABELS: Record<TimesheetStatus, string> = {
  draft: "Draft",
  submitted: "Submitted",
  agency_approved: "Agency Approved",
  client_approved: "Client Approved",
  invoiced: "Invoiced",
};

export const ROLE_LABELS: Record<UserRole, string> = {
  ADMIN: "Admin",
  CLERK: "Clerk",
  CONTRACTOR: "Contractor",
  CLIENT_APPROVER: "Client Approver",
};

export const ROLE_BADGE_COLORS: Record<UserRole, string> = {
  ADMIN: "bg-red-100 text-red-700 hover:bg-red-100",
  CLERK: "bg-blue-100 text-blue-700 hover:bg-blue-100",
  CONTRACTOR: "bg-green-100 text-green-700 hover:bg-green-100",
  CLIENT_APPROVER: "bg-amber-100 text-amber-700 hover:bg-amber-100",
};
