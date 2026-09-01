/**
 * Shared application header.
 *
 * Displays application identity and
 * authenticated user information.
 *
 * Phase 19.3 - Header & User Account Experience
 */

import { useNavigate } from "react-router-dom";

import { useAuth } from "../../contexts/AuthContext";

export default function Header() {
  const {
    user,
    logout,
  } = useAuth();

  const navigate = useNavigate();

  // Clear the session and return to login.
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

          {/* Show supporting identity on tablet and desktop. */}
          <div className="hidden text-xs text-gray-500 sm:block">
            School Management Platform
          </div>
        </div>

        {user && (
          <div className="flex shrink-0 items-center gap-3">

            {/* Hide detailed identity on smaller screens. */}
            <div className="hidden text-right sm:block">
              <div className="max-w-56 truncate text-sm font-medium text-gray-900">
                {user.email}
              </div>

              {/* Display the authenticated user's role. */}
              <div className="text-xs capitalize text-gray-500">
                {user.role}
              </div>
            </div>

            {/* Provide a compact identity indicator on mobile. */}
            <div
              className="flex h-9 w-9 items-center justify-center rounded-full bg-gray-900 text-sm font-semibold text-white sm:hidden"
              aria-label={`Signed in as ${user.role}`}
              title={user.email}
            >
              {user.email.charAt(0).toUpperCase()}
            </div>

            {/* End the authenticated session. */}
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