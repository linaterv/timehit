"use client";

import { useState, useEffect, type FormEvent } from "react";
import type { Contractor } from "@/lib/api/types";
import { ApiError } from "@/lib/api/client";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";

interface CreateData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  hourly_rate_default: number;
  phone?: string;
}

interface EditData {
  first_name: string;
  last_name: string;
  hourly_rate_default: number;
  phone?: string;
}

interface ContractorDialogProps {
  contractor?: Contractor | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCreateSubmit?: (data: CreateData) => Promise<void>;
  onEditSubmit?: (data: EditData) => Promise<void>;
  isPending: boolean;
}

export function ContractorDialog({
  contractor,
  open,
  onOpenChange,
  onCreateSubmit,
  onEditSubmit,
  isPending,
}: ContractorDialogProps) {
  const isEdit = !!contractor;
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [rate, setRate] = useState("");
  const [phone, setPhone] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string[]>>({});

  useEffect(() => {
    if (contractor) {
      setEmail(contractor.user.email);
      setFirstName(contractor.user.first_name);
      setLastName(contractor.user.last_name);
      setRate(String(contractor.hourly_rate_default));
      setPhone(contractor.phone || "");
      setPassword("");
    } else {
      setEmail("");
      setPassword("");
      setFirstName("");
      setLastName("");
      setRate("");
      setPhone("");
    }
    setFieldErrors({});
  }, [contractor, open]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setFieldErrors({});

    if (!firstName || !lastName || !rate) {
      toast.error("Name and rate are required.");
      return;
    }
    if (!isEdit && (!email || !password)) {
      toast.error("Email and password are required for new contractors.");
      return;
    }

    try {
      if (isEdit && onEditSubmit) {
        await onEditSubmit({
          first_name: firstName,
          last_name: lastName,
          hourly_rate_default: parseFloat(rate),
          phone,
        });
      } else if (onCreateSubmit) {
        await onCreateSubmit({
          email,
          password,
          first_name: firstName,
          last_name: lastName,
          hourly_rate_default: parseFloat(rate),
          phone,
        });
      }
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
      <DialogContent data-testid={isEdit ? "edit-contractor-dialog" : "create-contractor-dialog"}>
        <DialogHeader>
          <DialogTitle>
            {isEdit ? "Edit Contractor" : "Create Contractor"}
          </DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="co-fn">First Name</Label>
              <Input
                id="co-fn"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                data-testid="contractor-firstname-input"
                required
              />
              {fieldErrors.first_name && (
                <p className="text-sm text-destructive">{fieldErrors.first_name[0]}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="co-ln">Last Name</Label>
              <Input
                id="co-ln"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                data-testid="contractor-lastname-input"
                required
              />
              {fieldErrors.last_name && (
                <p className="text-sm text-destructive">{fieldErrors.last_name[0]}</p>
              )}
            </div>
          </div>

          {!isEdit && (
            <>
              <div className="space-y-2">
                <Label htmlFor="co-email">Email</Label>
                <Input
                  id="co-email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  data-testid="contractor-email-input"
                  required
                />
                {fieldErrors.email && (
                  <p className="text-sm text-destructive">{fieldErrors.email[0]}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="co-pw">Password</Label>
                <Input
                  id="co-pw"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  data-testid="contractor-password-input"
                  required
                />
                {fieldErrors.password && (
                  <p className="text-sm text-destructive">{fieldErrors.password[0]}</p>
                )}
              </div>
            </>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="co-rate">Default Hourly Rate (€)</Label>
              <Input
                id="co-rate"
                type="number"
                step="0.01"
                min="0"
                value={rate}
                onChange={(e) => setRate(e.target.value)}
                data-testid="contractor-rate-input"
                required
              />
              {fieldErrors.hourly_rate_default && (
                <p className="text-sm text-destructive">{fieldErrors.hourly_rate_default[0]}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="co-phone">Phone</Label>
              <Input
                id="co-phone"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                data-testid="contractor-phone-input"
              />
            </div>
          </div>

          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isPending} data-testid="contractor-submit-button">
              {isPending ? (
                <><Loader2 className="mr-2 h-4 w-4 animate-spin" />{isEdit ? "Saving…" : "Creating…"}</>
              ) : (
                isEdit ? "Save Changes" : "Create Contractor"
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
