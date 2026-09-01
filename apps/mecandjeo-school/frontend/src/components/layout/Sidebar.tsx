/**
 * Application sidebar.
 *
 * Provides the primary desktop navigation area.
 *
 * Phase 19.4 - Sidebar & Role-Aware Navigation UI
 */

import Navigation from "./Navigation";

// Sidebar component
export default function Sidebar() {
  return (
    <aside className="hidden min-h-[calc(100vh-73px)] w-64 shrink-0 border-r bg-white lg:block">

      {/* Keep desktop navigation visible while scrolling. */}
      <div className="sticky top-[73px] p-4">

        {/* Sidebar heading */}
        <div className="mb-6 px-3">
          <p className="text-xs font-semibold uppercase tracking-wider text-gray-400">
            Navigation
          </p>
        </div>

        {/* Role-aware navigation links */}
        <Navigation />

      </div>

    </aside>
  );
}