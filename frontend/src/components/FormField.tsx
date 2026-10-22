import type { ComponentProps } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

type FormFieldProps = ComponentProps<typeof Input> & {
  id: string;
  label: string;
  error?: string;
};

export function FormField({ id, label, error, ...inputProps }: FormFieldProps) {
  return (
    <div className="grid gap-1.5">
      <Label htmlFor={id}>{label}</Label>
      <Input id={id} aria-invalid={error !== undefined} {...inputProps} />
      {error !== undefined && <span className="text-xs text-destructive">{error}</span>}
    </div>
  );
}
