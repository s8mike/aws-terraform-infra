/**
 * Shared application header.
 *
 * Displays application identity and
 * authenticated user information.
 *
 * Provides logout functionality through
 * the global AuthContext.
 *
 * Phase 13.2 - Step 7.6
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
    <header className="border-b bg-white px-6 py-4">

      <div className="flex items-center justify-between">

        {/* Application identity */}
        <div className="text-lg font-bold">
          MECANDJEO LMS
        </div>


        {/* Authenticated user information */}
        {user && (
          <div className="flex items-center gap-4">

            <div className="text-right">

              <div className="text-sm font-medium">
                {user.email}
              </div>

              <div className="text-xs text-gray-500 capitalize">
                {user.role}
              </div>

            </div>


            {/* Logout */}
            <button
              type="button"
              onClick={handleLogout}
              className="rounded-md bg-black px-4 py-2 text-sm font-medium text-white hover:opacity-90"
            >
              Logout
            </button>

          </div>
        )}

      </div>

    </header>
  );
}