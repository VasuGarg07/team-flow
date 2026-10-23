import type { Role, Task } from "@/api/types";

export function canManageWorkspace(role: Role): boolean {
  return role === "OWNER" || role === "ADMIN";
}

export function canDeleteWorkspace(role: Role): boolean {
  return role === "OWNER";
}

export function canChangeRoles(role: Role): boolean {
  return role === "OWNER";
}

export function canRemoveMember(myRole: Role, targetRole: Role): boolean {
  if (targetRole === "OWNER") return false;
  if (myRole === "OWNER") return true;
  return myRole === "ADMIN" && targetRole === "MEMBER";
}

export function canEditTask(role: Role, userId: number, task: Task): boolean {
  if (canManageWorkspace(role)) return true;
  return task.reporter_id === userId || task.assignee_id === userId;
}

export function canDeleteTask(role: Role, userId: number, task: Task): boolean {
  if (canManageWorkspace(role)) return true;
  return task.reporter_id === userId;
}
