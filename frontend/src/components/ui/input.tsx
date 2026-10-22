import type { InputHTMLAttributes, Ref } from "react";
import { cn } from "@/lib/utils";

type InputProps = InputHTMLAttributes<HTMLInputElement> & { ref?: Ref<HTMLInputElement> };

export function Input({ className, ...props }: InputProps) {
  return (
    <input
      className={cn(
        "h-9 w-full rounded-md border border-input bg-card px-3 text-sm text-foreground placeholder:text-muted-foreground/70 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring aria-invalid:border-destructive disabled:opacity-50",
        className,
      )}
      {...props}
    />
  );
}
