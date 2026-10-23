import { Pencil, Trash2, X } from "lucide-react";
import { useEffect, useState, type ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import { useDeleteTask, useTask, useUpdateTask } from "@/api/tasks";
import type { TaskStatus } from "@/api/types";
import { useMembers, useWorkspace } from "@/api/workspaces";
import { useAuth } from "@/auth/AuthContext";
import { Avatar } from "@/components/Avatar";
import { ConfirmDialog } from "@/components/ConfirmDialog";
import { ErrorBox, Loading, QueryError } from "@/components/PageState";
import { StatusSelect } from "@/components/StatusSelect";
import { TaskForm } from "@/components/TaskForm";
import { PriorityBadge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Modal } from "@/components/ui/modal";
import { errorMessage } from "@/lib/forms";
import { formatDateTime } from "@/lib/format";
import { useNumericParam } from "@/lib/params";
import { canDeleteTask, canEditTask } from "@/lib/permissions";
import type { User } from "@/api/auth";

function Detail({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="grid grid-cols-[110px_1fr] items-center gap-3 text-sm">
      <dt className="text-muted-foreground">{label}</dt>
      <dd>{children}</dd>
    </div>
  );
}

function Person({ user }: { user: User | null }) {
  if (user === null) {
    return <span className="text-muted-foreground">Unassigned</span>;
  }
  return (
    <span className="flex items-center gap-2">
      <Avatar user={user} />
      {user.first_name} {user.last_name}
    </span>
  );
}

export function TaskPanel() {
  const workspaceId = useNumericParam("workspaceId");
  const projectId = useNumericParam("projectId");
  const taskId = useNumericParam("taskId");
  const navigate = useNavigate();
  const { user } = useAuth();
  const workspace = useWorkspace(workspaceId);
  const members = useMembers(workspaceId);
  const task = useTask(workspaceId, projectId, taskId);
  const updateTask = useUpdateTask(workspaceId, projectId);
  const deleteTask = useDeleteTask(workspaceId, projectId);
  const [editOpen, setEditOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  const closeUrl = `/app/${workspaceId}/projects/${projectId}`;

  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      const dialogOpen = document.querySelector("dialog[open]") !== null;
      if (event.key === "Escape" && !dialogOpen) {
        navigate(closeUrl);
      }
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [navigate, closeUrl]);

  async function changeStatus(status: TaskStatus) {
    setActionError(null);
    try {
      await updateTask.mutateAsync({ id: taskId, status });
    } catch (error) {
      setActionError(errorMessage(error));
    }
  }

  async function confirmDelete() {
    setActionError(null);
    try {
      await deleteTask.mutateAsync(taskId);
      navigate(closeUrl);
    } catch (error) {
      setActionError(errorMessage(error));
    }
  }

  const myRole = workspace.data?.role;
  const data = task.data;
  const canEdit = data !== undefined && myRole !== undefined && user !== null && canEditTask(myRole, user.id, data);
  const canDelete =
    data !== undefined && myRole !== undefined && user !== null && canDeleteTask(myRole, user.id, data);

  return (
    <div className="fixed inset-0 z-40 flex justify-end bg-foreground/30" onClick={() => navigate(closeUrl)}>
      <aside
        onClick={(event) => event.stopPropagation()}
        className="h-full w-full max-w-md overflow-y-auto border-l bg-card p-6 shadow-lg"
      >
        <div className="mb-4 flex items-center justify-between">
          <span className="text-xs text-muted-foreground">Task details</span>
          <Button variant="ghost" size="icon" aria-label="Close panel" onClick={() => navigate(closeUrl)}>
            <X size={16} />
          </Button>
        </div>

        {task.isPending && <Loading />}
        {task.isError && <QueryError error={task.error} />}
        {data !== undefined && (
          <div className="grid gap-6">
            <div>
              <h2 className="text-xl font-semibold tracking-tight">{data.name}</h2>
              <p className="mt-2 whitespace-pre-wrap text-sm text-muted-foreground">
                {data.description ?? "No description."}
              </p>
            </div>

            {actionError !== null && !deleteOpen && <ErrorBox message={actionError} />}

            <dl className="grid gap-3">
              <Detail label="Status">
                <StatusSelect status={data.status} canEdit={canEdit} onChange={changeStatus} />
              </Detail>
              <Detail label="Priority">
                <PriorityBadge priority={data.priority} />
              </Detail>
              <Detail label="Assignee">
                <Person user={data.assignee} />
              </Detail>
              <Detail label="Reporter">
                <Person user={data.reporter} />
              </Detail>
              <Detail label="Due">{data.due_date === null ? "None" : formatDateTime(data.due_date)}</Detail>
              <Detail label="Story points">{data.story_points}</Detail>
              <Detail label="Created">{formatDateTime(data.created_at)}</Detail>
              <Detail label="Updated">{formatDateTime(data.updated_at)}</Detail>
            </dl>

            {(canEdit || canDelete) && (
              <div className="flex gap-2">
                {canEdit && (
                  <Button variant="outline" onClick={() => setEditOpen(true)} disabled={members.data === undefined}>
                    <Pencil size={14} />
                    Edit
                  </Button>
                )}
                {canDelete && (
                  <Button
                    variant="outline"
                    onClick={() => {
                      setActionError(null);
                      setDeleteOpen(true);
                    }}
                  >
                    <Trash2 size={14} />
                    Delete
                  </Button>
                )}
              </div>
            )}
          </div>
        )}

        <Modal open={editOpen} title="Edit task" onClose={() => setEditOpen(false)}>
          {members.data !== undefined && data !== undefined && (
            <TaskForm
              workspaceId={workspaceId}
              projectId={projectId}
              members={members.data}
              task={data}
              onDone={() => setEditOpen(false)}
            />
          )}
        </Modal>
        <ConfirmDialog
          open={deleteOpen}
          title="Delete task"
          message={`Delete "${data?.name ?? ""}"? This cannot be undone.`}
          confirmLabel="Delete"
          error={actionError}
          isPending={deleteTask.isPending}
          onConfirm={confirmDelete}
          onClose={() => setDeleteOpen(false)}
        />
      </aside>
    </div>
  );
}
