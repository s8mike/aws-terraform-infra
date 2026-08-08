/**
 * Application routing.
 * Defines public and protected routes.
 */

import {
  BrowserRouter,
  Routes,
  Route,
} from "react-router-dom";

import LoginPage from "../pages/auth/LoginPage";
import DashboardPage from "../pages/DashboardPage";
import AdminDashboard from "../pages/admin/AdminDashboard";
import TeacherDashboard from "../pages/teacher/TeacherDashboard";
import StudentDashboard from "../pages/student/StudentDashboard";
import ParentDashboard from "../pages/parent/ParentDashboard";

import ProtectedRoute from "./ProtectedRoute";
import AccessDenied from "../pages/AccessDenied";
import AppLayout from "../components/layout/AppLayout";

export default function AppRoutes() {
  return (
    <BrowserRouter>

      <Routes>

        {/* Public authentication route */}
        <Route
          path="/login"
          element={<LoginPage />}
        />

        {/* Access denied page */}
        <Route
          path="/access-denied"
          element={<AccessDenied />}
        />

        {/* General authenticated dashboard */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <AppLayout>
                <DashboardPage />
              </AppLayout>
            </ProtectedRoute>
          }
        />


        {/* Admin-only dashboard */}
        <Route
          path="/admin/dashboard"
          element={
            <ProtectedRoute
              allowedRoles={["admin"]}
            >
              <AdminDashboard />
            </ProtectedRoute>
          }
        />
        
        {/* Teacher-only dashboard */}
        <Route
          path="/teacher/dashboard"
          element={
            <ProtectedRoute
              allowedRoles={["teacher"]}
            >
              <TeacherDashboard />
            </ProtectedRoute>
          }
        />

        {/* Student-only dashboard */}
        <Route
          path="/student/dashboard"
          element={
            <ProtectedRoute
              allowedRoles={["student"]}
            >
              <StudentDashboard />
            </ProtectedRoute>
          }
        />

        {/* Parent-only dashboard */}
        <Route
          path="/parent/dashboard"
          element={
            <ProtectedRoute
              allowedRoles={["parent"]}
            >
              <ParentDashboard />
            </ProtectedRoute>
          }
        />


      </Routes>

    </BrowserRouter>
  );
}