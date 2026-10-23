import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { useCreateTask, useUpdateTask } from "@/api/tasks";
import { taskPriorities, taskStatuses, type Member, type Task } from "@/api/types";
import { Field } from "@/components/Field";
import { ErrorBox } from "@/components/PageState";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { showServerError } from "@/lib/forms";
import { fromDateTimeInput, labelFor, toDateTimeInput } from "@/lib/format";

const taskSchema = z.object({
  name: z.string().trim().min(1, "Enter a name").max(100, "Max 100 characters"),
  description: z.string().max(1000, "Max 1000 characters"),
  assignee: z.string(),
  priority: z.enum(taskPriorities),
  status: z.enum(taskStatuses),
  story_points: z
    .number({ error: "Enter a number" })
    .int("Whole numbers only")
    .min(1, "At least 1")
    .max(100, "At most 100"),
  due_date: z.string(),
});

type TaskValues = z.infer<typeof taskSchema>;

type TaskFormProps = {
  workspaceId: number;
  projectId: number;
  members: Member[];
  task: Task | null;
  onDone: () => void;
};

export function TaskForm({ workspaceId, projectId, members, task, onDone }: TaskFormProps) {
  const createTask = useCreateTask(workspaceId, projectId);
  const updateTask = useUpdateTask(workspaceId, projectId);
  const [serverError, setServerError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm<TaskValues>({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      name: task?.name ?? "",
      description: task?.description ?? "",
      assignee: task?.assignee_id === null || task === null ? "" : String(task.assignee_id),
      priority: task?.priority ?? "MEDIUM",
      status: task?.status ?? "OPEN",
      story_points: task?.story_points ?? 1,
      due_date: toDateTimeInput(task?.due_date ?? null),
    },
  });

  async function onSubmit(values: TaskValues) {
    setServerError(null);
    const input = {
      name: values.name,
      description: values.description.trim() === "" ? null : values.description,
      assignee_id: values.assignee === "" ? null : Number(values.assignee),
      priority: values.priority,
      story_points: values.story_points,
      due_date: fromDateTimeInput(values.due_date),
    };
    try {
      if (task === null) {
        await createTask.mutateAsync(input);
      } else {
        await updateTask.mutateAsync({ ...input, id: task.id, status: values.status });
      }
      onDone();
    } catch (error) {
      setServerError(showServerError(error, setError));
    }
  }

  const isPending = createTask.isPending || updateTask.isPending;

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="grid gap-4" noValidate>
      <Field id="task-name" label="Name" error={errors.name?.message}>
        <Input id="task-name" aria-invalid={errors.name !== undefined} {...register("name")} />
      </Field>
      <Field id="task-description" label="Description" error={errors.description?.message}>
        <Textarea id="task-description" {...register("description")} />
      </Field>
      <div className="grid grid-cols-2 gap-3">
        <Field id="task-assignee" label="Assignee" error={errors.assignee?.message}>
          <Select id="task-assignee" {...register("assignee")}>
            <option value="">Unassigned</option>
            {members.map((member) => (
              <option key={member.user_id} value={member.user_id}>
                {member.user.first_name} {member.user.last_name}
              </option>
            ))}
          </Select>
        </Field>
        <Field id="task-priority" label="Priority" error={errors.priority?.message}>
          <Select id="task-priority" {...register("priority")}>
            {taskPriorities.map((priority) => (
              <option key={priority} value={priority}>
                {labelFor(priority)}
              </option>
            ))}
          </Select>
        </Field>
        {task !== null && (
          <Field id="task-status" label="Status" error={errors.status?.message}>
            <Select id="task-status" {...register("status")}>
              {taskStatuses.map((status) => (
                <option key={status} value={status}>
                  {labelFor(status)}
                </option>
              ))}
            </Select>
          </Field>
        )}
        <Field id="task-points" label="Story points" error={errors.story_points?.message}>
          <Input
            id="task-points"
            type="number"
            aria-invalid={errors.story_points !== undefined}
            {...register("story_points", { valueAsNumber: true })}
          />
        </Field>
      </div>
      <Field id="task-due" label="Due date" error={errors.due_date?.message}>
        <Input id="task-due" type="datetime-local" {...register("due_date")} />
      </Field>
      {serverError !== null && <ErrorBox message={serverError} />}
      <div className="flex justify-end gap-2">
        <Button type="button" variant="outline" onClick={onDone}>
          Cancel
        </Button>
        <Button type="submit" disabled={isPending}>
          {task === null ? "Create task" : "Save"}
        </Button>
      </div>
    </form>
  );
}
