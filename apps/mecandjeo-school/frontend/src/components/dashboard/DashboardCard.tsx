/**
 * Reusable dashboard summary card.
 *
 * Displays a label, value, and optional
 * supporting description.
 *
 * Phase 17.14.2 - Dashboard Foundation
 */

interface DashboardCardProps {
  title: string;
  value: string | number;
  description?: string;
}

// Shared dashboard summary/statistic card.
export default function DashboardCard({
  title,
  value,
  description,
}: DashboardCardProps) {
  return (
    <div className="rounded-lg border bg-white p-5 shadow-sm">
      {/* Card label */}
      <p className="text-sm font-medium text-gray-500">
        {title}
      </p>

      {/* Card value */}
      <p className="mt-2 text-2xl font-bold text-gray-900">
        {value}
      </p>

      {/* Optional supporting information */}
      {description && (
        <p className="mt-1 text-xs text-gray-500">
          {description}
        </p>
      )}
    </div>
  );
}