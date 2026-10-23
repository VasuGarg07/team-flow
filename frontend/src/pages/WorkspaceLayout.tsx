import { zodResolver } from "@hookform/resolvers/zod";
import { FolderKanban, Pencil, Trash2, Users } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { z } from "zod";
import { useDeleteWorkspace, useRenameWorkspace, useWorkspace } from "@/api/workspaces";
import { ConfirmDialog } from "@/components/ConfirmDialog";
import { ErrorBox, Loading, QueryError } from "@/components/PageState";
import { RoleBadge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Modal } from "@/components/ui/modal";
import { errorMessage, showServerError } from "@/lib/forms";
import { useNumericParam } from "@/lib/params";
import { canDeleteWorkspace, canManageWorkspace } from "@/lib/permissions";
import { cn } from "@/lib/utils";

const renameSchema = z.object({
  name: z.string().trim().min(1, "Enter a name").max(100, "Max 100 characters"),
});

type RenameValues = z.infer<typeof renameSchema>;

function RenameForm({ workspaceId, currentName, onDone }: { workspaceId: number; currentName: string; onDone: () => void }) {
  const rename = useRenameWorkspace(workspaceId);
  const [serverError, setServerError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm<RenameValues>({
    resolver: zodResolver(renameSchema),
    defaultValues: { name: currentName },
  });

  async function onSubmit(values: RenameValues) {
    setServerError(null);
    try {
      await rename.mutateAsync(values);
      onDone();
    } catch (error) {
      setServerError(showServerError(error, setError));
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="grid gap-4" noValidate>
      <div className="grid gap-1.5">
        <Input aria-label="Workspace name" aria-invalid={errors.name !== undefined} {...register("name")} />
        {errors.name !== undefined && <span className="text-xs text-destructive">{errors.name.message}</span>}
      </div>
      {serverError !== null && <ErrorBox message={serverError} />}
      <div className="flex justify-end gap-2">
        <Button type="button" variant="outline" onClick={onDone}>
          Cancel
        </Button>
        <Button type="submit" disabled={rename.isPending}>
          Save
        </Button>
      </div>
    </form>
  );
}

const tabClass = ({ isActive }: { isActive: boolean }) =>
  cn(
    "flex items-center gap-1.5 border-b-2 px-1 pb-2 text-sm font-medium",
    isActive ? "border-brand text-foreground" : "border-transparent text-muted-foreground hover:text-foreground",
  );

export function WorkspaceLayout() {
  const workspaceId = useNumericParam("workspaceId");
  const workspace = useWorkspace(workspaceId);
  const deleteWorkspace = useDeleteWorkspace(workspaceId);
  const navigate = useNavigate();
  const [renameOpen, setRenameOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  if (workspace.isPending) {
    return <Loading />;
  }
  if (workspace.isError) {
    return (
      <QueryError error={workspace.error}>
        <Link to="/app" className="mt-3 inline-block text-sm font-medium text-brand hover:underline">
          Back to workspaces
        </Link>
      </QueryError>
    );
  }

  const { name, role } = workspace.data;

  async function confirmDelete() {
    setDeleteError(null);
    try {
      await deleteWorkspace.mutateAsync();
      navigate("/app");
    } catch (error) {
      setDeleteError(errorMessage(error));
    }
  }

  return (
    <div className="grid gap-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-semibold tracking-tight">{name}</h1>
          <RoleBadge role={role} />
        </div>
        <div className="flex gap-2">
          {canManageWorkspace(role) && (
            <Button variant="outline" onClick={() => setRenameOpen(true)}>
              <Pencil size={14} />
              Rename
            </Button>
          )}
          {canDeleteWorkspace(role) && (
            <Button variant="outline" onClick={() => setDeleteOpen(true)}>
              <Trash2 size={14} />
              Delete
            </Button>
          )}
        </div>
      </div>

      <nav className="flex gap-5 border-b">
        <NavLink to={`/app/${workspaceId}`} end className={tabClass}>
          <FolderKanban size={14} />
          Projects
        </NavLink>
        <NavLink to={`/app/${workspaceId}/members`} className={tabClass}>
          <Users size={14} />
          Members
        </NavLink>
      </nav>

      <Outlet />

      <Modal open={renameOpen} title="Rename workspace" onClose={() => setRenameOpen(false)}>
        <RenameForm workspaceId={workspaceId} currentName={name} onDone={() => setRenameOpen(false)} />
      </Modal>
      <ConfirmDialog
        open={deleteOpen}
        title="Delete workspace"
        message={`Delete "${name}" with all its projects and tasks? This cannot be undone.`}
        confirmLabel="Delete"
        error={deleteError}
        isPending={deleteWorkspace.isPending}
        onConfirm={confirmDelete}
        onClose={() => setDeleteOpen(false)}
      />
    </div>
  );
}
