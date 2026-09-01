/**
 * Application navigation.
 *
 * Provides role-aware navigation for
 * authenticated application pages.
 *
 * Phase 19.5 - Responsive/Mobile Navigation
 */

import { NavLink } from "react-router-dom";

import { useAuth } from "../../contexts/AuthContext";

interface NavigationProps {
  onNavigate?: () => void;
}

export default function Navigation({
  onNavigate,
}: NavigationProps) {

  const { user } = useAuth();

  // Do not render navigation without authenticated user state.
  if (!user) {
    return null;
  }

  // Shared navigation styling keeps active and hover states consistent.
  const linkClassName = ({ isActive }: { isActive: boolean }) =>
    `flex items-center rounded-lg px-3 py-2.5 text-sm font-medium transition ${
      isActive
        ? "bg-blue-50 text-blue-700"
        : "text-gray-700 hover:bg-gray-100 hover:text-gray-900"
    }`;

  return (
    <nav
      className="space-y-1"
      aria-label="Main navigation"
    >

      {/* Primary navigation section. */}
      <div className="mb-3 px-3 text-xs font-semibold uppercase tracking-wider text-gray-400">
        Main
      </div>

      {/* Common dashboard destination. */}
      <NavLink
        to="/dashboard"
        className={linkClassName}
        onClick={onNavigate}
      >
        Dashboard
      </NavLink>

      {/* Administrator destination. */}
      {user.role === "admin" && (
        <NavLink
          to="/admin/dashboard"
          className={linkClassName}
          onClick={onNavigate}
        >
          Admin Dashboard
        </NavLink>
      )}

      {/* Teacher destination. */}
      {user.role === "teacher" && (
        <NavLink
          to="/teacher/dashboard"
          className={linkClassName}
          onClick={onNavigate}
        >
          Teacher Dashboard
        </NavLink>
      )}

      {/* Student destination. */}
      {user.role === "student" && (
        <NavLink
          to="/student/dashboard"
          className={linkClassName}
          onClick={onNavigate}
        >
          Student Dashboard
        </NavLink>
      )}

      {/* Parent destination. */}
      {user.role === "parent" && (
        <NavLink
          to="/parent/dashboard"
          className={linkClassName}
          onClick={onNavigate}
        >
          Parent Dashboard
        </NavLink>
      )}

    </nav>
  );
}