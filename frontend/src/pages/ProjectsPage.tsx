import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { ChevronRight, FolderKanban, Pencil, Plus, Trash2 } from "lucide-react";
import { useForm } from "react-hook-form";
import { Link } from "react-router-dom";
import { z } from "zod";
import { useCreateProject, useDeleteProject, useProjects, useUpdateProject } from "@/api/projects";
import type { Project } from "@/api/types";
import { useWorkspace } from "@/api/workspaces";
import { ConfirmDialog } from "@/components/ConfirmDialog";
import { Field } from "@/components/Field";
import { EmptyState, ErrorBox, Loading, QueryError } from "@/components/PageState";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Modal } from "@/components/ui/modal";
import { Textarea } from "@/components/ui/textarea";
import { errorMessage, showServerError } from "@/lib/forms";
import { useNumericParam } from "@/lib/params";
import { canManageWorkspace } from "@/lib/permissions";

const projectSchema = z.object({
  name: z.string().trim().min(1, "Enter a name").max(100, "Max 100 characters"),
  description: z.string().max(1000, "Max 1000 characters"),
});

type ProjectValues = z.infer<typeof projectSchema>;

type ProjectFormProps = {
  workspaceId: number;
  project: Project | null;
  onDone: () => void;
};

function ProjectForm({ workspaceId, project, onDone }: ProjectFormProps) {
  const createProject = useCreateProject(workspaceId);
  const updateProject = useUpdateProject(workspaceId);
  const [serverError, setServerError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm<ProjectValues>({
    resolver: zodResolver(projectSchema),
    defaultValues: { name: project?.name ?? "", description: project?.description ?? "" },
  });

  async function onSubmit(values: ProjectValues) {
    setServerError(null);
    const description = values.description.trim() === "" ? null : values.description;
    try {
      if (project === null) {
        await createProject.mutateAsync({ name: values.name, description });
      } else {
        await updateProject.mutateAsync({ id: project.id, name: values.name, description });
      }
      onDone();
    } catch (error) {
      setServerError(showServerError(error, setError));
    }
  }

  const isPending = createProject.isPending || updateProject.isPending;

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="grid gap-4" noValidate>
      <Field id="project-name" label="Name" error={errors.name?.message}>
        <Input id="project-name" aria-invalid={errors.name !== undefined} {...register("name")} />
      </Field>
      <Field id="project-description" label="Description" error={errors.description?.message}>
        <Textarea
          id="project-description"
          aria-invalid={errors.description !== undefined}
          {...register("description")}
        />
      </Field>
      {serverError !== null && <ErrorBox message={serverError} />}
      <div className="flex justify-end gap-2">
        <Button type="button" variant="outline" onClick={onDone}>
          Cancel
        </Button>
        <Button type="submit" disabled={isPending}>
          {project === null ? "Create project" : "Save"}
        </Button>
      </div>
    </form>
  );
}

export function ProjectsPage() {
  const workspaceId = useNumericParam("workspaceId");
  const workspace = useWorkspace(workspaceId);
  const projects = useProjects(workspaceId);
  const deleteProject = useDeleteProject(workspaceId);
  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState<Project | null>(null);
  const [deleting, setDeleting] = useState<Project | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const canManage = workspace.data !== undefined && canManageWorkspace(workspace.data.role);

  function openCreate() {
    setEditing(null);
    setFormOpen(true);
  }

  function openEdit(project: Project) {
    setEditing(project);
    setFormOpen(true);
  }

  function openDelete(project: Project) {
    setDeleteError(null);
    setDeleting(project);
  }

  async function confirmDelete() {
    if (deleting === null) return;
    try {
      await deleteProject.mutateAsync(deleting.id);
      setDeleting(null);
    } catch (error) {
      setDeleteError(errorMessage(error));
    }
  }

  return (
    <div className="grid gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold tracking-tight">Projects</h2>
        {canManage && (
          <Button variant="brand" onClick={openCreate}>
            <Plus size={16} />
            New project
          </Button>
        )}
      </div>

      {projects.isPending && <Loading />}
      {projects.isError && <QueryError error={projects.error} />}
      {projects.data?.length === 0 && (
        <EmptyState
          icon={FolderKanban}
          title="No projects yet"
          hint={canManage ? "Create the first project to start adding tasks." : "Ask an owner or admin to create one."}
        />
      )}
      {projects.data !== undefined && projects.data.length > 0 && (
        <ul className="divide-y rounded-lg border bg-card">
          {projects.data.map((project) => (
            <li key={project.id} className="flex items-center justify-between gap-4 p-4">
              <Link
                to={`/app/${workspaceId}/projects/${project.id}`}
                className="flex min-w-0 flex-1 items-center gap-3"
              >
                <div className="grid h-9 w-9 shrink-0 place-items-center rounded-md bg-muted text-muted-foreground">
                  <FolderKanban size={18} />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="font-medium">{project.name}</p>
                  {project.description !== null && (
                    <p className="mt-0.5 truncate text-sm text-muted-foreground">{project.description}</p>
                  )}
                </div>
                <ChevronRight size={16} className="text-muted-foreground" />
              </Link>
              {canManage && (
                <div className="flex gap-1">
                  <Button variant="ghost" size="icon" aria-label="Edit project" onClick={() => openEdit(project)}>
                    <Pencil size={16} />
                  </Button>
                  <Button variant="ghost" size="icon" aria-label="Delete project" onClick={() => openDelete(project)}>
                    <Trash2 size={16} />
                  </Button>
                </div>
              )}
            </li>
          ))}
        </ul>
      )}

      <Modal
        open={formOpen}
        title={editing === null ? "New project" : "Edit project"}
        onClose={() => setFormOpen(false)}
      >
        <ProjectForm workspaceId={workspaceId} project={editing} onDone={() => setFormOpen(false)} />
      </Modal>
      <ConfirmDialog
        open={deleting !== null}
        title="Delete project"
        message={`Delete "${deleting?.name ?? ""}" and all its tasks? This cannot be undone.`}
        confirmLabel="Delete"
        error={deleteError}
        isPending={deleteProject.isPending}
        onConfirm={confirmDelete}
        onClose={() => setDeleting(null)}
      />
    </div>
  );
}
