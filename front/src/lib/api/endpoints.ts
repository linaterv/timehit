import { apiClient } from "./client";
import type {
  AuthTokens,
  LoginCredentials,
  PaginatedResponse,
  Timesheet,
  Placement,
  User,
  Client,
  Contractor,
  Invoice,
} from "./types";

// Auth
export const authApi = {
  login: (credentials: LoginCredentials) =>
    apiClient<AuthTokens>("/api/auth/login/", {
      method: "POST",
      body: JSON.stringify(credentials),
    }),
  refresh: (refresh: string) =>
    apiClient<{ access: string }>("/api/auth/refresh/", {
      method: "POST",
      body: JSON.stringify({ refresh }),
    }),
  logout: (refresh: string) =>
    apiClient<void>("/api/auth/logout/", {
      method: "POST",
      body: JSON.stringify({ refresh }),
    }),
  me: () => apiClient<User>("/api/auth/me/"),
};

// Timesheets
export const timesheetApi = {
  list: (params?: string) =>
    apiClient<PaginatedResponse<Timesheet>>(
      `/api/timesheets/${params ? `?${params}` : ""}`
    ),
  get: (id: number) => apiClient<Timesheet>(`/api/timesheets/${id}/`),
  create: (data: Partial<Timesheet>) =>
    apiClient<Timesheet>("/api/timesheets/", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (id: number, data: Partial<Timesheet>) =>
    apiClient<Timesheet>(`/api/timesheets/${id}/`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
  submit: (id: number) =>
    apiClient<Timesheet>(`/api/timesheets/${id}/submit/`, { method: "POST" }),
  approve: (id: number) =>
    apiClient<Timesheet>(`/api/timesheets/${id}/approve/`, { method: "POST" }),
  reject: (id: number, note: string) =>
    apiClient<Timesheet>(`/api/timesheets/${id}/reject/`, {
      method: "POST",
      body: JSON.stringify({ note }),
    }),
};

// Placements
export const placementApi = {
  list: (params?: string) =>
    apiClient<PaginatedResponse<Placement>>(
      `/api/placements/${params ? `?${params}` : ""}`
    ),
  get: (id: number) => apiClient<Placement>(`/api/placements/${id}/`),
  create: (data: Partial<Placement>) =>
    apiClient<Placement>("/api/placements/", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (id: number, data: Partial<Placement>) =>
    apiClient<Placement>(`/api/placements/${id}/`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
};

// Users
export const userApi = {
  list: (params?: string) =>
    apiClient<PaginatedResponse<User>>(
      `/api/users/${params ? `?${params}` : ""}`
    ),
  get: (id: number) => apiClient<User>(`/api/users/${id}/`),
  create: (data: Partial<User> & { password: string }) =>
    apiClient<User>("/api/users/", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (id: number, data: Partial<User>) =>
    apiClient<User>(`/api/users/${id}/`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
  deactivate: (id: number) =>
    apiClient<void>(`/api/users/${id}/`, { method: "DELETE" }),
};

// Clients
export const clientApi = {
  list: (params?: string) =>
    apiClient<PaginatedResponse<Client>>(
      `/api/clients/${params ? `?${params}` : ""}`
    ),
  get: (id: number) => apiClient<Client>(`/api/clients/${id}/`),
};

// Contractors
export const contractorApi = {
  list: (params?: string) =>
    apiClient<PaginatedResponse<Contractor>>(
      `/api/contractors/${params ? `?${params}` : ""}`
    ),
  get: (id: number) => apiClient<Contractor>(`/api/contractors/${id}/`),
};

// Invoices
export const invoiceApi = {
  list: (params?: string) =>
    apiClient<PaginatedResponse<Invoice>>(
      `/api/invoices/${params ? `?${params}` : ""}`
    ),
  get: (id: number) => apiClient<Invoice>(`/api/invoices/${id}/`),
};
