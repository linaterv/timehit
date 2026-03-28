"use client";

import { useState, useEffect, type FormEvent } from "react";
import type { Client } from "@/lib/api/types";
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

interface ClientDialogProps {
  client?: Client | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: Partial<Client>) => Promise<void>;
  isPending: boolean;
}

export function ClientDialog({
  client,
  open,
  onOpenChange,
  onSubmit,
  isPending,
}: ClientDialogProps) {
  const isEdit = !!client;
  const [name, setName] = useState("");
  const [contactEmail, setContactEmail] = useState("");
  const [contactPhone, setContactPhone] = useState("");
  const [address, setAddress] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string[]>>({});

  useEffect(() => {
    if (client) {
      setName(client.name);
      setContactEmail(client.contact_email);
      setContactPhone(client.contact_phone || "");
      setAddress(client.address || "");
    } else {
      setName("");
      setContactEmail("");
      setContactPhone("");
      setAddress("");
    }
    setFieldErrors({});
  }, [client, open]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setFieldErrors({});
    if (!name) {
      toast.error("Name is required.");
      return;
    }
    try {
      await onSubmit({
        name,
        contact_email: contactEmail,
        contact_phone: contactPhone,
        address,
      });
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
      <DialogContent data-testid={isEdit ? "edit-client-dialog" : "create-client-dialog"}>
        <DialogHeader>
          <DialogTitle>{isEdit ? "Edit Client" : "Create Client"}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="cl-name">Name</Label>
            <Input
              id="cl-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              data-testid="client-name-input"
              required
            />
            {fieldErrors.name && (
              <p className="text-sm text-destructive">{fieldErrors.name[0]}</p>
            )}
          </div>
          <div className="space-y-2">
            <Label htmlFor="cl-email">Contact Email</Label>
            <Input
              id="cl-email"
              type="email"
              value={contactEmail}
              onChange={(e) => setContactEmail(e.target.value)}
              data-testid="client-email-input"
            />
            {fieldErrors.contact_email && (
              <p className="text-sm text-destructive">
                {fieldErrors.contact_email[0]}
              </p>
            )}
          </div>
          <div className="space-y-2">
            <Label htmlFor="cl-phone">Contact Phone</Label>
            <Input
              id="cl-phone"
              value={contactPhone}
              onChange={(e) => setContactPhone(e.target.value)}
              data-testid="client-phone-input"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="cl-address">Address</Label>
            <Input
              id="cl-address"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              data-testid="client-address-input"
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isPending} data-testid="client-submit-button">
              {isPending ? (
                <><Loader2 className="mr-2 h-4 w-4 animate-spin" />{isEdit ? "Saving…" : "Creating…"}</>
              ) : (
                isEdit ? "Save Changes" : "Create Client"
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
