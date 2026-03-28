"use client";

import { useState, useEffect, type FormEvent } from "react";
import { useUpdateUser } from "@/hooks/use-users";
import { ApiError } from "@/lib/api/client";
import type { User, UserRole } from "@/lib/api/types";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";

interface EditUserDialogProps {
  user: User | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function EditUserDialog({
  user,
  open,
  onOpenChange,
}: EditUserDialogProps) {
  const updateUser = useUpdateUser();
  const [email, setEmail] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [role, setRole] = useState<UserRole | "">("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string[]>>({});

  useEffect(() => {
    if (user) {
      setEmail(user.email);
      setFirstName(user.first_name);
      setLastName(user.last_name);
      setRole(user.role);
      setFieldErrors({});
    }
  }, [user]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!user) return;
    setFieldErrors({});

    try {
      await updateUser.mutateAsync({
        id: user.id,
        data: {
          email,
          first_name: firstName,
          last_name: lastName,
          role: role as UserRole,
        },
      });
      toast.success("User updated successfully.");
      onOpenChange(false);
    } catch (err) {
      if (err instanceof ApiError && err.status === 400 && err.data) {
        setFieldErrors(err.data as Record<string, string[]>);
      } else if (err instanceof ApiError && err.status === 403) {
        toast.error("You don't have permission to do this.");
      } else {
        toast.error("Something went wrong. Please try again.");
      }
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent data-testid="edit-user-dialog">
        <DialogHeader>
          <DialogTitle>Edit User</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="eu-firstname">First Name</Label>
              <Input
                id="eu-firstname"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                data-testid="user-firstname-input"
                required
              />
              {fieldErrors.first_name && (
                <p className="text-sm text-destructive">
                  {fieldErrors.first_name[0]}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="eu-lastname">Last Name</Label>
              <Input
                id="eu-lastname"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                data-testid="user-lastname-input"
                required
              />
              {fieldErrors.last_name && (
                <p className="text-sm text-destructive">
                  {fieldErrors.last_name[0]}
                </p>
              )}
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="eu-email">Email</Label>
            <Input
              id="eu-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              data-testid="user-email-input"
              required
            />
            {fieldErrors.email && (
              <p className="text-sm text-destructive">
                {fieldErrors.email[0]}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label>Role</Label>
            <Select
              value={role}
              onValueChange={(v) => setRole(v as UserRole)}
            >
              <SelectTrigger data-testid="user-role-select">
                <SelectValue placeholder="Select role" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ADMIN">Admin</SelectItem>
                <SelectItem value="CLERK">Clerk</SelectItem>
                <SelectItem value="CONTRACTOR">Contractor</SelectItem>
                <SelectItem value="CLIENT_APPROVER">Client Approver</SelectItem>
              </SelectContent>
            </Select>
            {fieldErrors.role && (
              <p className="text-sm text-destructive">
                {fieldErrors.role[0]}
              </p>
            )}
          </div>

          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={updateUser.isPending}>
              {updateUser.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving…
                </>
              ) : (
                "Save Changes"
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
