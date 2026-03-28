import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { clientApi } from "@/lib/api/endpoints";
import type { Client } from "@/lib/api/types";

export function useClients(search?: string) {
  const params = search ? `search=${encodeURIComponent(search)}` : undefined;
  return useQuery({
    queryKey: ["clients", search],
    queryFn: () => clientApi.list(params),
  });
}

export function useCreateClient() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Client>) => clientApi.create(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["clients"] }),
  });
}

export function useUpdateClient() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Client> }) =>
      clientApi.update(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["clients"] }),
  });
}

export function useDeactivateClient() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => clientApi.deactivate(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["clients"] }),
  });
}
