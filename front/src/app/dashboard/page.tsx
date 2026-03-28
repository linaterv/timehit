"use client";

import { useAuth } from "@/lib/auth/context";
import { ROLE_LABELS } from "@/lib/utils/constants";

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold" data-testid="dashboard-title">
        Dashboard
      </h1>
      {user && (
        <p className="text-muted-foreground" data-testid="dashboard-welcome">
          Welcome, {user.first_name || user.email}. You are logged in as{" "}
          <span className="font-medium">{ROLE_LABELS[user.role] ?? user.role}</span>.
        </p>
      )}
    </div>
  );
}
