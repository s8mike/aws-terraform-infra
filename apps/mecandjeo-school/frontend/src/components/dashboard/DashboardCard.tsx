/**
 * Reusable dashboard summary card.
 *
 * Phase 19.8 - Loading, Empty State & User Feedback
 */

interface DashboardCardProps {
  title: string;
  value: string | number;
  description?: string;
  loading?: boolean;
}

// Consistent dashboard statistic card with loading feedback.
export default function DashboardCard({
  title,
  value,
  description,
  loading = false,
}: DashboardCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
      {/* Statistic label */}
      <p className="text-sm font-medium text-gray-500">
        {title}
      </p>

      {loading ? (
        /* Loading placeholder while dashboard data is retrieved */
        <div
          className="mt-3 h-7 w-16 animate-pulse rounded bg-gray-200"
          aria-label="Loading"
        />
      ) : (
        <>
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
        </>
      )}
    </div>
  );
}