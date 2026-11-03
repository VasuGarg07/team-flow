import { Download, FileText, Image, Paperclip, Trash2 } from "lucide-react";
import { useRef, useState, type ChangeEvent } from "react";
import {
  allowedUploadTypes,
  downloadAttachment,
  maxUploadBytes,
  useAttachments,
  useDeleteAttachment,
  useUploadAttachment,
} from "@/api/attachments";
import type { Attachment, Role } from "@/api/types";
import { ErrorBox, Loading, QueryError } from "@/components/PageState";
import { Button } from "@/components/ui/button";
import { errorMessage } from "@/lib/forms";
import { formatBytes } from "@/lib/format";
import { canDeleteAttachment } from "@/lib/permissions";

type AttachmentsSectionProps = {
  workspaceId: number;
  projectId: number;
  taskId: number;
  role: Role;
  userId: number;
};

export function AttachmentsSection({ workspaceId, projectId, taskId, role, userId }: AttachmentsSectionProps) {
  const attachments = useAttachments(workspaceId, projectId, taskId);
  const uploadAttachment = useUploadAttachment(workspaceId, projectId, taskId);
  const deleteAttachment = useDeleteAttachment(workspaceId, projectId, taskId);
  const fileInput = useRef<HTMLInputElement>(null);
  const [error, setError] = useState<string | null>(null);

  async function onFileChosen(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (file === undefined) return;
    setError(null);
    if (!allowedUploadTypes.includes(file.type)) {
      setError("Only PNG, JPG and PDF files are allowed.");
      return;
    }
    if (file.size > maxUploadBytes) {
      setError("The file is larger than 5 MB.");
      return;
    }
    try {
      await uploadAttachment.mutateAsync(file);
    } catch (uploadError) {
      setError(errorMessage(uploadError));
    }
  }

  async function onDownload(attachment: Attachment) {
    setError(null);
    try {
      await downloadAttachment(workspaceId, projectId, taskId, attachment);
    } catch (downloadError) {
      setError(errorMessage(downloadError));
    }
  }

  async function onDelete(attachment: Attachment) {
    setError(null);
    try {
      await deleteAttachment.mutateAsync(attachment.id);
    } catch (deleteError) {
      setError(errorMessage(deleteError));
    }
  }

  return (
    <section className="grid gap-3">
      <div className="flex items-center justify-between">
        <h3 className="flex items-center gap-1.5 text-sm font-semibold">
          <Paperclip size={14} />
          Attachments
        </h3>
        <Button variant="outline" onClick={() => fileInput.current?.click()} disabled={uploadAttachment.isPending}>
          {uploadAttachment.isPending ? "Uploading..." : "Upload"}
        </Button>
        <input
          ref={fileInput}
          type="file"
          accept={allowedUploadTypes.join(",")}
          onChange={onFileChosen}
          className="hidden"
          aria-label="Choose a file to upload"
        />
      </div>
      <p className="text-xs text-muted-foreground">PNG, JPG or PDF, up to 5 MB.</p>

      {error !== null && <ErrorBox message={error} />}
      {attachments.isPending && <Loading />}
      {attachments.isError && <QueryError error={attachments.error} />}
      {attachments.data?.length === 0 && <p className="text-sm text-muted-foreground">No attachments yet.</p>}
      {attachments.data !== undefined && attachments.data.length > 0 && (
        <ul className="divide-y rounded-md border">
          {attachments.data.map((attachment) => {
            const Icon = attachment.content_type === "PDF" ? FileText : Image;
            return (
              <li key={attachment.id} className="flex items-center gap-3 px-3 py-2 text-sm">
                <Icon size={16} className="shrink-0 text-muted-foreground" />
                <div className="min-w-0 flex-1">
                  <p className="truncate">{attachment.original_name}</p>
                  <p className="text-xs text-muted-foreground">{formatBytes(attachment.size_bytes)}</p>
                </div>
                <Button variant="ghost" size="icon" aria-label="Download" onClick={() => onDownload(attachment)}>
                  <Download size={16} />
                </Button>
                {canDeleteAttachment(role, userId, attachment) && (
                  <Button variant="ghost" size="icon" aria-label="Delete attachment" onClick={() => onDelete(attachment)}>
                    <Trash2 size={16} />
                  </Button>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
