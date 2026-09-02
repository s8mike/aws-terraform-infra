/**
 * Reusable dashboard header.
 *
 * Phase 19.7 - Dashboard Visual Polish
 */

interface DashboardHeaderProps {
  title: string;
  description: string;
}

// Provides consistent dashboard heading hierarchy.
export default function DashboardHeader({
  title,
  description,
}: DashboardHeaderProps) {
  return (
    <div className="mb-6">
      {/* Primary dashboard heading */}
      <h1 className="text-2xl font-bold tracking-tight text-gray-900 sm:text-3xl">
        {title}
      </h1>

      {/* Supporting dashboard context */}
      <p className="mt-2 max-w-3xl text-sm leading-6 text-gray-600">
        {description}
      </p>
    </div>
  );
}