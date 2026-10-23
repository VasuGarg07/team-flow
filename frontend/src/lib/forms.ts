import type { FieldValues, Path, UseFormSetError } from "react-hook-form";
import { ApiError } from "@/lib/api";

export function errorMessage(error: unknown): string {
  return error instanceof ApiError ? error.message : "Could not reach the server";
}

export function showServerError<T extends FieldValues>(
  error: unknown,
  setError: UseFormSetError<T>,
): string | null {
  if (error instanceof ApiError && error.status === 422 && error.details.length > 0) {
    for (const detail of error.details) {
      const field = detail.field.replace(/^body\./, "");
      setError(field as Path<T>, { message: detail.message });
    }
    return null;
  }
  return errorMessage(error);
}
