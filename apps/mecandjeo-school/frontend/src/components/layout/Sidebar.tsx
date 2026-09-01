/**
 * Application sidebar.
 *
 * Provides the navigation area for
 * authenticated application pages.
 *
 * Phase 19.2 - Application Shell & Global Layout
 */

import Navigation from "./Navigation";

// Sidebar component
export default function Sidebar() {
  return (
    <aside className="hidden min-h-[calc(100vh-73px)] w-64 shrink-0 border-r bg-white lg:block">

      {/* Sidebar navigation container */}
      <div className="sticky top-0 p-4">

        {/* Navigation links */}
        <Navigation />

      </div>

    </aside>
  );
}