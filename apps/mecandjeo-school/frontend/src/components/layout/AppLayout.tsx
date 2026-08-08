/**
 * Main application layout.
 *
 * Provides the shared structure used by
 * authenticated application pages.
 *
 * Phase 13.2 - Step 7.1
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

        <div className="flex">

        {/* Shared application sidebar */}
        <Sidebar />

        {/* Shared application content area */}
        <main className="min-h-screen flex-1 p-6">
            {children}
        </main>

        </div>

    </div>
    );
}