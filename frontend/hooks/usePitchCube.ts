/**
 * React Query Hooks for PitchCube API
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../lib/api/client';

// Query Keys
export const queryKeys = {
  products: ['products'] as const,
  product: (id: string | null) => ['products', id] as const,
  posters: ['posters'] as const,
  poster: (id: string | null) => ['posters', id] as const,
  videos: ['videos'] as const,
  video: (id: string | null) => ['videos', id] as const,
  voices: ['voices'] as const,
  voice: (id: string | null) => ['voices', id] as const,
  profile: ['profile'] as const,
  subscription: ['subscription'] as const,
  plans: ['plans'] as const,
  projects: ['projects'] as const,
  project: (id: string | null) => ['projects', id] as const,
  dashboard: (timeRange: string) => ['dashboard', timeRange] as const,
  userStats: ['user-stats'] as const,
  generationStats: (period: string) => ['generation-stats', period] as const,
  platformStats: (period: string) => ['platform-stats', period] as const,
  batch: (id: string | null) => ['batch', id] as const,
};

// ============ Products ============

export function useProducts(options?: { skip?: number; limit?: number }) {
  return useQuery({
    queryKey: [...queryKeys.products, options],
    queryFn: () => apiClient.listProducts(options?.skip, options?.limit),
  });
}

export function useProduct(id: string) {
  return useQuery({
    queryKey: queryKeys.product(id),
    queryFn: () => apiClient.getProduct(id),
    enabled: !!id,
  });
}

export function useCreateProduct() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: apiClient.createProduct,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.products });
    },
  });
}

export function useUpdateProduct() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => apiClient.updateProduct(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.product(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.products });
    },
  });
}

export function useDeleteProduct() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: apiClient.deleteProduct,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.products });
    },
  });
}

export function useAnalyzeProduct() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: apiClient.analyzeProduct,
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.product(id) });
    },
  });
}

// ============ Posters ============

export function usePosterTemplates() {
  return useQuery({
    queryKey: ['poster-templates'],
    queryFn: apiClient.getPosterTemplates,
  });
}

export function usePosterStatus(id: string | null, options?: { interval?: number }) {
  return useQuery({
    queryKey: queryKeys.poster(id),
    queryFn: () => apiClient.getPosterStatus(id!),
    enabled: !!id,
    refetchInterval: (data: any) => {
      if (data?.status === 'processing' && options?.interval !== 0) {
        return options?.interval || 2000;
      }
      return false;
    },
  });
}

export function useGeneratePoster() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: apiClient.generatePoster,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.posters });
    },
  });
}

// ============ Videos ============

export function useVideoTemplates() {
  return useQuery({
    queryKey: ['video-templates'],
    queryFn: apiClient.getVideoTemplates,
  });
}

export function useVideoStatus(id: string | null, options?: { interval?: number }) {
  return useQuery({
    queryKey: queryKeys.video(id),
    queryFn: () => apiClient.getVideoStatus(id!),
    enabled: !!id,
    refetchInterval: (data: any) => {
      if (data?.status === 'processing' && options?.interval !== 0) {
        return options?.interval || 3000;
      }
      return false;
    },
  });
}

export function useGenerateVideo() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: apiClient.generateVideo,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.videos });
    },
  });
}

// ============ Voices ============

export function useVoices(options?: { style?: string; gender?: string }) {
  return useQuery({
    queryKey: [...queryKeys.voices, options],
    queryFn: () => apiClient.getVoices(options?.style, options?.gender),
  });
}

export function useVoiceStatus(id: string | null, options?: { interval?: number }) {
  return useQuery({
    queryKey: queryKeys.voice(id),
    queryFn: () => apiClient.getVoiceStatus(id!),
    enabled: !!id,
    refetchInterval: (data: any) => {
      if (data?.status === 'processing' && options?.interval !== 0) {
        return options?.interval || 2000;
      }
      return false;
    },
  });
}

export function useGenerateVoice() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: apiClient.generateVoice,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.voices });
    },
  });
}

// ============ Auth ============

export function useProfile() {
  return useQuery({
    queryKey: queryKeys.profile,
    queryFn: apiClient.getProfile,
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: apiClient.updateProfile,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.profile });
    },
  });
}

// ============ Payments ============

export function usePlans() {
  return useQuery({
    queryKey: queryKeys.plans,
    queryFn: apiClient.getPlans,
  });
}

export function useSubscription() {
  return useQuery({
    queryKey: queryKeys.subscription,
    queryFn: apiClient.getSubscription,
  });
}

export function useCreateCheckout() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ planId, billingCycle }: { planId: string; billingCycle?: string }) =>
      apiClient.createCheckout(planId, billingCycle),
    onSuccess: (_, { planId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.subscription });
    },
  });
}

// ============ Health ============

export function useHealthCheck() {
  return useQuery({
    queryKey: ['health'],
    queryFn: apiClient.healthCheck,
    refetchInterval: 30000,
  });
}

// ============ Collaboration ============

export function useProjects(options?: { skip?: number; limit?: number }) {
  return useQuery({
    queryKey: [...queryKeys.projects, options],
    queryFn: () => apiClient.listProjects(options?.skip, options?.limit),
  });
}

export function useProject(id: string) {
  return useQuery({
    queryKey: queryKeys.project(id),
    queryFn: () => apiClient.getProject(id),
    enabled: !!id,
  });
}

export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: apiClient.createProject,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects });
    },
  });
}

export function useUpdateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => apiClient.updateProject(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.project(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.projects });
    },
  });
}

export function useDeleteProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: apiClient.deleteProject,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects });
    },
  });
}

export function useInviteCollaborator() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ projectId, data }: { projectId: string; data: any }) =>
      apiClient.inviteCollaborator(projectId, data),
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.project(projectId) });
    },
  });
}

export function useRemoveCollaborator() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ projectId, userId }: { projectId: string; userId: string }) =>
      apiClient.removeCollaborator(projectId, userId),
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.project(projectId) });
    },
  });
}

// ============ Analytics ============

export function useDashboard(timeRange = '7d') {
  return useQuery({
    queryKey: queryKeys.dashboard(timeRange),
    queryFn: () => apiClient.getDashboard(timeRange),
  });
}

export function useUserStats() {
  return useQuery({
    queryKey: queryKeys.userStats,
    queryFn: apiClient.getUserStats,
  });
}

export function useGenerationStats(period = '7d') {
  return useQuery({
    queryKey: queryKeys.generationStats(period),
    queryFn: () => apiClient.getGenerationStats(period),
  });
}

export function usePlatformStats(period = '7d') {
  return useQuery({
    queryKey: queryKeys.platformStats(period),
    queryFn: () => apiClient.getPlatformStats(period),
  });
}

export function useTrackEvent() {
  return useMutation({
    mutationFn: ({ eventType, data }: { eventType: string; data: Record<string, any> }) =>
      apiClient.trackEvent(eventType, data),
  });
}

// ============ Batch Generation ============

interface BatchGenerateResult {
  batch_id: string;
  status: string;
  message: string;
}

export function useBatchGenerate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: apiClient.batchGenerate,
    onSuccess: (data: BatchGenerateResult) => {
      if (data.batch_id) {
        queryClient.invalidateQueries({ queryKey: queryKeys.batch(data.batch_id) });
      }
      queryClient.invalidateQueries({ queryKey: queryKeys.posters });
      queryClient.invalidateQueries({ queryKey: queryKeys.videos });
      queryClient.invalidateQueries({ queryKey: queryKeys.voices });
    },
  });
}

export function useBatchStatus(batchId: string | null) {
  return useQuery({
    queryKey: batchId ? queryKeys.batch(batchId) : ['batch', null],
    queryFn: () => apiClient.getBatchStatus(batchId!),
    enabled: !!batchId,
    refetchInterval: (data: any) => {
      if (data?.status === 'processing') {
        return 3000;
      }
      return false;
    },
  });
}

export function useCancelBatch() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: apiClient.cancelBatch,
    onSuccess: (_, batchId) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.batch(batchId) });
    },
  });
}
