/**
 * Main application layout.
 *
 * Provides the shared structure used by
 * authenticated application pages.
 *
 * Phase 19.5 - Responsive/Mobile Navigation
 */

import { useState, type ReactNode } from "react";

import Header from "./Header";
import Sidebar from "./Sidebar";

interface AppLayoutProps {
  children: ReactNode;
}

export default function AppLayout({
  children,
}: AppLayoutProps) {

  // Controls the mobile/tablet navigation drawer.
  const [isMobileMenuOpen, setIsMobileMenuOpen] =
    useState(false);

  return (
    <div className="min-h-screen bg-gray-50">

      {/* Header controls the mobile navigation toggle. */}
      <Header
        onMenuToggle={() =>
          setIsMobileMenuOpen((open) => !open)
        }
        isMobileMenuOpen={isMobileMenuOpen}
      />

      <div className="flex min-h-[calc(100vh-73px)]">

        {/* Sidebar adapts between desktop and mobile layouts. */}
        <Sidebar
          isMobileMenuOpen={isMobileMenuOpen}
          onClose={() =>
            setIsMobileMenuOpen(false)
          }
        />

        {/* Shared application content area. */}
        <main className="min-w-0 flex-1 p-4 sm:p-6">
          {children}
        </main>

      </div>

    </div>
  );
}