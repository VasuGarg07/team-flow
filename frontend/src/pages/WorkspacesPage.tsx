import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { Building2, ChevronRight, Plus } from "lucide-react";
import { useForm } from "react-hook-form";
import { Link } from "react-router-dom";
import { z } from "zod";
import { useCreateWorkspace, useWorkspaces } from "@/api/workspaces";
import { EmptyState, ErrorBox, Loading, QueryError } from "@/components/PageState";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { RoleBadge } from "@/components/ui/badge";
import { showServerError } from "@/lib/forms";
import { formatDate } from "@/lib/format";

const schema = z.object({
  name: z.string().trim().min(1, "Enter a name").max(100, "Max 100 characters"),
});

type Values = z.infer<typeof schema>;

export function WorkspacesPage() {
  const workspaces = useWorkspaces();
  const createWorkspace = useCreateWorkspace();
  const [serverError, setServerError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    reset,
    setError,
    formState: { errors },
  } = useForm<Values>({ resolver: zodResolver(schema) });

  async function onSubmit(values: Values) {
    setServerError(null);
    try {
      await createWorkspace.mutateAsync(values);
      reset();
    } catch (error) {
      setServerError(showServerError(error, setError));
    }
  }

  return (
    <div className="grid gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Workspaces</h1>
        <p className="mt-1 text-sm text-muted-foreground">Pick a workspace or create a new one.</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="flex items-start gap-2" noValidate>
        <div className="grid flex-1 gap-1.5 sm:max-w-xs">
          <Input
            placeholder="New workspace name"
            aria-label="New workspace name"
            aria-invalid={errors.name !== undefined}
            {...register("name")}
          />
          {errors.name !== undefined && (
            <span className="text-xs text-destructive">{errors.name.message}</span>
          )}
        </div>
        <Button type="submit" variant="brand" disabled={createWorkspace.isPending}>
          <Plus size={16} />
          Create
        </Button>
      </form>
      {serverError !== null && <ErrorBox message={serverError} />}

      {workspaces.isPending && <Loading />}
      {workspaces.isError && <QueryError error={workspaces.error} />}
      {workspaces.data?.length === 0 && (
        <EmptyState icon={Building2} title="No workspaces yet" hint="Create your first one above." />
      )}
      {workspaces.data !== undefined && workspaces.data.length > 0 && (
        <ul className="grid gap-3 sm:grid-cols-2">
          {workspaces.data.map((workspace) => (
            <li key={workspace.id}>
              <Link
                to={`/app/${workspace.id}`}
                className="block rounded-lg border bg-card p-4 shadow-sm transition-colors hover:bg-accent"
              >
                <div className="flex items-center gap-3">
                  <div className="grid h-9 w-9 shrink-0 place-items-center rounded-md bg-muted text-muted-foreground">
                    <Building2 size={18} />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-medium">{workspace.name}</p>
                    <p className="text-xs text-muted-foreground">Created {formatDate(workspace.created_at)}</p>
                  </div>
                  <RoleBadge role={workspace.role} />
                  <ChevronRight size={16} className="text-muted-foreground" />
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
