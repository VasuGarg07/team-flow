import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import {
  fetchCurrentUser,
  loginRequest,
  logoutRequest,
  registerRequest,
  type RegisterInput,
  type User,
} from "@/api/auth";
import { refreshAccessToken } from "@/lib/api";

type AuthStatus = "loading" | "authenticated" | "guest";

type AuthContextValue = {
  status: AuthStatus;
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (input: RegisterInput) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<AuthStatus>("loading");
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    async function restoreSession() {
      const token = await refreshAccessToken();
      if (token === null) {
        setStatus("guest");
        return;
      }
      const currentUser = await fetchCurrentUser();
      setUser(currentUser);
      setStatus("authenticated");
    }
    restoreSession().catch(() => setStatus("guest"));
  }, []);

  async function login(email: string, password: string) {
    await loginRequest(email, password);
    const currentUser = await fetchCurrentUser();
    setUser(currentUser);
    setStatus("authenticated");
  }

  async function register(input: RegisterInput) {
    await registerRequest(input);
    await login(input.email, input.password);
  }

  async function logout() {
    await logoutRequest();
    setUser(null);
    setStatus("guest");
  }

  return (
    <AuthContext.Provider value={{ status, user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (context === null) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
