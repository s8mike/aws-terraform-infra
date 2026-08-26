/**
 * Reusable dashboard header.
 *
 * Displays the dashboard title and
 * contextual welcome message.
 *
 * Phase 17.14.2 - Dashboard Foundation
 */

interface DashboardHeaderProps {
  title: string;
  description: string;
}

// Shared dashboard heading component.
export default function DashboardHeader({
  title,
  description,
}: DashboardHeaderProps) {
  return (
    <div className="mb-6">
      {/* Dashboard page title */}
      <h1 className="text-2xl font-bold text-gray-900">
        {title}
      </h1>

      {/* Dashboard contextual description */}
      <p className="mt-1 text-sm text-gray-600">
        {description}
      </p>
    </div>
  );
}