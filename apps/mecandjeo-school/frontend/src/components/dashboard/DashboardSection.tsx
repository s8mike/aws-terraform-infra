/**
 * Reusable dashboard content section.
 *
 * Provides consistent spacing and visual
 * structure for dashboard content areas.
 *
 * Phase 17.14.2 - Dashboard Foundation
 */

import type { ReactNode } from "react";

interface DashboardSectionProps {
  title: string;
  children: ReactNode;
}

// Shared dashboard section container.
export default function DashboardSection({
  title,
  children,
}: DashboardSectionProps) {
  return (
    <section className="rounded-lg border bg-white p-5 shadow-sm">
      {/* Section heading */}
      <h2 className="text-lg font-semibold text-gray-900">
        {title}
      </h2>

      {/* Section content */}
      <div className="mt-4">
        {children}
      </div>
    </section>
  );
}