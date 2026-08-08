/**
 * Admin dashboard page.
 *
 * Accessible only by users
 * with admin role.
 */

export default function AdminDashboard() {
  return (
    <div className="p-8">

      <h1 className="text-3xl font-bold">
        Admin Dashboard
      </h1>

      <p className="mt-4">
        Welcome to the administrator area.
      </p>

    </div>
  );
}