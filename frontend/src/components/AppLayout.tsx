import { Layers, LogOut } from "lucide-react";
import { Link, Outlet, useNavigate, useParams } from "react-router-dom";
import { useWorkspaces } from "@/api/workspaces";
import { useAuth } from "@/auth/AuthContext";
import { Avatar } from "@/components/Avatar";
import { Logo } from "@/components/Logo";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";

export function AppLayout() {
  const { user, logout } = useAuth();
  const { workspaceId } = useParams();
  const navigate = useNavigate();
  const workspaces = useWorkspaces();

  if (user === null) {
    return null;
  }

  return (
    <div className="min-h-screen">
      <header className="flex h-14 items-center justify-between gap-4 border-b px-6">
        <div className="flex items-center gap-4">
          <Link to="/app">
            <Logo />
          </Link>
          <div className="relative">
            <Layers
              size={14}
              className="pointer-events-none absolute left-2.5 top-1/2 -translate-y-1/2 text-muted-foreground"
            />
            <Select
              aria-label="Switch workspace"
              className="w-52 pl-8"
              value={workspaceId ?? ""}
              onChange={(event) => navigate(`/app/${event.target.value}`)}
            >
              <option value="" disabled>
                Switch workspace
              </option>
              {workspaces.data?.map((workspace) => (
                <option key={workspace.id} value={workspace.id}>
                  {workspace.name}
                </option>
              ))}
            </Select>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Avatar user={user} className="h-7 w-7 text-xs" />
          <span className="hidden text-sm sm:inline">
            {user.first_name} {user.last_name}
          </span>
          <Button variant="ghost" size="icon" onClick={logout} aria-label="Sign out">
            <LogOut size={16} />
          </Button>
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-6 py-8">
        <Outlet />
      </main>
    </div>
  );
}
