import { AlertCircle, Loader2, type LucideIcon } from "lucide-react";
import type { ReactNode } from "react";
import { ApiError } from "@/lib/api";
import { errorMessage } from "@/lib/forms";

export function Loading() {
  return (
    <div className="flex items-center justify-center gap-2 py-10 text-sm text-muted-foreground">
      <Loader2 size={16} className="animate-spin" />
      Loading
    </div>
  );
}

export function EmptyState({ icon: Icon, title, hint }: { icon: LucideIcon; title: string; hint?: string }) {
  return (
    <div className="rounded-lg border border-dashed py-10 text-center">
      <Icon size={24} className="mx-auto mb-2 text-muted-foreground" />
      <p className="font-medium">{title}</p>
      {hint !== undefined && <p className="mt-1 text-sm text-muted-foreground">{hint}</p>}
    </div>
  );
}

export function QueryError({ error, children }: { error: unknown; children?: ReactNode }) {
  const notFound = error instanceof ApiError && error.status === 404;
  return (
    <div className="rounded-lg border border-dashed py-10 text-center">
      <AlertCircle size={24} className="mx-auto mb-2 text-muted-foreground" />
      <p className="font-medium">{notFound ? "Not found" : "Something went wrong"}</p>
      <p className="mt-1 text-sm text-muted-foreground">
        {notFound ? "It may not exist, or you are not a member." : errorMessage(error)}
      </p>
      {children}
    </div>
  );
}

export function ErrorBox({ message }: { message: string }) {
  return (
    <p
      role="alert"
      className="flex items-start gap-2 rounded-md bg-destructive-subtle px-3 py-2 text-sm text-destructive"
    >
      <AlertCircle size={16} className="mt-0.5 shrink-0" />
      {message}
    </p>
  );
}
