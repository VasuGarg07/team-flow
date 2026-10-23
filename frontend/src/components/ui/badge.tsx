import { Crown, Shield, User, type LucideIcon } from "lucide-react";
import type { Role, TaskPriority, TaskStatus } from "@/api/types";
import { labelFor } from "@/lib/format";
import { cn } from "@/lib/utils";

const roleStyles: Record<Role, string> = {
  OWNER: "bg-brand-subtle text-brand",
  ADMIN: "bg-info-subtle text-info",
  MEMBER: "bg-muted text-muted-foreground",
};

export const statusStyles: Record<TaskStatus, string> = {
  OPEN: "bg-status-open-subtle text-status-open",
  IN_PROGRESS: "bg-status-in-progress-subtle text-status-in-progress",
  TESTING: "bg-status-testing-subtle text-status-testing",
  LIVE: "bg-status-live-subtle text-status-live",
  VOID: "bg-status-void-subtle text-status-void",
};

const priorityStyles: Record<TaskPriority, string> = {
  LIVE_ISSUE: "bg-priority-live-issue-subtle text-priority-live-issue",
  BLOCKER: "bg-priority-blocker-subtle text-priority-blocker",
  HIGH: "bg-priority-high-subtle text-priority-high",
  MEDIUM: "bg-priority-medium-subtle text-priority-medium",
  LOW: "bg-priority-low-subtle text-priority-low",
};

export const priorityEdge: Record<TaskPriority, string> = {
  LIVE_ISSUE: "border-l-priority-live-issue",
  BLOCKER: "border-l-priority-blocker",
  HIGH: "border-l-priority-high",
  MEDIUM: "border-l-priority-medium",
  LOW: "border-l-priority-low",
};

const roleIcons: Record<Role, LucideIcon> = {
  OWNER: Crown,
  ADMIN: Shield,
  MEMBER: User,
};

function Badge({ label, style, icon: Icon }: { label: string; style: string; icon?: LucideIcon }) {
  return (
    <span
      className={cn(
        "inline-flex h-5 items-center whitespace-nowrap rounded-full px-2 text-xs font-medium",
        style,
      )}
    >
      {Icon === undefined ? (
        <span className="mr-1.5 h-1.5 w-1.5 rounded-full bg-current" />
      ) : (
        <Icon size={12} className="mr-1" />
      )}
      {labelFor(label)}
    </span>
  );
}

export function RoleBadge({ role }: { role: Role }) {
  return <Badge label={role} style={roleStyles[role]} icon={roleIcons[role]} />;
}

export function StatusBadge({ status }: { status: TaskStatus }) {
  return <Badge label={status} style={statusStyles[status]} />;
}

export function PriorityBadge({ priority }: { priority: TaskPriority }) {
  return <Badge label={priority} style={priorityStyles[priority]} />;
}
