/**
 * Shared application header.
 *
 * Displays application identity and
 * authenticated user information.
 *
 * Provides logout functionality through
 * the global AuthContext.
 *
 * Phase 19.2 - Application Shell & Global Layout
 */

import { useNavigate } from "react-router-dom";

import { useAuth } from "../../contexts/AuthContext";

export default function Header() {
  const {
    user,
    logout,
  } = useAuth();

  const navigate = useNavigate();

  // Handle authenticated user logout
  const handleLogout = () => {
    logout();

    navigate("/login", {
      replace: true,
    });
  };

  return (
    <header className="sticky top-0 z-30 border-b bg-white/95 px-4 py-3 backdrop-blur sm:px-6">

      <div className="flex min-h-10 items-center justify-between gap-4">

        {/* Application identity */}
        <div className="min-w-0">
          <div className="truncate text-lg font-bold tracking-tight text-gray-900">
            MECANDJEO LMS
          </div>

          <div className="hidden text-xs text-gray-500 sm:block">
            School Management Platform
          </div>
        </div>

        {/* Authenticated user information */}
        {user && (
          <div className="flex shrink-0 items-center gap-3">

            <div className="hidden text-right sm:block">

              <div className="text-sm font-medium text-gray-900">
                {user.email}
              </div>

              <div className="text-xs capitalize text-gray-500">
                {user.role}
              </div>

            </div>

            {/* Logout */}
            <button
              type="button"
              onClick={handleLogout}
              className="rounded-md bg-gray-900 px-3 py-2 text-sm font-medium text-white transition hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2"
            >
              Logout
            </button>

          </div>
        )}

      </div>

    </header>
  );
}