export type UserRole = "admin" | "clerk" | "contractor" | "client_approver";

export type TimesheetStatus =
  | "draft"
  | "submitted"
  | "agency_approved"
  | "client_approved"
  | "invoiced";

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  is_active: boolean;
}

export interface Client {
  id: number;
  name: string;
  contact_email: string;
  is_active: boolean;
}

export interface Contractor {
  id: number;
  user: User;
  default_rate: number;
  is_active: boolean;
}

export interface PlacementSummary {
  id: number;
  contractor_name: string;
  client_name: string;
  job_title: string;
}

export interface Placement {
  id: number;
  contractor: Contractor;
  client: Client;
  job_title: string;
  start_date: string;
  end_date: string | null;
  client_rate: number;
  contractor_rate: number;
  is_active: boolean;
}

export interface TimesheetEntry {
  id: number;
  date: string;
  hours: number;
  note: string | null;
}

export interface Timesheet {
  id: number;
  placement: PlacementSummary;
  month: string; // "2025-03"
  status: TimesheetStatus;
  entries: TimesheetEntry[];
  total_hours: number;
  submitted_at: string | null;
  rejection_note: string | null;
  created_at: string;
  updated_at: string;
}

export interface Invoice {
  id: number;
  invoice_number: string;
  type: "client" | "contractor";
  timesheet: Timesheet;
  total_amount: number;
  status: "draft" | "sent" | "paid";
  created_at: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}
