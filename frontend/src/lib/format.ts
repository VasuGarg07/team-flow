export function labelFor(value: string): string {
  const spaced = value.toLowerCase().replace("_", " ");
  return spaced.charAt(0).toUpperCase() + spaced.slice(1);
}

export function formatDate(isoDate: string): string {
  return new Date(isoDate).toLocaleDateString(undefined, {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export function formatDateTime(isoDate: string): string {
  return new Date(isoDate).toLocaleString(undefined, {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export function daysOverdue(isoDate: string): number {
  const millisecondsPerDay = 86_400_000;
  const difference = Date.now() - new Date(isoDate).getTime();
  if (difference <= 0) return 0;
  return Math.max(1, Math.floor(difference / millisecondsPerDay));
}

export function toDateTimeInput(isoDate: string | null): string {
  return isoDate === null ? "" : isoDate.slice(0, 16);
}

export function fromDateTimeInput(value: string): string | null {
  return value === "" ? null : `${value}:00`;
}
