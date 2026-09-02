/**
 * Shared application header.
 *
 * Displays application identity and
 * authenticated user information.
 *
 * Phase 19.5 - Responsive/Mobile Navigation
 */

import { Menu, X } from "lucide-react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../../contexts/AuthContext";

interface HeaderProps {
  onMenuToggle: () => void;
  isMobileMenuOpen: boolean;
}

export default function Header({
  onMenuToggle,
  isMobileMenuOpen,
}: HeaderProps) {

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
    <header className="border-b bg-white px-4 py-3 sm:px-6">

      <div className="flex items-center justify-between gap-4">

        {/* Mobile/tablet menu button. */}
        <button
          type="button"
          onClick={onMenuToggle}
          className="rounded-md p-2 text-gray-700 hover:bg-gray-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 lg:hidden"
          aria-label={
            isMobileMenuOpen
              ? "Close navigation menu"
              : "Open navigation menu"
          }
          aria-expanded={isMobileMenuOpen}
          aria-controls="mobile-navigation"
        >
          {isMobileMenuOpen ? (
            <X size={22} aria-hidden="true" />
          ) : (
            <Menu size={22} aria-hidden="true" />
          )}
        </button>

        {/* Application identity. */}
        <div className="mr-auto">
          <div className="text-lg font-bold">
            MECANDJEO LMS
          </div>

          <div className="hidden text-xs text-gray-500 sm:block">
            School Management Platform
          </div>
        </div>

        {/* Authenticated user information. */}
        {user && (
          <div className="flex items-center gap-2 sm:gap-4">

            <div className="hidden text-right sm:block">

              <div className="text-sm font-medium">
                {user.email}
              </div>

              <div className="text-xs capitalize text-gray-500">
                {user.role}
              </div>

            </div>

            {/* Logout remains available on every screen size. */}
            <button
              type="button"
              onClick={handleLogout}
              className="rounded-md bg-black px-3 py-2 text-sm font-medium text-white hover:opacity-90 sm:px-4"
            >
              Logout
            </button>

          </div>
        )}

      </div>

    </header>
  );
}