/**
 * Application navigation.
 *
 * Contains navigation links available
 * to the authenticated user.
 *
 * Navigation visibility is based on
 * the user's authenticated role.
 *
 * Phase 13.2 - Step 7.5
 */

import { NavLink } from "react-router-dom";

import { useAuth } from "../../contexts/AuthContext";


// Navigation component
export default function Navigation() {

  const { user } = useAuth();

  // No navigation is rendered until
  // the authenticated user is available.
  if (!user) {
    return null;
  }

  return (
    <nav className="space-y-2">

      {/* Common dashboard link */}
      <NavLink
        to="/dashboard"
        className={({ isActive }) =>
          `block rounded-md px-3 py-2 text-sm font-medium ${
            isActive
              ? "bg-blue-100 text-blue-700"
              : "text-gray-700 hover:bg-gray-100"
          }`
        }
      >
        Dashboard
      </NavLink>


      {/* Administrator navigation */}
      {user.role === "admin" && (
        <NavLink
          to="/admin/dashboard"
          className={({ isActive }) =>
            `block rounded-md px-3 py-2 text-sm font-medium ${
              isActive
                ? "bg-blue-100 text-blue-700"
                : "text-gray-700 hover:bg-gray-100"
            }`
          }
        >
          Admin Dashboard
        </NavLink>
      )}


      {/* Teacher navigation */}
      {user.role === "teacher" && (
        <NavLink
          to="/teacher/dashboard"
          className={({ isActive }) =>
            `block rounded-md px-3 py-2 text-sm font-medium ${
              isActive
                ? "bg-blue-100 text-blue-700"
                : "text-gray-700 hover:bg-gray-100"
            }`
          }
        >
          Teacher Dashboard
        </NavLink>
      )}


      {/* Student navigation */}
      {user.role === "student" && (
        <NavLink
          to="/student/dashboard"
          className={({ isActive }) =>
            `block rounded-md px-3 py-2 text-sm font-medium ${
              isActive
                ? "bg-blue-100 text-blue-700"
                : "text-gray-700 hover:bg-gray-100"
            }`
          }
        >
          Student Dashboard
        </NavLink>
      )}


      {/* Parent navigation */}
      {user.role === "parent" && (
        <NavLink
          to="/parent/dashboard"
          className={({ isActive }) =>
            `block rounded-md px-3 py-2 text-sm font-medium ${
              isActive
                ? "bg-blue-100 text-blue-700"
                : "text-gray-700 hover:bg-gray-100"
            }`
          }
        >
          Parent Dashboard
        </NavLink>
      )}

    </nav>
  );
}