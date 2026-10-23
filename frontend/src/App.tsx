import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Navigate, Outlet, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "@/auth/AuthContext";
import { AppLayout } from "@/components/AppLayout";
import { LoginPage } from "@/pages/LoginPage";
import { MembersPage } from "@/pages/MembersPage";
import { ProjectsPage } from "@/pages/ProjectsPage";
import { RegisterPage } from "@/pages/RegisterPage";
import { TaskPanel } from "@/pages/TaskPanel";
import { TasksPage } from "@/pages/TasksPage";
import { WorkspaceLayout } from "@/pages/WorkspaceLayout";
import { WorkspacesPage } from "@/pages/WorkspacesPage";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false, refetchOnWindowFocus: false, staleTime: 30_000 } },
});

function ProtectedRoutes() {
  const { status } = useAuth();
  if (status === "loading") {
    return null;
  }
  if (status === "guest") {
    return <Navigate to="/login" replace />;
  }
  return <Outlet />;
}

function GuestRoutes() {
  const { status } = useAuth();
  if (status === "loading") {
    return null;
  }
  if (status === "authenticated") {
    return <Navigate to="/app" replace />;
  }
  return <Outlet />;
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route element={<ProtectedRoutes />}>
              <Route element={<AppLayout />}>
                <Route path="/app" element={<WorkspacesPage />} />
                <Route path="/app/:workspaceId" element={<WorkspaceLayout />}>
                  <Route index element={<ProjectsPage />} />
                  <Route path="members" element={<MembersPage />} />
                  <Route path="projects/:projectId" element={<TasksPage />}>
                    <Route path="tasks/:taskId" element={<TaskPanel />} />
                  </Route>
                </Route>
              </Route>
            </Route>
            <Route element={<GuestRoutes />}>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
            </Route>
            <Route path="*" element={<Navigate to="/app" replace />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
