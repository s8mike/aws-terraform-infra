/**
 * Main authenticated dashboard.
 *
 * Provides role-aware dashboard content and
 * retrieves live administrator statistics.
 *
 * Phase 19.6 - Dashboard Content & Information Hierarchy
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

  // Tracks administrator dashboard loading state.
  const [loading, setLoading] = useState(false);

  // Stores a user-safe dashboard error message.
  const [error, setError] = useState<string | null>(
    null
  );

  // Retrieve live statistics only for administrators.
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

  const role = user?.role;

  const isAdmin = role === "admin";
  const isTeacher = role === "teacher";
  const isStudent = role === "student";
  const isParent = role === "parent";

  // Define dashboard identity and context by role.
  const dashboardContent = isAdmin
    ? {
        title: "Administrator Dashboard",
        description:
          "Manage the school platform, users, courses, and system activity.",
      }
    : isTeacher
      ? {
          title: "Teacher Dashboard",
          description:
            "Manage your teaching activities, classes, courses, and assignments.",
        }
      : isStudent
        ? {
            title: "Student Dashboard",
            description:
              "View your courses, assignments, learning progress, and results.",
          }
        : isParent
          ? {
              title: "Parent Dashboard",
              description:
                "Monitor your child's courses, attendance, progress, and results.",
            }
          : {
              title: "Dashboard",
              description:
                "Welcome to the Mecandjeo School LMS.",
            };

  return (
    <div className="mx-auto max-w-7xl">

      {/* Dashboard identity and authenticated-user context */}
      <DashboardHeader
        title={dashboardContent.title}
        description={
          user
            ? `Welcome back, ${user.email}. ${dashboardContent.description}`
            : dashboardContent.description
        }
      />

      {error && (
        <div
          role="alert"
          className="mb-4 rounded-lg border border-red-200 bg-red-50 p-4"
        >
          {/* User-safe API error feedback */}
          <p className="text-sm font-medium text-red-800">
            {error}
          </p>

          {/* Retry the failed dashboard request */}
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="mt-3 rounded-md border border-red-300 px-3 py-1.5 text-sm font-medium text-red-700 hover:bg-red-100"
          >
            Retry
          </button>
        </div>
      )}

      {/* Administrator statistics come from the live backend API. */}
      {isAdmin && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

          <DashboardCard
            title="Students"
            value={
              adminStats?.total_students ?? "—"
            }
            description={
              adminStats
                ? "Students currently registered"
                : "Data integration pending"
            }
            loading={loading}
          />

          <DashboardCard
            title="Teachers"
            value={
              adminStats?.total_teachers ?? "—"
            }
            description={
              adminStats
                ? "Teachers currently registered"
                : "Data integration pending"
            }
            loading={loading}
          />

          <DashboardCard
            title="Courses"
            value={
              adminStats?.total_courses ?? "—"
            }
            description={
              adminStats
                ? "Courses currently available"
                : "Data integration pending"
            }
            loading={loading}
          />

          <DashboardCard
            title="Users"
            value={
              adminStats?.total_users ?? "—"
            }
            description={
              adminStats
                ? "Registered LMS users"
                : "Data integration pending"
            }
            loading={loading}
          />

        </div>
      )}

      {/* Role-specific dashboard summaries without inventing backend data. */}
      {!isAdmin && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

          {isTeacher && (
            <>
              <DashboardCard
                title="My Students"
                value="—"
                description="Student data integration pending"
              />

              <DashboardCard
                title="My Courses"
                value="—"
                description="Course data integration pending"
              />

              <DashboardCard
                title="Assignments"
                value="—"
                description="Assignment data integration pending"
              />

              <DashboardCard
                title="Classes"
                value="—"
                description="Class data integration pending"
              />
            </>
          )}

          {isStudent && (
            <>
              <DashboardCard
                title="My Courses"
                value="—"
                description="Course data integration pending"
              />

              <DashboardCard
                title="Assignments"
                value="—"
                description="Assignment data integration pending"
              />

              <DashboardCard
                title="Results"
                value="—"
                description="Results data integration pending"
              />

              <DashboardCard
                title="Progress"
                value="—"
                description="Progress data integration pending"
              />
            </>
          )}

          {isParent && (
            <>
              <DashboardCard
                title="Children"
                value="—"
                description="Child data integration pending"
              />

              <DashboardCard
                title="Courses"
                value="—"
                description="Course data integration pending"
              />

              <DashboardCard
                title="Attendance"
                value="—"
                description="Attendance data integration pending"
              />

              <DashboardCard
                title="Results"
                value="—"
                description="Results data integration pending"
              />
            </>
          )}

        </div>
      )}

      {/* Shared activity and role-appropriate actions. */}
      <div className="mt-6 grid gap-6 lg:grid-cols-2">

        <DashboardSection title="Recent Activity">
          <p className="text-sm text-gray-500">
            No recent activity is available yet.
          </p>
        </DashboardSection>

        <DashboardSection title="Quick Actions">

          {/* Administrator actions are displayed only to administrators. */}
          {isAdmin && (
            <div className="space-y-4">

              <div className="rounded-lg border border-gray-200 p-4 transition hover:-translate-y-0.5 hover:bg-gray-50 hover:shadow-sm">
                <h3 className="font-medium text-gray-900">
                  Manage Users
                </h3>

                <p className="mt-1 text-sm text-gray-600">
                  Manage students, teachers, parents,
                  and other platform users.
                </p>
              </div>

              <div className="rounded-lg border border-gray-200 p-4 transition hover:-translate-y-0.5 hover:bg-gray-50 hover:shadow-sm">
                <h3 className="font-medium text-gray-900">
                  Manage Courses
                </h3>

                <p className="mt-1 text-sm text-gray-600">
                  Create and manage courses across the
                  school platform.
                </p>
              </div>

            </div>
          )}

          {/* Teacher actions are prepared for future API integration. */}
          {isTeacher && (
            <div className="space-y-4">

              <div className="rounded-lg border border-gray-200 p-4 transition hover:-translate-y-0.5 hover:bg-gray-50 hover:shadow-sm">
                <h3 className="font-medium text-gray-900">
                  My Courses
                </h3>

                <p className="mt-1 text-sm text-gray-600">
                  View and manage your teaching courses.
                </p>
              </div>

              <div className="rounded-lg border border-gray-200 p-4 transition hover:-translate-y-0.5 hover:bg-gray-50 hover:shadow-sm">
                <h3 className="font-medium text-gray-900">
                  Assignments
                </h3>

                <p className="mt-1 text-sm text-gray-600">
                  Manage assignments for your students.
                </p>
              </div>

            </div>
          )}

          {/* Student actions are prepared for future API integration. */}
          {isStudent && (
            <div className="space-y-4">

              <div className="rounded-lg border border-gray-200 p-4 transition hover:-translate-y-0.5 hover:bg-gray-50 hover:shadow-sm">
                <h3 className="font-medium text-gray-900">
                  My Courses
                </h3>

                <p className="mt-1 text-sm text-gray-600">
                  View your enrolled courses.
                </p>
              </div>

              <div className="rounded-lg border border-gray-200 p-4 transition hover:-translate-y-0.5 hover:bg-gray-50 hover:shadow-sm">
                <h3 className="font-medium text-gray-900">
                  Assignments
                </h3>

                <p className="mt-1 text-sm text-gray-600">
                  View your current assignments.
                </p>
              </div>

            </div>
          )}

          {/* Parent actions are prepared for future API integration. */}
          {isParent && (
            <div className="space-y-4">

              <div className="rounded-lg border border-gray-200 p-4 transition hover:-translate-y-0.5 hover:bg-gray-50 hover:shadow-sm">
                <h3 className="font-medium text-gray-900">
                  Child Progress
                </h3>

                <p className="mt-1 text-sm text-gray-600">
                  Monitor your child's learning progress.
                </p>
              </div>

              <div className="rounded-lg border border-gray-200 p-4 transition hover:-translate-y-0.5 hover:bg-gray-50 hover:shadow-sm">
                <h3 className="font-medium text-gray-900">
                  Results
                </h3>

                <p className="mt-1 text-sm text-gray-600">
                  View your child's academic results.
                </p>
              </div>

            </div>
          )}

        </DashboardSection>

      </div>
    </div>
  );
}