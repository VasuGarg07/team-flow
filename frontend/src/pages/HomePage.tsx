import { LogOut } from "lucide-react";
import { useAuth } from "@/auth/AuthContext";
import { Logo } from "@/components/Logo";
import { Button } from "@/components/ui/button";

export function HomePage() {
  const { user, logout } = useAuth();

  if (user === null) {
    return null;
  }

  const initials = `${user.first_name.charAt(0)}${user.last_name.charAt(0)}`.toUpperCase();

  return (
    <div className="min-h-screen">
      <header className="flex h-14 items-center justify-between border-b px-6">
        <Logo />
        <div className="flex items-center gap-3">
          <div className="grid h-7 w-7 place-items-center rounded-full bg-brand-subtle text-xs font-semibold text-brand">
            {initials}
          </div>
          <span className="hidden text-sm sm:inline">
            {user.first_name} {user.last_name}
          </span>
          <Button variant="ghost" size="icon" onClick={logout} aria-label="Sign out">
            <LogOut size={16} />
          </Button>
        </div>
      </header>
      <main className="mx-auto max-w-3xl px-6 py-12">
        <h1 className="text-2xl font-semibold tracking-tight">Hi, {user.first_name}</h1>
        <p className="mt-1 text-sm text-muted-foreground">{user.email}</p>
        <div className="mt-8 rounded-lg border bg-card p-6 shadow-sm">
          <h2 className="font-semibold tracking-tight">No workspaces yet</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Workspaces, projects and tasks will show up here as the backend grows.
          </p>
        </div>
      </main>
    </div>
  );
}
