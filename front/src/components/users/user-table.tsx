"use client";

import type { User } from "@/lib/api/types";
import { ROLE_LABELS } from "@/lib/utils/constants";
import { formatFullName } from "@/lib/utils/formatting";
import { Badge } from "@/components/ui/badge";
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
import { Button } from "@/components/ui/button";
import { MoreHorizontal, Pencil, UserX } from "lucide-react";

const ROLE_VARIANT: Record<string, string> = {
  admin: "bg-red-100 text-red-700 hover:bg-red-100",
  clerk: "bg-blue-100 text-blue-700 hover:bg-blue-100",
  contractor: "bg-green-100 text-green-700 hover:bg-green-100",
  client_approver: "bg-amber-100 text-amber-700 hover:bg-amber-100",
};

interface UserTableProps {
  users: User[];
  onEdit: (user: User) => void;
  onDeactivate: (user: User) => void;
}

export function UserTable({ users, onEdit, onDeactivate }: UserTableProps) {
  return (
    <Table data-testid="user-table">
      <TableHeader>
        <TableRow>
          <TableHead>Name</TableHead>
          <TableHead>Email</TableHead>
          <TableHead>Role</TableHead>
          <TableHead>Status</TableHead>
          <TableHead className="w-12" />
        </TableRow>
      </TableHeader>
      <TableBody>
        {users.map((user) => (
          <TableRow key={user.id} data-testid={`user-row-${user.id}`}>
            <TableCell className="font-medium">
              {formatFullName(user.first_name, user.last_name) || "—"}
            </TableCell>
            <TableCell>{user.email}</TableCell>
            <TableCell>
              <Badge
                variant="secondary"
                className={ROLE_VARIANT[user.role] ?? ""}
              >
                {ROLE_LABELS[user.role] ?? user.role}
              </Badge>
            </TableCell>
            <TableCell>
              {user.is_active ? (
                <span className="inline-flex items-center gap-1.5 text-sm">
                  <span className="h-2 w-2 rounded-full bg-green-500" />
                  Active
                </span>
              ) : (
                <span className="inline-flex items-center gap-1.5 text-sm text-muted-foreground">
                  <span className="h-2 w-2 rounded-full bg-gray-400" />
                  Inactive
                </span>
              )}
            </TableCell>
            <TableCell>
              <DropdownMenu>
                <DropdownMenuTrigger
                  render={<Button variant="ghost" size="icon" className="h-8 w-8" />}
                >
                  <MoreHorizontal className="h-4 w-4" />
                  <span className="sr-only">Actions</span>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={() => onEdit(user)}>
                    <Pencil className="mr-2 h-4 w-4" />
                    Edit
                  </DropdownMenuItem>
                  {user.is_active && (
                    <DropdownMenuItem
                      onClick={() => onDeactivate(user)}
                      className="text-destructive focus:text-destructive"
                      data-testid={`deactivate-user-button-${user.id}`}
                    >
                      <UserX className="mr-2 h-4 w-4" />
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
  );
}
