import {
  ArrowDown,
  ArrowLeft,
  ArrowUp,
  ArrowUpDown,
  CalendarDays,
  ChevronLeft,
  ChevronRight,
  ListChecks,
  Pencil,
  Plus,
  Trash2,
  UserRound,
  X,
} from "lucide-react";
import { useEffect, useState } from "react";
import { Link, Outlet, useNavigate } from "react-router-dom";
import { useProject } from "@/api/projects";
import { tasksPerPage, useDeleteTask, useTasks, useUpdateTask, type TaskFilters } from "@/api/tasks";
import {
  taskPriorities,
  taskStatuses,
  type SortField,
  type Task,
  type TaskPriority,
  type TaskStatus,
} from "@/api/types";
import { useMembers, useWorkspace } from "@/api/workspaces";
import { useAuth } from "@/auth/AuthContext";
import { Avatar } from "@/components/Avatar";
import { ConfirmDialog } from "@/components/ConfirmDialog";
import { EmptyState, ErrorBox, Loading, QueryError } from "@/components/PageState";
import { StatusSelect } from "@/components/StatusSelect";
import { TaskForm } from "@/components/TaskForm";
import { PriorityBadge, priorityEdge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Modal } from "@/components/ui/modal";
import { Select } from "@/components/ui/select";
import { errorMessage } from "@/lib/forms";
import { daysOverdue, formatDate, labelFor } from "@/lib/format";
import { useNumericParam } from "@/lib/params";
import { canDeleteTask, canEditTask } from "@/lib/permissions";
import { cn } from "@/lib/utils";

const defaultFilters: TaskFilters = {
  status: "",
  priority: "",
  assigneeId: "",
  sortBy: "created_at",
  order: "desc",
  page: 1,
};

type SortHeaderProps = {
  label: string;
  field: SortField;
  filters: TaskFilters;
  onSort: (field: SortField) => void;
};

function SortHeader({ label, field, filters, onSort }: SortHeaderProps) {
  const active = filters.sortBy === field;
  const Icon = !active ? ArrowUpDown : filters.order === "asc" ? ArrowUp : ArrowDown;
  return (
    <th className="px-4 py-2 font-medium">
      <button
        type="button"
        onClick={() => onSort(field)}
        className={cn(
          "flex items-center gap-1 hover:text-foreground",
          active && "text-foreground",
        )}
      >
        {label}
        <Icon size={12} className={active ? "" : "opacity-50"} />
      </button>
    </th>
  );
}

