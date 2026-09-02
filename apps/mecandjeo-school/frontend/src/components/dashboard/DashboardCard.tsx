/**
 * Reusable dashboard summary card.
 *
 * Phase 19.7 - Dashboard Visual Polish
 */

interface DashboardCardProps {
  title: string;
  value: string | number;
  description?: string;
}

// Consistent visual treatment for dashboard statistics.
export default function DashboardCard({
  title,
  value,
  description,
}: DashboardCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
      {/* Statistic label */}
      <p className="text-sm font-medium text-gray-500">
        {title}
      </p>

      {/* Primary statistic value */}
      <p className="mt-2 text-2xl font-bold tracking-tight text-gray-900">
        {value}
      </p>

      {/* Supporting context */}
      {description && (
        <p className="mt-2 text-xs leading-5 text-gray-500">
          {description}
        </p>
      )}
    </div>
  );
}