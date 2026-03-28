import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { contractorApi } from "@/lib/api/endpoints";

export function useContractors() {
  return useQuery({
    queryKey: ["contractors"],
    queryFn: () => contractorApi.list(),
  });
}

export function useCreateContractor() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: {
      email: string;
      password: string;
      first_name: string;
      last_name: string;
      hourly_rate_default: number;
      phone?: string;
    }) => contractorApi.create(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["contractors"] }),
  });
}

export function useUpdateContractor() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: number;
      data: { first_name?: string; last_name?: string; hourly_rate_default?: number; phone?: string };
    }) => contractorApi.update(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["contractors"] }),
  });
}
