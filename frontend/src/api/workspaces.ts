import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiRequest } from "@/lib/api";
import type { Member, Role, Workspace } from "@/api/types";

export function useWorkspaces() {
  return useQuery({
    queryKey: ["workspaces"],
    queryFn: () => apiRequest<Workspace[]>("/workspaces"),
  });
}

export function useWorkspace(workspaceId: number) {
  return useQuery({
    queryKey: ["workspace", workspaceId],
    queryFn: () => apiRequest<Workspace>(`/workspaces/${workspaceId}`),
  });
}

export function useCreateWorkspace() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: { name: string }) =>
      apiRequest<unknown>("/workspaces", { method: "POST", body: input }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["workspaces"] }),
  });
}

export function useRenameWorkspace(workspaceId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: { name: string }) =>
      apiRequest<unknown>(`/workspaces/${workspaceId}`, { method: "PATCH", body: input }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workspaces"] });
      queryClient.invalidateQueries({ queryKey: ["workspace", workspaceId] });
    },
  });
}

export function useDeleteWorkspace(workspaceId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => apiRequest<unknown>(`/workspaces/${workspaceId}`, { method: "DELETE" }),
    onSuccess: () => {
      queryClient.removeQueries({ queryKey: ["workspace", workspaceId] });
      queryClient.invalidateQueries({ queryKey: ["workspaces"] });
    },
  });
}

export function useMembers(workspaceId: number) {
  return useQuery({
    queryKey: ["members", workspaceId],
    queryFn: () => apiRequest<Member[]>(`/workspaces/${workspaceId}/members`),
  });
}

export function useAddMember(workspaceId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: { email: string; role: Role }) =>
      apiRequest<unknown>(`/workspaces/${workspaceId}/members`, { method: "POST", body: input }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["members", workspaceId] }),
  });
}

export function useChangeMemberRole(workspaceId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: { userId: number; role: Role }) =>
      apiRequest<unknown>(`/workspaces/${workspaceId}/members/${input.userId}`, {
        method: "PATCH",
        body: { role: input.role },
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["members", workspaceId] }),
  });
}

export function useRemoveMember(workspaceId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (userId: number) =>
      apiRequest<unknown>(`/workspaces/${workspaceId}/members/${userId}`, { method: "DELETE" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["members", workspaceId] }),
  });
}
