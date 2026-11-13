import type { ReactNode } from "react";
import { Navigate, Route, Routes } from "react-router";
import { getToken } from "./api";
import LoginPage from "./LoginPage";
import StaffEventsPage from "./StaffEventsPage";
import RegisterPage from "./RegisterPage";
import CheckInPage from "./CheckInPage";
import DashboardPage from "./DashboardPage";

function RequireAuth({ children }: { children: ReactNode }) {
  return getToken() ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
            <Route path="/events/:eventId/register" element={<RegisterPage />} />
      <Route
        path="/staff"
        element={
          <RequireAuth>
            <StaffEventsPage />
          </RequireAuth>
        }
      />
            <Route
        path="/staff/events/:eventId/checkin"
        element={
          <RequireAuth>
            <CheckInPage />
          </RequireAuth>
        }
      />
            <Route
        path="/staff/events/:eventId/dashboard"
        element={
          <RequireAuth>
            <DashboardPage />
          </RequireAuth>
        }
      />
      <Route path="*" element={<Navigate to="/staff" replace />} />
    </Routes>
  );
}