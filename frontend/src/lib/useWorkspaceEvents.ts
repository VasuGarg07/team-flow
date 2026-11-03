import { useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import { getAccessToken, refreshAccessToken } from "@/lib/api";

const policyViolationCode = 1008;
const reconnectDelayMs = 3000;

type TaskEvent = { projectId: number; taskId: number };

function readTaskEvent(text: string): TaskEvent | null {
  try {
    const data: unknown = JSON.parse(text);
    if (typeof data !== "object" || data === null) return null;
    if (!("project_id" in data) || !("task_id" in data)) return null;
    if (typeof data.project_id !== "number" || typeof data.task_id !== "number") return null;
    return { projectId: data.project_id, taskId: data.task_id };
  } catch {
    return null;
  }
}

export function useWorkspaceEvents(workspaceId: number): void {
  const queryClient = useQueryClient();

  useEffect(() => {
    let socket: WebSocket | null = null;
    let reconnectTimer: number | undefined;
    let stopped = false;
    let retriedAfterRefusal = false;

    async function connect(isReconnect: boolean) {
      if (isReconnect) {
        const token = await refreshAccessToken();
        if (token === null || stopped) return;
        queryClient.invalidateQueries({ queryKey: ["tasks"] });
        queryClient.invalidateQueries({ queryKey: ["task"] });
      }
      const protocol = window.location.protocol === "https:" ? "wss" : "ws";
      const newSocket = new WebSocket(`${protocol}://${window.location.host}/ws/workspaces/${workspaceId}`);
      socket = newSocket;

      newSocket.onopen = () => {
        const token = getAccessToken();
        if (token === null) {
          newSocket.close();
          return;
        }
        newSocket.send(JSON.stringify({ token }));
      };

      newSocket.onmessage = (event: MessageEvent<string>) => {
        const taskEvent = readTaskEvent(event.data);
        if (taskEvent === null) return;
        queryClient.invalidateQueries({ queryKey: ["tasks", taskEvent.projectId] });
        queryClient.invalidateQueries({ queryKey: ["task", taskEvent.taskId] });
      };

      newSocket.onclose = (event: CloseEvent) => {
        if (stopped) return;
        if (event.code === policyViolationCode) {
          if (retriedAfterRefusal) return;
          retriedAfterRefusal = true;
        }
        reconnectTimer = window.setTimeout(() => connect(true), reconnectDelayMs);
      };
    }

    connect(false);

    return () => {
      stopped = true;
      window.clearTimeout(reconnectTimer);
      socket?.close();
    };
  }, [workspaceId, queryClient]);
}
