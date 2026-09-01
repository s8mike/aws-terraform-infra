/**
 * Application sidebar.
 *
 * Provides desktop navigation and the
 * responsive mobile/tablet navigation drawer.
 *
 * Phase 19.5 - Responsive/Mobile Navigation
 */

import Navigation from "./Navigation";

interface SidebarProps {
  isMobileMenuOpen: boolean;
  onClose: () => void;
}

export default function Sidebar({
  isMobileMenuOpen,
  onClose,
}: SidebarProps) {

  return (
    <>
      {/* Desktop sidebar. */}
      <aside className="hidden min-h-[calc(100vh-73px)] w-64 shrink-0 border-r bg-white lg:block">

        <div className="sticky top-[73px] p-4">

          <div className="mb-6 px-3">
            <p className="text-xs font-semibold uppercase tracking-wider text-gray-400">
              Navigation
            </p>
          </div>

          <Navigation />

        </div>

      </aside>


      {/* Mobile/tablet navigation overlay. */}
      {isMobileMenuOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/30 lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}


      {/* Mobile/tablet navigation drawer. */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-72 max-w-[85vw] border-r bg-white shadow-lg transition-transform duration-200 lg:hidden ${
          isMobileMenuOpen
            ? "translate-x-0"
            : "-translate-x-full"
        }`}
        aria-label="Mobile navigation"
      >

        <div className="border-b px-4 py-4">

          <div className="text-sm font-semibold">
            Navigation
          </div>

        </div>

        <div className="p-4">

          {/* Reuse the same role-aware navigation. */}
          <Navigation
            onNavigate={onClose}
          />

        </div>

      </aside>
    </>
  );
}