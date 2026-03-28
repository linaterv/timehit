import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { placementApi } from "@/lib/api/endpoints";

interface PlacementFilters {
  client?: number;
  contractor?: number;
  is_active?: boolean;
}

function buildParams(filters?: PlacementFilters): string | undefined {
  if (!filters) return undefined;
  const parts: string[] = [];
  if (filters.client) parts.push(`client=${filters.client}`);
  if (filters.contractor) parts.push(`contractor=${filters.contractor}`);
  if (filters.is_active !== undefined)
    parts.push(`is_active=${filters.is_active}`);
  return parts.length ? parts.join("&") : undefined;
}

export function usePlacements(filters?: PlacementFilters) {
  return useQuery({
    queryKey: ["placements", filters],
    queryFn: () => placementApi.list(buildParams(filters)),
  });
}

export function useCreatePlacement() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: {
      contractor: number;
      client: number;
      client_rate: number;
      contractor_rate: number;
      start_date: string;
      end_date?: string | null;
    }) => placementApi.create(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["placements"] }),
  });
}

export function useUpdatePlacement() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: number;
      data: Record<string, unknown>;
    }) => placementApi.update(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["placements"] }),
  });
}
