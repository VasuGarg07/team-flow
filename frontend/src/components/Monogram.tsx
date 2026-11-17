export function Monogram({ name }: { name: string }) {
  return (
    <div className="grid h-9 w-9 shrink-0 place-items-center rounded-md bg-muted text-sm font-medium text-muted-foreground">
      {name.charAt(0).toUpperCase()}
    </div>
  );
}
