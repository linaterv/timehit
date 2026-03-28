"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth/context";
import { useUsers, useDeactivateUser } from "@/hooks/use-users";
import type { User, UserRole } from "@/lib/api/types";
import { UserTable } from "@/components/users/user-table";
import { CreateUserDialog } from "@/components/users/create-user-dialog";
import { EditUserDialog } from "@/components/users/edit-user-dialog";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { Plus, Users, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { ApiError } from "@/lib/api/client";

export default function AdminUsersPage() {
  const router = useRouter();
  const { user: currentUser, isLoading: authLoading } = useAuth();
  const [roleFilter, setRoleFilter] = useState<UserRole | "all">("all");
  const activeFilter = roleFilter === "all" ? "" : roleFilter;
  const { data, isLoading, error } = useUsers(activeFilter);
  const deactivateUser = useDeactivateUser();

  const [createOpen, setCreateOpen] = useState(false);
  const [editUser, setEditUser] = useState<User | null>(null);
  const [deactivateTarget, setDeactivateTarget] = useState<User | null>(null);

  // Redirect non-admins
  useEffect(() => {
    if (!authLoading && currentUser && currentUser.role !== "admin") {
      router.replace("/dashboard");
    }
  }, [authLoading, currentUser, router]);

  if (authLoading || (!currentUser)) {
    return (
      <div data-testid="loading-skeleton" className="space-y-4 p-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-10 w-full" />
      </div>
    );
  }

  if (currentUser.role !== "admin") return null;

  async function handleDeactivate() {
    if (!deactivateTarget) return;
    try {
      await deactivateUser.mutateAsync(deactivateTarget.id);
      toast.success(`${deactivateTarget.email} has been deactivated.`);
      setDeactivateTarget(null);
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) {
        toast.error("You don't have permission to do this.");
      } else {
        toast.error("Something went wrong. Please try again.");
      }
    }
  }

  const users = data?.results ?? [];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">User Management</h1>
        <Button
          onClick={() => setCreateOpen(true)}
          data-testid="create-user-button"
        >
          <Plus className="mr-2 h-4 w-4" />
          Create User
        </Button>
      </div>

      <div className="flex items-center gap-4">
        <Select
          value={roleFilter}
          onValueChange={(v) => setRoleFilter((v ?? "all") as UserRole | "all")}
        >
          <SelectTrigger className="w-48" data-testid="role-filter">
            <SelectValue placeholder="Filter by role" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Roles</SelectItem>
            <SelectItem value="admin">Admin</SelectItem>
            <SelectItem value="clerk">Clerk</SelectItem>
            <SelectItem value="contractor">Contractor</SelectItem>
            <SelectItem value="client_approver">Client Approver</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {isLoading ? (
        <div data-testid="loading-skeleton" className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </div>
      ) : error ? (
        <p className="text-sm text-destructive">
          Failed to load users. Please try again.
        </p>
      ) : users.length === 0 ? (
        <div
          data-testid="empty-state"
          className="flex flex-col items-center justify-center gap-2 py-12 text-muted-foreground"
        >
          <Users className="h-10 w-10" />
          <p>No users found.</p>
        </div>
      ) : (
        <UserTable
          users={users}
          onEdit={(u) => setEditUser(u)}
          onDeactivate={(u) => setDeactivateTarget(u)}
        />
      )}

      <CreateUserDialog open={createOpen} onOpenChange={setCreateOpen} />

      <EditUserDialog
        user={editUser}
        open={!!editUser}
        onOpenChange={(open) => {
          if (!open) setEditUser(null);
        }}
      />

      {/* Deactivation confirmation dialog */}
      <Dialog
        open={!!deactivateTarget}
        onOpenChange={(open) => {
          if (!open) setDeactivateTarget(null);
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Deactivate User</DialogTitle>
            <DialogDescription>
              Are you sure you want to deactivate{" "}
              <strong>{deactivateTarget?.email}</strong>? They will no longer
              be able to log in.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDeactivateTarget(null)}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDeactivate}
              disabled={deactivateUser.isPending}
            >
              {deactivateUser.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Deactivating…
                </>
              ) : (
                "Deactivate"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