export function TasksPage() {
  const workspaceId = useNumericParam("workspaceId");
  const projectId = useNumericParam("projectId");
  const navigate = useNavigate();
  const { user } = useAuth();
  const workspace = useWorkspace(workspaceId);
  const project = useProject(workspaceId, projectId);
  const members = useMembers(workspaceId);
  const [filters, setFilters] = useState<TaskFilters>(defaultFilters);
  const tasks = useTasks(workspaceId, projectId, filters);
  const updateTask = useUpdateTask(workspaceId, projectId);
  const deleteTask = useDeleteTask(workspaceId, projectId);
  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState<Task | null>(null);
  const [deleting, setDeleting] = useState<Task | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [rowError, setRowError] = useState<string | null>(null);

  function changeFilters(changes: Partial<TaskFilters>) {
    setFilters({ ...filters, page: 1, ...changes });
  }

  function sortBy(field: SortField) {
    if (filters.sortBy === field) {
      changeFilters({ order: filters.order === "asc" ? "desc" : "asc" });
      return;
    }
    changeFilters({ sortBy: field, order: field === "name" ? "asc" : "desc" });
  }

  function openCreate() {
    setEditing(null);
    setFormOpen(true);
  }

  function openEdit(task: Task) {
    setEditing(task);
    setFormOpen(true);
  }

  async function changeStatus(task: Task, status: TaskStatus) {
    setRowError(null);
    try {
      await updateTask.mutateAsync({ id: task.id, status });
    } catch (error) {
      setRowError(errorMessage(error));
    }
  }

  async function confirmDelete() {
    if (deleting === null) return;
    try {
      await deleteTask.mutateAsync(deleting.id);
      setDeleting(null);
    } catch (error) {
      setDeleteError(errorMessage(error));
    }
  }

  const membersLoaded = members.data !== undefined;

  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      const target = event.target;
      const typing =
        target instanceof HTMLElement && ["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName);
      const modifier = event.metaKey || event.ctrlKey || event.altKey;
      const dialogOpen = document.querySelector("dialog[open]") !== null;
      if (event.key === "c" && !typing && !modifier && !dialogOpen && membersLoaded) {
        event.preventDefault();
        setEditing(null);
        setFormOpen(true);
      }
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [membersLoaded]);

  if (project.isError) {
    return <QueryError error={project.error} />;
  }

  const myRole = workspace.data?.role;
  const totalPages = tasks.data === undefined ? 1 : Math.max(1, Math.ceil(tasks.data.total / tasksPerPage));
  const hasFilters = filters.status !== "" || filters.priority !== "" || filters.assigneeId !== "";
  const tasksUrl = `/app/${workspaceId}/projects/${projectId}`;

  return (
    <div className="grid gap-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <Link
            to={`/app/${workspaceId}`}
            className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
          >
            <ArrowLeft size={14} />
            Back to projects
          </Link>
          <h2 className="text-lg font-semibold tracking-tight">{project.data?.name ?? "Project"}</h2>
        </div>
        <Button variant="brand" onClick={openCreate} disabled={!membersLoaded}>
          <Plus size={16} />
          New task
          <kbd className="rounded bg-brand-foreground/20 px-1 text-[10px]">C</kbd>
        </Button>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3">
        <div role="tablist" aria-label="Filter by status" className="flex flex-wrap gap-1">
          {["", ...taskStatuses].map((status) => (
            <button
              key={status}
              type="button"
              role="tab"
              aria-selected={filters.status === status}
              onClick={() => changeFilters({ status: status as TaskStatus | "" })}
              className={cn(
                "rounded-md px-2.5 py-1 text-sm font-medium",
                filters.status === status
                  ? "bg-foreground text-background"
                  : "text-muted-foreground hover:bg-accent hover:text-foreground",
              )}
            >
              {status === "" ? "All" : labelFor(status)}
            </button>
          ))}
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Select
            aria-label="Filter by priority"
            className="w-36"
            value={filters.priority}
            onChange={(event) => changeFilters({ priority: event.target.value as TaskPriority | "" })}
          >
            <option value="">All priorities</option>
            {taskPriorities.map((priority) => (
              <option key={priority} value={priority}>
                {labelFor(priority)}
              </option>
            ))}
          </Select>
          <Select
            aria-label="Filter by assignee"
            className="w-40"
            value={filters.assigneeId}
            onChange={(event) => changeFilters({ assigneeId: event.target.value })}
          >
            <option value="">Anyone</option>
            {members.data?.map((member) => (
              <option key={member.user_id} value={member.user_id}>
                {member.user.first_name} {member.user.last_name}
              </option>
            ))}
          </Select>
          {hasFilters && (
            <Button variant="ghost" onClick={() => setFilters(defaultFilters)}>
              <X size={14} />
              Clear
            </Button>
          )}
        </div>
      </div>

      {rowError !== null && <ErrorBox message={rowError} />}
      {tasks.isPending && <Loading />}
      {tasks.isError && <QueryError error={tasks.error} />}
      {tasks.data?.items.length === 0 && (
        <EmptyState
          icon={ListChecks}
          title={hasFilters ? "No tasks match these filters" : "No tasks yet"}
          hint={hasFilters ? "Try clearing a filter." : "Create the first task for this project."}
        />
      )}
      {tasks.data !== undefined && tasks.data.items.length > 0 && myRole !== undefined && user !== null && (
        <div className="overflow-x-auto rounded-lg border bg-card">
          <table className="w-full text-sm">
            <thead className="border-b bg-muted text-left text-xs text-muted-foreground">
              <tr>
                <SortHeader label="Task" field="name" filters={filters} onSort={sortBy} />
                <SortHeader label="Priority" field="priority" filters={filters} onSort={sortBy} />
                <SortHeader label="Status" field="status" filters={filters} onSort={sortBy} />
                <th className="px-4 py-2 font-medium">Assignee</th>
                <SortHeader label="Due" field="due_date" filters={filters} onSort={sortBy} />
                <SortHeader label="Pts" field="story_points" filters={filters} onSort={sortBy} />
                <SortHeader label="Created" field="created_at" filters={filters} onSort={sortBy} />
                <th className="px-4 py-2" />
              </tr>
            </thead>
            <tbody className="divide-y">
              {tasks.data.items.map((task) => {
                const overdueDays =
                  task.due_date !== null && task.status !== "LIVE" && task.status !== "VOID"
                    ? daysOverdue(task.due_date)
                    : 0;
                const editable = canEditTask(myRole, user.id, task);
                return (
                  <tr
                    key={task.id}
                    onClick={() => navigate(`${tasksUrl}/tasks/${task.id}`)}
                    className="cursor-pointer hover:bg-muted/60"
                  >
                    <td className={cn("max-w-xs border-l-[3px] px-4 py-3", priorityEdge[task.priority])}>
                      <Link
                        to={`${tasksUrl}/tasks/${task.id}`}
                        onClick={(event) => event.stopPropagation()}
                        className="block truncate font-medium hover:underline"
                      >
                        {task.name}
                      </Link>
                    </td>
                    <td className="px-4 py-3">
                      <PriorityBadge priority={task.priority} />
                    </td>
                    <td className="px-4 py-3" onClick={(event) => event.stopPropagation()}>
                      <StatusSelect
                        status={task.status}
                        canEdit={editable}
                        onChange={(status) => changeStatus(task, status)}
                      />
                    </td>
                    <td className="whitespace-nowrap px-4 py-3">
                      {task.assignee === null ? (
                        <span className="flex items-center gap-1.5 text-muted-foreground">
                          <UserRound size={14} />
                          Unassigned
                        </span>
                      ) : (
                        <span className="flex items-center gap-2">
                          <Avatar user={task.assignee} />
                          {task.assignee.first_name}
                        </span>
                      )}
                    </td>
                    <td
                      className={cn(
                        "whitespace-nowrap px-4 py-3",
                        overdueDays > 0 ? "text-destructive" : "text-muted-foreground",
                      )}
                    >
                      <span className="flex items-center gap-1.5">
                        <CalendarDays size={14} />
                        {task.due_date === null ? "None" : formatDate(task.due_date)}
                        {overdueDays > 0 && <span className="text-xs">· {overdueDays}d overdue</span>}
                      </span>
                    </td>
                    <td className="px-4 py-3">{task.story_points}</td>
                    <td className="whitespace-nowrap px-4 py-3 text-muted-foreground">
                      {formatDate(task.created_at)}
                    </td>
                    <td
                      className="whitespace-nowrap px-4 py-3 text-right"
                      onClick={(event) => event.stopPropagation()}
                    >
                      {editable && (
                        <Button variant="ghost" size="icon" aria-label="Edit task" onClick={() => openEdit(task)}>
                          <Pencil size={16} />
                        </Button>
                      )}
                      {canDeleteTask(myRole, user.id, task) && (
                        <Button
                          variant="ghost"
                          size="icon"
                          aria-label="Delete task"
                          onClick={() => {
                            setDeleteError(null);
                            setDeleting(task);
                          }}
                        >
                          <Trash2 size={16} />
                        </Button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {tasks.data !== undefined && tasks.data.total > 0 && (
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <span>
            {tasks.data.total} tasks · Page {filters.page} of {totalPages}
          </span>
          <div className="flex gap-2">
            <Button
              variant="outline"
              disabled={filters.page <= 1}
              onClick={() => setFilters({ ...filters, page: filters.page - 1 })}
            >
              <ChevronLeft size={16} />
              Previous
            </Button>
            <Button
              variant="outline"
              disabled={filters.page >= totalPages}
              onClick={() => setFilters({ ...filters, page: filters.page + 1 })}
            >
              Next
              <ChevronRight size={16} />
            </Button>
          </div>
        </div>
      )}

      <Modal open={formOpen} title={editing === null ? "New task" : "Edit task"} onClose={() => setFormOpen(false)}>
        {members.data !== undefined && (
          <TaskForm
            workspaceId={workspaceId}
            projectId={projectId}
            members={members.data}
            task={editing}
            onDone={() => setFormOpen(false)}
          />
        )}
      </Modal>
      <ConfirmDialog
        open={deleting !== null}
        title="Delete task"
        message={`Delete "${deleting?.name ?? ""}"? This cannot be undone.`}
        confirmLabel="Delete"
        error={deleteError}
        isPending={deleteTask.isPending}
        onConfirm={confirmDelete}
        onClose={() => setDeleting(null)}
      />
      <Outlet />
    </div>
  );
}
