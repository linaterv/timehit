"use client";

import { useState } from "react";
import {
  useContractors,
  useCreateContractor,
  useUpdateContractor,
} from "@/hooks/use-contractors";
import type { Contractor } from "@/lib/api/types";
import { ContractorDialog } from "@/components/contractors/contractor-dialog";
import { formatFullName, formatCurrency } from "@/lib/utils/formatting";
import { Button } from "@/components/ui/button";
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
import { Plus, MoreHorizontal, Pencil, Users } from "lucide-react";
import { toast } from "sonner";

export default function ContractorsPage() {
  const { data, isLoading, error } = useContractors();
  const createContractor = useCreateContractor();
  const updateContractor = useUpdateContractor();

  const [createOpen, setCreateOpen] = useState(false);
  const [editContractor, setEditContractor] = useState<Contractor | null>(null);

  const contractors = data?.results ?? [];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Contractors</h1>
        <Button
          onClick={() => setCreateOpen(true)}
          data-testid="create-contractor-button"
        >
          <Plus className="mr-2 h-4 w-4" />
          Create Contractor
        </Button>
      </div>

      {isLoading ? (
        <div data-testid="loading-skeleton" className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </div>
      ) : error ? (
        <p className="text-sm text-destructive">Failed to load contractors.</p>
      ) : contractors.length === 0 ? (
        <div
          data-testid="empty-state"
          className="flex flex-col items-center justify-center gap-2 py-12 text-muted-foreground"
        >
          <Users className="h-10 w-10" />
          <p>No contractors found.</p>
        </div>
      ) : (
        <Table data-testid="contractor-table">
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Email</TableHead>
              <TableHead>Default Rate</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="w-12" />
            </TableRow>
          </TableHeader>
          <TableBody>
            {contractors.map((c) => (
              <TableRow key={c.id} data-testid={`contractor-row-${c.id}`}>
                <TableCell className="font-medium">
                  {formatFullName(c.user.first_name, c.user.last_name) || "—"}
                </TableCell>
                <TableCell>{c.user.email}</TableCell>
                <TableCell>{formatCurrency(c.hourly_rate_default)}/hr</TableCell>
                <TableCell>
                  {c.is_active ? (
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
                      <DropdownMenuItem onClick={() => setEditContractor(c)}>
                        <Pencil className="mr-2 h-4 w-4" />
                        Edit
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      {/* Create */}
      <ContractorDialog
        open={createOpen}
        onOpenChange={setCreateOpen}
        onCreateSubmit={async (data) => {
          await createContractor.mutateAsync(data);
          toast.success("Contractor created successfully.");
        }}
        isPending={createContractor.isPending}
      />

      {/* Edit */}
      <ContractorDialog
        contractor={editContractor}
        open={!!editContractor}
        onOpenChange={(open) => { if (!open) setEditContractor(null); }}
        onEditSubmit={async (data) => {
          if (!editContractor) return;
          await updateContractor.mutateAsync({ id: editContractor.id, data });
          toast.success("Contractor updated successfully.");
        }}
        isPending={updateContractor.isPending}
      />
    </div>
  );
}
