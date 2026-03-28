"use client";

import { useState, useEffect, type FormEvent } from "react";
import type { Placement, Client, Contractor } from "@/lib/api/types";
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";

interface PlacementDialogProps {
  placement?: Placement | null;
  clients: Client[];
  contractors: Contractor[];
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: Record<string, unknown>) => Promise<void>;
  isPending: boolean;
}

export function PlacementDialog({
  placement,
  clients,
  contractors,
  open,
  onOpenChange,
  onSubmit,
  isPending,
}: PlacementDialogProps) {
  const isEdit = !!placement;
  const [clientId, setClientId] = useState("");
  const [contractorId, setContractorId] = useState("");
  const [clientRate, setClientRate] = useState("");
  const [contractorRate, setContractorRate] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string[]>>({});

  useEffect(() => {
    if (placement) {
      setClientId(String(placement.client.id));
      setContractorId(String(placement.contractor.id));
      setClientRate(String(placement.client_rate));
      setContractorRate(String(placement.contractor_rate));
      setStartDate(placement.start_date);
      setEndDate(placement.end_date || "");
    } else {
      setClientId("");
      setContractorId("");
      setClientRate("");
      setContractorRate("");
      setStartDate("");
      setEndDate("");
    }
    setFieldErrors({});
  }, [placement, open]);

  const margin =
    clientRate && contractorRate
      ? (parseFloat(clientRate) - parseFloat(contractorRate)).toFixed(2)
      : "—";

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setFieldErrors({});

    if (!clientId || !contractorId || !clientRate || !contractorRate || !startDate) {
      toast.error("All required fields must be filled.");
      return;
    }

    try {
      await onSubmit({
        client: parseInt(clientId),
        contractor: parseInt(contractorId),
        client_rate: parseFloat(clientRate),
        contractor_rate: parseFloat(contractorRate),
        start_date: startDate,
        end_date: endDate || null,
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
      <DialogContent
        className="max-w-lg"
        data-testid={isEdit ? "edit-placement-dialog" : "create-placement-dialog"}
      >
        <DialogHeader>
          <DialogTitle>
            {isEdit ? "Edit Placement" : "Create Placement"}
          </DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label>Client</Label>
            <Select value={clientId} onValueChange={(v) => setClientId(v ?? "")}>
              <SelectTrigger data-testid="placement-client-select">
                <SelectValue placeholder="Select client" />
              </SelectTrigger>
              <SelectContent>
                {clients.map((c) => (
                  <SelectItem key={c.id} value={String(c.id)}>
                    {c.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {fieldErrors.client && (
              <p className="text-sm text-destructive">{fieldErrors.client[0]}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label>Contractor</Label>
            <Select value={contractorId} onValueChange={(v) => setContractorId(v ?? "")}>
              <SelectTrigger data-testid="placement-contractor-select">
                <SelectValue placeholder="Select contractor" />
              </SelectTrigger>
              <SelectContent>
                {contractors.map((c) => (
                  <SelectItem key={c.id} value={String(c.id)}>
                    {c.user.first_name} {c.user.last_name} ({c.user.email})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {fieldErrors.contractor && (
              <p className="text-sm text-destructive">{fieldErrors.contractor[0]}</p>
            )}
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="pl-cr">Client Rate (€/hr)</Label>
              <Input
                id="pl-cr"
                type="number"
                step="0.01"
                min="0"
                value={clientRate}
                onChange={(e) => setClientRate(e.target.value)}
                data-testid="placement-client-rate-input"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="pl-cor">Contractor Rate (€/hr)</Label>
              <Input
                id="pl-cor"
                type="number"
                step="0.01"
                min="0"
                value={contractorRate}
                onChange={(e) => setContractorRate(e.target.value)}
                data-testid="placement-contractor-rate-input"
                required
              />
            </div>
            <div className="space-y-2">
              <Label>Margin (€/hr)</Label>
              <div
                className="flex h-8 items-center rounded-lg border bg-muted px-2.5 text-sm font-medium"
                data-testid="placement-margin-display"
              >
                {margin}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="pl-sd">Start Date</Label>
              <Input
                id="pl-sd"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                data-testid="placement-start-date-input"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="pl-ed">End Date</Label>
              <Input
                id="pl-ed"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                data-testid="placement-end-date-input"
              />
            </div>
          </div>

          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isPending} data-testid="placement-submit-button">
              {isPending ? (
                <><Loader2 className="mr-2 h-4 w-4 animate-spin" />{isEdit ? "Saving…" : "Creating…"}</>
              ) : (
                isEdit ? "Save Changes" : "Create Placement"
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
