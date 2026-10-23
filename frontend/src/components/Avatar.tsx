import type { User } from "@/api/auth";
import { cn } from "@/lib/utils";

export function Avatar({ user, className }: { user: User; className?: string }) {
  const initials = `${user.first_name.charAt(0)}${user.last_name.charAt(0)}`.toUpperCase();
  return (
    <span
      title={`${user.first_name} ${user.last_name}`}
      className={cn(
        "grid h-6 w-6 shrink-0 place-items-center rounded-full bg-brand-subtle text-[10px] font-semibold text-brand",
        className,
      )}
    >
      {initials}
    </span>
  );
}
