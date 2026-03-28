"use client";

// TODO: Implement route guards for authenticated/role-based access
// This will wrap pages that require authentication and redirect to /login if not authenticated.
// It will also support role-based access control using the UserRole type.

import type { UserRole } from "@/lib/api/types";

export interface GuardProps {
  children: React.ReactNode;
  requiredRoles?: UserRole[];
}

export function AuthGuard({ children }: GuardProps) {
  // Placeholder: will check authentication status and redirect if needed
  return <>{children}</>;
}

export function RoleGuard({ children }: GuardProps) {
  // Placeholder: will check user role and show unauthorized if needed
  return <>{children}</>;
}
