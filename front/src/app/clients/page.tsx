"use client";

import { useState } from "react";
import {
  useClients,
  useCreateClient,
  useUpdateClient,
  useDeactivateClient,
} from "@/hooks/use-clients";
import type { Client } from "@/lib/api/types";
import { ClientDialog } from "@/components/clients/client-dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Plus,
  Search,
  MoreHorizontal,
  Pencil,
  XCircle,
  Building2,
  Loader2,
} from "lucide-react";
import { toast } from "sonner";
import { ApiError } from "@/lib/api/client";

export default function ClientsPage() {
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const { data, isLoading, error } = useClients(debouncedSearch);
  const createClient = useCreateClient();
  const updateClient = useUpdateClient();
  const deactivateClient = useDeactivateClient();

  const [createOpen, setCreateOpen] = useState(false);
  const [editClient, setEditClient] = useState<Client | null>(null);
  const [deactivateTarget, setDeactivateTarget] = useState<Client | null>(null);

  // Simple debounce on search
  let searchTimer: ReturnType<typeof setTimeout>;
  function handleSearch(value: string) {
    setSearch(value);
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => setDebouncedSearch(value), 300);
  }

  async function handleCreate(data: Partial<Client>) {
    await createClient.mutateAsync(data);
    toast.success("Client created successfully.");
  }

  async function handleUpdate(data: Partial<Client>) {
    if (!editClient) return;
    await updateClient.mutateAsync({ id: editClient.id, data });
    toast.success("Client updated successfully.");
  }

  async function handleDeactivate() {
    if (!deactivateTarget) return;
    try {
      await deactivateClient.mutateAsync(deactivateTarget.id);
      toast.success(`${deactivateTarget.name} has been deactivated.`);
      setDeactivateTarget(null);
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) {
        toast.error("You don't have permission to do this.");
      } else {
        toast.error("Something went wrong. Please try again.");
      }
    }
  }

  const clients = data?.results ?? [];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Clients</h1>
        <Button onClick={() => setCreateOpen(true)} data-testid="create-client-button">
          <Plus className="mr-2 h-4 w-4" />
          Create Client
        </Button>
      </div>

      <div className="relative max-w-sm">
        <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search by name…"
          value={search}
          onChange={(e) => handleSearch(e.target.value)}
          className="pl-9"
          data-testid="client-search-input"
        />
      </div>

      {isLoading ? (
        <div data-testid="loading-skeleton" className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </div>
      ) : error ? (
        <p className="text-sm text-destructive">Failed to load clients.</p>
      ) : clients.length === 0 ? (
        <div
          data-testid="empty-state"
          className="flex flex-col items-center justify-center gap-2 py-12 text-muted-foreground"
        >
          <Building2 className="h-10 w-10" />
          <p>No clients found.</p>
        </div>
      ) : (
        <Table data-testid="client-table">
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Contact Email</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="w-12" />
            </TableRow>
          </TableHeader>
          <TableBody>
            {clients.map((client) => (
              <TableRow key={client.id} data-testid={`client-row-${client.id}`}>
                <TableCell className="font-medium">{client.name}</TableCell>
                <TableCell>{client.contact_email || "—"}</TableCell>
                <TableCell>
                  {client.is_active ? (
                    <Badge variant="secondary" className="bg-green-100 text-green-700">
                      Active
                    </Badge>
                  ) : (
                    <Badge variant="secondary" className="bg-gray-100 text-gray-500">
                      Inactive
                    </Badge>
                  )}
                </TableCell>
                <TableCell>
                  <DropdownMenu>
                    <DropdownMenuTrigger
                      render={<Button variant="ghost" size="icon" className="h-8 w-8" />}
                    >
                      <MoreHorizontal className="h-4 w-4" />
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={() => setEditClient(client)}>
                        <Pencil className="mr-2 h-4 w-4" />
                        Edit
                      </DropdownMenuItem>
                      {client.is_active && (
                        <DropdownMenuItem
                          onClick={() => setDeactivateTarget(client)}
                          className="text-destructive focus:text-destructive"
                          data-testid={`deactivate-client-button-${client.id}`}
                        >
                          <XCircle className="mr-2 h-4 w-4" />
                          Deactivate
                        </DropdownMenuItem>
                      )}
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      {/* Create dialog */}
      <ClientDialog
        open={createOpen}
        onOpenChange={setCreateOpen}
        onSubmit={handleCreate}
        isPending={createClient.isPending}
      />

      {/* Edit dialog */}
      <ClientDialog
        client={editClient}
        open={!!editClient}
        onOpenChange={(open) => { if (!open) setEditClient(null); }}
        onSubmit={handleUpdate}
        isPending={updateClient.isPending}
      />

      {/* Deactivate confirmation */}
      <Dialog
        open={!!deactivateTarget}
        onOpenChange={(open) => { if (!open) setDeactivateTarget(null); }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Deactivate Client</DialogTitle>
            <DialogDescription>
              Are you sure you want to deactivate <strong>{deactivateTarget?.name}</strong>?
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeactivateTarget(null)}>Cancel</Button>
            <Button
              variant="destructive"
              onClick={handleDeactivate}
              disabled={deactivateClient.isPending}
            >
              {deactivateClient.isPending ? (
                <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Deactivating…</>
              ) : "Deactivate"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
