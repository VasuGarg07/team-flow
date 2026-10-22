import type { ReactNode } from "react";
import { Logo } from "@/components/Logo";

export function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="grid min-h-screen md:grid-cols-[1.1fr_1fr]">
      <div className="relative hidden flex-col justify-between overflow-hidden bg-foreground p-10 text-background md:flex">
        <div className="text-background">
          <Logo />
        </div>
        <div>
          <h2 className="max-w-[14ch] text-3xl font-semibold leading-tight tracking-tight">
            Ship the work, not the status meetings.
          </h2>
          <p className="mt-3 max-w-[34ch] text-sm text-background/60">
            Workspaces, projects and tasks for small teams.
          </p>
        </div>
        <div className="pointer-events-none absolute -bottom-20 -right-20 h-72 w-72 rounded-full border border-background/15 shadow-[0_0_0_40px_rgb(250_249_247/0.04),0_0_0_80px_rgb(250_249_247/0.025)]" />
      </div>
      <div className="grid content-center px-6 py-10 md:px-12">
        <div className="mx-auto grid w-full max-w-sm gap-5">
          <div className="md:hidden">
            <Logo />
          </div>
          {children}
        </div>
      </div>
    </div>
  );
}
