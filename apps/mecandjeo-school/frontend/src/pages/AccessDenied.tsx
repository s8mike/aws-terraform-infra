/**
 * Access denied page.
 *
 * Displayed when an authenticated user
 * tries to access a page without permission.
 */

import { Link } from "react-router-dom";

export default function AccessDenied() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6">

      <h1 className="text-4xl font-bold text-red-600">
        403
      </h1>

      <h2 className="mt-4 text-2xl font-semibold">
        Access Denied
      </h2>

      <p className="mt-4 text-gray-600 text-center max-w-md">
        You are signed in, but you do not have permission
        to access this page.
      </p>

      <Link
        to="/dashboard"
        className="mt-8 rounded-lg bg-blue-600 px-6 py-3 text-white hover:bg-blue-700"
      >
        Return to Dashboard
      </Link>

    </div>
  );
}