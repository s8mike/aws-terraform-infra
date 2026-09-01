/**
 * Main application layout.
 *
 * Provides the shared structure used by
 * authenticated application pages.
 *
 * Phase 19.2 - Application Shell & Global Layout
 */

import type { ReactNode } from "react";

import Header from "./Header";
import Sidebar from "./Sidebar";

// Layout component contract
interface AppLayoutProps {
  children: ReactNode;
}

// Shared application layout
export default function AppLayout({
  children,
}: AppLayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50">

      {/* Shared application header */}
      <Header />

      <div className="flex min-h-[calc(100vh-73px)]">

        {/* Shared application sidebar */}
        <Sidebar />

        {/* Shared application content area */}
        <main className="min-w-0 flex-1 p-4 sm:p-6 lg:p-8">
          {children}
        </main>

      </div>

    </div>
  );
}