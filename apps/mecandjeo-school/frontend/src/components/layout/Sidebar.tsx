/**
 * Application sidebar.
 *
 * Provides the navigation area for
 * authenticated application pages.
 *
 * Phase 13.2 - Step 7.3
 */

import Navigation from "./Navigation";


// Sidebar component
export default function Sidebar() {
  return (
    <aside className="w-64 border-r bg-white p-4">

      {/* Navigation links */}
      <Navigation />

    </aside>
  );
}