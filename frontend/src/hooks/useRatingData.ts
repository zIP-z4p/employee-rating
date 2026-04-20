// frontend/src/hooks/useRatingData.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ratingsApi } from '../api/client';

export const useSnapshot = (period: string, topN?: number) =>
  useQuery({
    queryKey: ['snapshot', period, topN],
    queryFn: () => ratingsApi.getSnapshot(period, topN).then(r => r.data),
    enabled: !!period,
  });

export const useEmployeeTrend = (employeeId: string | null, months = 6) =>
  useQuery({
    queryKey: ['trend', employeeId, months],
    queryFn: () =>
      ratingsApi.getEmployeeTrend(employeeId!, months).then(r => r.data),
    enabled: !!employeeId,
  });

export const useBuildSnapshot = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (period: string) =>
      ratingsApi.buildSnapshot(period).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['snapshot'] }),
  });
};

