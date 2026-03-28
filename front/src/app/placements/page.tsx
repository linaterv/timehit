"use client";

import { useState } from "react";
import {
  usePlacements,
  useCreatePlacement,
  useUpdatePlacement,
} from "@/hooks/use-placements";
import { useClients } from "@/hooks/use-clients";
import { useContractors } from "@/hooks/use-contractors";
import type { Placement } from "@/lib/api/types";
import { PlacementDialog } from "@/components/placements/placement-dialog";
import { formatCurrency, formatDate, formatFullName } from "@/lib/utils/formatting";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
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
import { Plus, MoreHorizontal, Pencil, Briefcase } from "lucide-react";
import { toast } from "sonner";

export default function PlacementsPage() {
  const [clientFilter, setClientFilter] = useState<number | undefined>();
  const [contractorFilter, setContractorFilter] = useState<number | undefined>();
  const [activeFilter, setActiveFilter] = useState<boolean | undefined>();

  const { data, isLoading, error } = usePlacements({
    client: clientFilter,
    contractor: contractorFilter,
    is_active: activeFilter,
  });
  const { data: clientsData } = useClients();
  const { data: contractorsData } = useContractors();
  const createPlacement = useCreatePlacement();
  const updatePlacement = useUpdatePlacement();

  const [createOpen, setCreateOpen] = useState(false);
  const [editPlacement, setEditPlacement] = useState<Placement | null>(null);

  const placements = data?.results ?? [];
  const clients = clientsData?.results ?? [];
  const contractors = contractorsData?.results ?? [];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Placements</h1>
        <Button
          onClick={() => setCreateOpen(true)}
          data-testid="create-placement-button"
        >
          <Plus className="mr-2 h-4 w-4" />
          Create Placement
        </Button>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <Select
          value={clientFilter ? String(clientFilter) : "all"}
          onValueChange={(v) => setClientFilter(!v || v === "all" ? undefined : parseInt(v))}
        >
          <SelectTrigger className="w-48" data-testid="placement-filter-client">
            <SelectValue placeholder="Filter by client" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Clients</SelectItem>
            {clients.map((c) => (
              <SelectItem key={c.id} value={String(c.id)}>
                {c.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select
          value={contractorFilter ? String(contractorFilter) : "all"}
          onValueChange={(v) =>
            setContractorFilter(!v || v === "all" ? undefined : parseInt(v))
          }
        >
          <SelectTrigger className="w-48" data-testid="placement-filter-contractor">
            <SelectValue placeholder="Filter by contractor" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Contractors</SelectItem>
            {contractors.map((c) => (
              <SelectItem key={c.id} value={String(c.id)}>
                {formatFullName(c.user.first_name, c.user.last_name)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select
          value={activeFilter === undefined ? "all" : String(activeFilter)}
          onValueChange={(v) =>
            setActiveFilter(!v || v === "all" ? undefined : v === "true")
          }
        >
          <SelectTrigger className="w-36" data-testid="placement-filter-active">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="true">Active</SelectItem>
            <SelectItem value="false">Inactive</SelectItem>
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
        <p className="text-sm text-destructive">Failed to load placements.</p>
      ) : placements.length === 0 ? (
        <div
          data-testid="empty-state"
          className="flex flex-col items-center justify-center gap-2 py-12 text-muted-foreground"
        >
          <Briefcase className="h-10 w-10" />
          <p>No placements found.</p>
        </div>
      ) : (
        <Table data-testid="placement-table">
          <TableHeader>
            <TableRow>
              <TableHead>Contractor</TableHead>
              <TableHead>Client</TableHead>
              <TableHead className="text-right">Client Rate</TableHead>
              <TableHead className="text-right">Contractor Rate</TableHead>
              <TableHead className="text-right">Margin</TableHead>
              <TableHead>Start</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="w-12" />
            </TableRow>
          </TableHeader>
          <TableBody>
            {placements.map((p) => {
              const margin = p.client_rate - p.contractor_rate;
              return (
                <TableRow key={p.id} data-testid={`placement-row-${p.id}`}>
                  <TableCell className="font-medium">
                    {formatFullName(
                      p.contractor.user.first_name,
                      p.contractor.user.last_name
                    )}
                  </TableCell>
                  <TableCell>{p.client.name}</TableCell>
                  <TableCell className="text-right">
                    {formatCurrency(p.client_rate)}/hr
                  </TableCell>
                  <TableCell className="text-right">
                    {formatCurrency(p.contractor_rate)}/hr
                  </TableCell>
                  <TableCell
                    className={`text-right font-medium ${
                      margin > 0
                        ? "text-green-600"
                        : margin < 0
                          ? "text-red-600"
                          : ""
                    }`}
                    data-testid={`placement-margin-${p.id}`}
                  >
                    {formatCurrency(margin)}/hr
                  </TableCell>
                  <TableCell>{formatDate(p.start_date)}</TableCell>
                  <TableCell>
                    {p.is_active ? (
                      <Badge
                        variant="secondary"
                        className="bg-green-100 text-green-700"
                      >
                        Active
                      </Badge>
                    ) : (
                      <Badge
                        variant="secondary"
                        className="bg-gray-100 text-gray-500"
                      >
                        Inactive
                      </Badge>
                    )}
                  </TableCell>
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger
                        render={
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8"
                          />
                        }
                      >
                        <MoreHorizontal className="h-4 w-4" />
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem
                          onClick={() => setEditPlacement(p)}
                        >
                          <Pencil className="mr-2 h-4 w-4" />
                          Edit
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      )}

      {/* Create */}
      <PlacementDialog
        clients={clients}
        contractors={contractors}
        open={createOpen}
        onOpenChange={setCreateOpen}
        onSubmit={async (data) => {
          await createPlacement.mutateAsync(
            data as {
              contractor: number;
              client: number;
              client_rate: number;
              contractor_rate: number;
              start_date: string;
              end_date?: string | null;
            }
          );
          toast.success("Placement created successfully.");
        }}
        isPending={createPlacement.isPending}
      />

      {/* Edit */}
      <PlacementDialog
        placement={editPlacement}
        clients={clients}
        contractors={contractors}
        open={!!editPlacement}
        onOpenChange={(open) => {
          if (!open) setEditPlacement(null);
        }}
        onSubmit={async (data) => {
          if (!editPlacement) return;
          await updatePlacement.mutateAsync({ id: editPlacement.id, data });
          toast.success("Placement updated successfully.");
        }}
        isPending={updatePlacement.isPending}
      />
    </div>
  );
}
