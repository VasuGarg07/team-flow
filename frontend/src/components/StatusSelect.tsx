import { ChevronDown } from "lucide-react";
import { taskStatuses, type TaskStatus } from "@/api/types";
import { StatusBadge, statusStyles } from "@/components/ui/badge";
import { labelFor } from "@/lib/format";
import { cn } from "@/lib/utils";

type StatusSelectProps = {
  status: TaskStatus;
  canEdit: boolean;
  onChange: (status: TaskStatus) => void;
};

export function StatusSelect({ status, canEdit, onChange }: StatusSelectProps) {
  if (!canEdit) {
    return <StatusBadge status={status} />;
  }
  return (
    <div className="relative inline-flex">
      <select
        aria-label="Change status"
        value={status}
        onChange={(event) => onChange(event.target.value as TaskStatus)}
        className={cn(
          "h-5 cursor-pointer appearance-none rounded-full border-0 pl-2 pr-5 text-xs font-medium focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring",
          statusStyles[status],
        )}
      >
        {taskStatuses.map((option) => (
          <option key={option} value={option} className="bg-card text-foreground">
            {labelFor(option)}
          </option>
        ))}
      </select>
      <ChevronDown size={12} className="pointer-events-none absolute right-1.5 top-1/2 -translate-y-1/2" />
    </div>
  );
}
