/**
 * Main authenticated dashboard.
 *
 * Provides a role-aware dashboard foundation
 * and retrieves live administrator statistics
 * when the authenticated user has the admin role.
 *
 * Phase 17.15.4 - Live Admin Dashboard Integration
 */

import { useEffect, useState } from "react";

import DashboardCard from "../components/dashboard/DashboardCard";
import DashboardHeader from "../components/dashboard/DashboardHeader";
import DashboardSection from "../components/dashboard/DashboardSection";
import { useAuth } from "../contexts/AuthContext";
import {
  getAdminDashboard,
  type AdminDashboardResponse,
} from "../services/adminService";

// Main dashboard page for authenticated users.
export default function DashboardPage() {
  const { user } = useAuth();

  // Stores live administrator dashboard statistics.
  const [adminStats, setAdminStats] =
    useState<AdminDashboardResponse | null>(null);

  // Tracks dashboard API loading state.
  const [loading, setLoading] = useState(false);

  // Stores a user-safe dashboard error message.
  const [error, setError] = useState<string | null>(
    null
  );

  // Retrieve live dashboard statistics for administrators.
  useEffect(() => {
    if (user?.role !== "admin") {
      return;
    }

    const loadAdminDashboard = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await getAdminDashboard();

        setAdminStats(data);
      } catch (requestError) {
        console.error(
          "Failed to load administrator dashboard:",
          requestError
        );

        setError(
          "Unable to load dashboard statistics."
        );
      } finally {
        setLoading(false);
      }
    };

    loadAdminDashboard();
  }, [user?.role]);

  // Define role-specific dashboard content.
  const isAdmin = user?.role === "admin";

  const title = isAdmin
    ? "Administrator Dashboard"
    : "Dashboard";

  const description = isAdmin
    ? "Manage the school platform, users, courses, and system activity."
    : "Welcome to the Mecandjeo School LMS.";

  return (
    <div className="mx-auto max-w-7xl">
      {/* Dashboard heading and authenticated-user context */}
      <DashboardHeader
        title={title}
        description={
          user
            ? `Welcome back, ${user.email}. ${description}`
            : description
        }
      />

      {/* Display dashboard loading state while API data is retrieved */}
      {loading && (
        <p className="mb-4 text-sm text-gray-500">
          Loading dashboard statistics...
        </p>
      )}

      {/* Display a safe error message when the API request fails */}
      {error && (
        <div className="mb-4 rounded-md border border-red-200 bg-red-50 p-4">
          <p className="text-sm text-red-700">
            {error}
          </p>
        </div>
      )}

      {/* Display live administrator dashboard statistics */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <DashboardCard
          title="Students"
          value={
            adminStats?.total_students ??
            "—"
          }
          description={
            adminStats
              ? "Students currently registered"
              : "Data integration pending"
          }
        />

        <DashboardCard
          title="Teachers"
          value={
            adminStats?.total_teachers ??
            "—"
          }
          description={
            adminStats
              ? "Teachers currently registered"
              : "Data integration pending"
          }
        />

        <DashboardCard
          title="Courses"
          value={
            adminStats?.total_courses ??
            "—"
          }
          description={
            adminStats
              ? "Courses currently available"
              : "Data integration pending"
          }
        />

        <DashboardCard
          title="Users"
          value={
            adminStats?.total_users ??
            "—"
          }
          description={
            adminStats
              ? "Registered LMS users"
              : "Data integration pending"
          }
        />
      </div>

      {/* Dashboard information and quick-action area */}
      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <DashboardSection title="Recent Activity">
          {/* Activity integration will be implemented later */}
          <p className="text-sm text-gray-500">
            No recent activity is available yet.
          </p>
        </DashboardSection>

        <DashboardSection title="Quick Actions">
          {/* Administrator actions prepared for future
              navigation and API integration. */}
          <div className="space-y-4">
            <div className="rounded-md border p-4">
              {/* Administrator user-management action */}
              <h3 className="font-medium text-gray-900">
                Manage Users
              </h3>

              <p className="mt-1 text-sm text-gray-600">
                Manage students, teachers, parents,
                and other platform users.
              </p>
            </div>

            <div className="rounded-md border p-4">
              {/* Administrator course-management action */}
              <h3 className="font-medium text-gray-900">
                Manage Courses
              </h3>

              <p className="mt-1 text-sm text-gray-600">
                Create and manage courses across the
                school platform.
              </p>
            </div>
          </div>
        </DashboardSection>
      </div>
    </div>
  );
}