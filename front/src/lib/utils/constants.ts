import type { TimesheetStatus } from "@/lib/api/types";

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

export const ROLE_LABELS: Record<string, string> = {
  admin: "Admin",
  clerk: "Clerk",
  contractor: "Contractor",
  client_approver: "Client Approver",
};
