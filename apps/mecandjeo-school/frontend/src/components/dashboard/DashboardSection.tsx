/**
 * Reusable dashboard content section.
 *
 * Phase 19.7 - Dashboard Visual Polish
 */

import type { ReactNode } from "react";

interface DashboardSectionProps {
  title: string;
  children: ReactNode;
}

// Provides consistent dashboard section styling.
export default function DashboardSection({
  title,
  children,
}: DashboardSectionProps) {
  return (
    <section className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
      {/* Section heading */}
      <h2 className="text-lg font-semibold tracking-tight text-gray-900">
        {title}
      </h2>

      {/* Section content */}
      <div className="mt-4">
        {children}
      </div>
    </section>
  );
}