import type { ReactNode } from "react";
import { Navigate, Route, Routes } from "react-router";
import { getToken } from "./api";
import LoginPage from "./LoginPage";
import StaffEventsPage from "./StaffEventsPage";

function RequireAuth({ children }: { children: ReactNode }) {
  return getToken() ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/staff"
        element={
          <RequireAuth>
            <StaffEventsPage />
          </RequireAuth>
        }
      />
      <Route path="*" element={<Navigate to="/staff" replace />} />
    </Routes>
  );
}