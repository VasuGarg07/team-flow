import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiBlob, apiRequest } from "@/lib/api";
import type { Attachment } from "@/api/types";

export const maxUploadBytes = 5 * 1024 * 1024;
export const allowedUploadTypes = ["image/png", "image/jpeg", "application/pdf"];

function attachmentsPath(workspaceId: number, projectId: number, taskId: number): string {
  return `/workspaces/${workspaceId}/projects/${projectId}/tasks/${taskId}/attachments`;
}

export function useAttachments(workspaceId: number, projectId: number, taskId: number) {
  return useQuery({
    queryKey: ["attachments", taskId],
    queryFn: () => apiRequest<Attachment[]>(attachmentsPath(workspaceId, projectId, taskId)),
  });
}

export function useUploadAttachment(workspaceId: number, projectId: number, taskId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => {
      const formData = new FormData();
      formData.append("file", file);
      return apiRequest<unknown>(attachmentsPath(workspaceId, projectId, taskId), {
        method: "POST",
        body: formData,
      });
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["attachments", taskId] }),
  });
}

export function useDeleteAttachment(workspaceId: number, projectId: number, taskId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (attachmentId: number) =>
      apiRequest<unknown>(`${attachmentsPath(workspaceId, projectId, taskId)}/${attachmentId}`, {
        method: "DELETE",
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["attachments", taskId] }),
  });
}

export async function downloadAttachment(
  workspaceId: number,
  projectId: number,
  taskId: number,
  attachment: Attachment,
): Promise<void> {
  const blob = await apiBlob(`${attachmentsPath(workspaceId, projectId, taskId)}/${attachment.id}`);
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = attachment.original_name;
  link.click();
  URL.revokeObjectURL(url);
}
