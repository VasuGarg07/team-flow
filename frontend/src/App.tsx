import { BrowserRouter, Navigate, Outlet, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "@/auth/AuthContext";
import { HomePage } from "@/pages/HomePage";
import { LoginPage } from "@/pages/LoginPage";
import { RegisterPage } from "@/pages/RegisterPage";

function ProtectedRoutes() {
  const { status } = useAuth();
  if (status === "loading") {
    return null;
  }
  if (status === "guest") {
    return <Navigate to="/login" replace />;
  }
  return <Outlet />;
}

function GuestRoutes() {
  const { status } = useAuth();
  if (status === "loading") {
    return null;
  }
  if (status === "authenticated") {
    return <Navigate to="/" replace />;
  }
  return <Outlet />;
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route element={<ProtectedRoutes />}>
            <Route path="/" element={<HomePage />} />
          </Route>
          <Route element={<GuestRoutes />}>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
