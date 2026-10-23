import type { User } from "@/api/auth";

export const roles = ["OWNER", "ADMIN", "MEMBER"] as const;
export const taskStatuses = ["OPEN", "IN_PROGRESS", "TESTING", "LIVE", "VOID"] as const;
export const taskPriorities = ["LIVE_ISSUE", "BLOCKER", "HIGH", "MEDIUM", "LOW"] as const;
export const sortFields = ["created_at", "due_date", "priority", "status", "story_points", "name"] as const;

export type Role = (typeof roles)[number];
export type TaskStatus = (typeof taskStatuses)[number];
export type TaskPriority = (typeof taskPriorities)[number];
export type SortField = (typeof sortFields)[number];

export type Workspace = {
  id: number;
  name: string;
  created_at: string;
  role: Role;
};

export type Member = {
  user_id: number;
  role: Role;
  user: User;
};

export type Project = {
  id: number;
  workspace_id: number;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
};

export type Task = {
  id: number;
  project_id: number;
  name: string;
  description: string | null;
  assignee_id: number | null;
  assignee: User | null;
  reporter_id: number;
  reporter: User;
  status: TaskStatus;
  priority: TaskPriority;
  story_points: number;
  due_date: string | null;
  created_at: string;
  updated_at: string;
};

export type TaskPage = {
  items: Task[];
  total: number;
  page: number;
  limit: number;
};
