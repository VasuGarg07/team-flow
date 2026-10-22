export function Logo() {
  return (
    <div className="flex items-center gap-2 font-semibold tracking-tight">
      <div className="grid h-[22px] w-[22px] place-items-center rounded-sm bg-brand">
        <span className="h-2 w-2 rotate-45 rounded-[2px] bg-brand-foreground" />
      </div>
      TeamFlow
    </div>
  );
}
