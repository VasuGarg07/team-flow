import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiRequest } from "@/lib/api";
import type { Project } from "@/api/types";

export type ProjectInput = {
  name: string;
  description: string | null;
};

export function useProjects(workspaceId: number) {
  return useQuery({
    queryKey: ["projects", workspaceId],
    queryFn: () => apiRequest<Project[]>(`/workspaces/${workspaceId}/projects`),
  });
}

export function useProject(workspaceId: number, projectId: number) {
  return useQuery({
    queryKey: ["project", projectId],
    queryFn: () => apiRequest<Project>(`/workspaces/${workspaceId}/projects/${projectId}`),
  });
}

export function useCreateProject(workspaceId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: ProjectInput) =>
      apiRequest<unknown>(`/workspaces/${workspaceId}/projects`, { method: "POST", body: input }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["projects", workspaceId] }),
  });
}

export function useUpdateProject(workspaceId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: ProjectInput & { id: number }) =>
      apiRequest<unknown>(`/workspaces/${workspaceId}/projects/${input.id}`, {
        method: "PATCH",
        body: { name: input.name, description: input.description },
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects", workspaceId] });
      queryClient.invalidateQueries({ queryKey: ["project"] });
    },
  });
}

export function useDeleteProject(workspaceId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (projectId: number) =>
      apiRequest<unknown>(`/workspaces/${workspaceId}/projects/${projectId}`, { method: "DELETE" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["projects", workspaceId] }),
  });
}
