import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import { z } from "zod";
import { ApiError } from "@/lib/api";
import { useAuth } from "@/auth/AuthContext";
import { AuthLayout } from "@/components/AuthLayout";
import { FormField } from "@/components/FormField";
import { Button } from "@/components/ui/button";

const loginSchema = z.object({
  email: z.email("Enter a valid email"),
  password: z.string().min(1, "Enter your password"),
});

type LoginValues = z.infer<typeof loginSchema>;

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [serverError, setServerError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginValues>({ resolver: zodResolver(loginSchema) });

  async function onSubmit(values: LoginValues) {
    setServerError(null);
    try {
      await login(values.email, values.password);
      navigate("/");
    } catch (error) {
      setServerError(error instanceof ApiError ? error.message : "Could not reach the server");
    }
  }

  return (
    <AuthLayout>
      <div>
        <h1 className="text-xl font-semibold tracking-tight">Welcome back</h1>
        <p className="mt-1 text-sm text-muted-foreground">Sign in to your workspace.</p>
      </div>
      <form onSubmit={handleSubmit(onSubmit)} className="grid gap-4" noValidate>
        <FormField
          id="email"
          label="Email"
          type="email"
          autoComplete="email"
          placeholder="you@company.com"
          error={errors.email?.message}
          {...register("email")}
        />
        <FormField
          id="password"
          label="Password"
          type="password"
          autoComplete="current-password"
          error={errors.password?.message}
          {...register("password")}
        />
        {serverError !== null && (
          <p role="alert" className="rounded-md bg-destructive-subtle px-3 py-2 text-sm text-destructive">
            {serverError}
          </p>
        )}
        <Button type="submit" size="lg" disabled={isSubmitting}>
          {isSubmitting ? "Signing in..." : "Sign in"}
        </Button>
      </form>
      <p className="text-sm text-muted-foreground">
        New here?{" "}
        <Link to="/register" className="font-medium text-brand hover:underline">
          Create an account
        </Link>
      </p>
    </AuthLayout>
  );
}
