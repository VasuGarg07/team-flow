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

const registerSchema = z.object({
  first_name: z.string().min(1, "Enter your first name").max(50, "Max 50 characters"),
  last_name: z.string().min(1, "Enter your last name").max(50, "Max 50 characters"),
  email: z.email("Enter a valid email"),
  password: z.string().min(8, "At least 8 characters").max(128, "Max 128 characters"),
});

type RegisterValues = z.infer<typeof registerSchema>;

export function RegisterPage() {
  const { register: registerUser } = useAuth();
  const navigate = useNavigate();
  const [serverError, setServerError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterValues>({ resolver: zodResolver(registerSchema) });

  async function onSubmit(values: RegisterValues) {
    setServerError(null);
    try {
      await registerUser(values);
      navigate("/");
    } catch (error) {
      setServerError(error instanceof ApiError ? error.message : "Could not reach the server");
    }
  }

  return (
    <AuthLayout>
      <div>
        <h1 className="text-xl font-semibold tracking-tight">Create your account</h1>
        <p className="mt-1 text-sm text-muted-foreground">It takes less than a minute.</p>
      </div>
      <form onSubmit={handleSubmit(onSubmit)} className="grid gap-4" noValidate>
        <div className="grid grid-cols-2 gap-3">
          <FormField
            id="first_name"
            label="First name"
            autoComplete="given-name"
            error={errors.first_name?.message}
            {...register("first_name")}
          />
          <FormField
            id="last_name"
            label="Last name"
            autoComplete="family-name"
            error={errors.last_name?.message}
            {...register("last_name")}
          />
        </div>
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
          autoComplete="new-password"
          error={errors.password?.message}
          {...register("password")}
        />
        {serverError !== null && (
          <p role="alert" className="rounded-md bg-destructive-subtle px-3 py-2 text-sm text-destructive">
            {serverError}
          </p>
        )}
        <Button type="submit" size="lg" disabled={isSubmitting}>
          {isSubmitting ? "Creating account..." : "Create account"}
        </Button>
      </form>
      <p className="text-sm text-muted-foreground">
        Already have an account?{" "}
        <Link to="/login" className="font-medium text-brand hover:underline">
          Sign in
        </Link>
      </p>
    </AuthLayout>
  );
}
