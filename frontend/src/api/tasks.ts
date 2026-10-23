import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiRequest } from "@/lib/api";
import type { SortField, Task, TaskPage, TaskPriority, TaskStatus } from "@/api/types";

export type TaskFilters = {
  status: TaskStatus | "";
  priority: TaskPriority | "";
  assigneeId: string;
  sortBy: SortField;
  order: "asc" | "desc";
  page: number;
};

export const tasksPerPage = 20;

export type TaskInput = {
  name: string;
  description: string | null;
  assignee_id: number | null;
  priority: TaskPriority;
  story_points: number;
  due_date: string | null;
};

function buildQueryString(filters: TaskFilters): string {
  const params = new URLSearchParams();
  if (filters.status !== "") params.set("status", filters.status);
  if (filters.priority !== "") params.set("priority", filters.priority);
  if (filters.assigneeId !== "") params.set("assignee_id", filters.assigneeId);
  params.set("sort_by", filters.sortBy);
  params.set("order", filters.order);
  params.set("page", String(filters.page));
  params.set("limit", String(tasksPerPage));
  return params.toString();
}

export function useTasks(workspaceId: number, projectId: number, filters: TaskFilters) {
  return useQuery({
    queryKey: ["tasks", projectId, filters],
    queryFn: () =>
      apiRequest<TaskPage>(
        `/workspaces/${workspaceId}/projects/${projectId}/tasks?${buildQueryString(filters)}`,
      ),
    placeholderData: keepPreviousData,
  });
}

export function useTask(workspaceId: number, projectId: number, taskId: number) {
  return useQuery({
    queryKey: ["task", taskId],
    queryFn: () =>
      apiRequest<Task>(`/workspaces/${workspaceId}/projects/${projectId}/tasks/${taskId}`),
  });
}

export function useCreateTask(workspaceId: number, projectId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: TaskInput) =>
      apiRequest<unknown>(`/workspaces/${workspaceId}/projects/${projectId}/tasks`, {
        method: "POST",
        body: input,
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["tasks", projectId] }),
  });
}

export function useUpdateTask(workspaceId: number, projectId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: Partial<TaskInput & { status: TaskStatus }> & { id: number }) => {
      const { id, ...body } = input;
      return apiRequest<unknown>(`/workspaces/${workspaceId}/projects/${projectId}/tasks/${id}`, {
        method: "PATCH",
        body,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks", projectId] });
      queryClient.invalidateQueries({ queryKey: ["task"] });
    },
  });
}

export function useDeleteTask(workspaceId: number, projectId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (taskId: number) =>
      apiRequest<unknown>(`/workspaces/${workspaceId}/projects/${projectId}/tasks/${taskId}`, {
        method: "DELETE",
      }),
    onSuccess: (_result, taskId) => {
      queryClient.invalidateQueries({ queryKey: ["tasks", projectId] });
      queryClient.removeQueries({ queryKey: ["task", taskId] });
    },
  });
}
