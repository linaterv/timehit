export type UserRole = "ADMIN" | "CLERK" | "CONTRACTOR" | "CLIENT_APPROVER";

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
  date_joined?: string;
}

export interface Client {
  id: number;
  name: string;
  contact_email: string;
  contact_phone: string;
  address: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Contractor {
  id: number;
  user: User;
  hourly_rate_default: number;
  phone: string;
  is_active: boolean;
  created_at: string;
}

export interface Placement {
  id: number;
  contractor: Contractor;
  client: Client;
  client_rate: number;
  contractor_rate: number;
  margin: number;
  start_date: string;
  end_date: string | null;
  approval_mode: string;
  is_active: boolean;
  created_at: string;
}

export interface PlacementSummary {
  id: number;
  contractor_name: string;
  client_name: string;
  job_title: string;
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
  month: string;
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
  user: User;
}

export interface LoginCredentials {
  email: string;
  password: string;
}
