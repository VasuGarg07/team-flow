import { apiRequest, setAccessToken } from "@/lib/api";

export type User = {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
};

export type RegisterInput = {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
};

type TokenResponse = { access_token: string; token_type: string };

export async function loginRequest(email: string, password: string): Promise<void> {
  const tokens = await apiRequest<TokenResponse>("/auth/login", {
    method: "POST",
    body: { email, password },
  });
  setAccessToken(tokens.access_token);
}

export function registerRequest(input: RegisterInput): Promise<User> {
  return apiRequest<User>("/auth/register", { method: "POST", body: input });
}

export function fetchCurrentUser(): Promise<User> {
  return apiRequest<User>("/auth/me");
}

export async function logoutRequest(): Promise<void> {
  await apiRequest<void>("/auth/logout", { method: "DELETE" });
  setAccessToken(null);
}
