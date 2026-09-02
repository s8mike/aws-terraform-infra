/**
 * Login page for application authentication.
 *
 * Provides credential validation, authentication
 * submission, and user feedback.
 *
 * Phase 19.9 - Forms & Interactions
 */

import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../../contexts/AuthContext";
import { login as loginService } from "../../services/authService";

// Validate credentials before sending them to the backend.
const loginSchema = z.object({
  email: z.email("Please enter a valid email address"),
  password: z.string().min(1, "Password is required"),
});

type LoginFormData = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  // Submit credentials and establish the authenticated session.
  const onSubmit = async (data: LoginFormData) => {
    try {
      setLoading(true);
      setError("");

      const response = await loginService(data);

      login(response);

      navigate("/dashboard", {
        replace: true,
      });
    } catch (error: any) {
      console.error("Login failed:", error);

      setError(
        error?.response?.data?.detail ||
          "Invalid email or password"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4 py-8">
      {/* Responsive form container for mobile, tablet and desktop. */}
      <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-md sm:p-8">

        <h1 className="mb-2 text-center text-2xl font-bold sm:text-3xl">
          MECANDJEO LMS
        </h1>

        <p className="mb-8 text-center text-gray-500">
          Sign in to continue
        </p>

        <form
          onSubmit={handleSubmit(onSubmit)}
          className="space-y-5"
          noValidate
        >
          {/* Email field */}
          <div>
            <label
              htmlFor="email"
              className="mb-2 block text-sm font-medium text-gray-900"
            >
              Email
            </label>

            <input
              id="email"
              type="email"
              autoComplete="email"
              placeholder="admin@mecandjeo-school.com"
              aria-invalid={errors.email ? "true" : "false"}
              aria-describedby={
                errors.email ? "email-error" : undefined
              }
              className="w-full rounded-md border border-gray-300 px-3 py-2.5 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              {...register("email")}
            />

            {errors.email && (
              <p
                id="email-error"
                className="mt-1 text-sm text-red-600"
              >
                {errors.email.message}
              </p>
            )}
          </div>

          {/* Password field */}
          <div>
            <label
              htmlFor="password"
              className="mb-2 block text-sm font-medium text-gray-900"
            >
              Password
            </label>

            <div className="relative">
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
                placeholder="Enter password"
                aria-invalid={errors.password ? "true" : "false"}
                aria-describedby={
                  errors.password
                    ? "password-error"
                    : undefined
                }
                className="w-full rounded-md border border-gray-300 px-3 py-2.5 pr-12 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                {...register("password")}
              />

              {/* Password visibility control. */}
              <button
                type="button"
                onClick={() =>
                  setShowPassword((visible) => !visible)
                }
                aria-label={
                  showPassword
                    ? "Hide password"
                    : "Show password"
                }
                title={
                  showPassword
                    ? "Hide password"
                    : "Show password"
                }
                className="absolute right-2 top-1/2 -translate-y-1/2 rounded-md p-2 text-gray-500 transition hover:bg-gray-100 hover:text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {showPassword ? (
                  <EyeOff size={18} />
                ) : (
                  <Eye size={18} />
                )}
              </button>
            </div>

            {errors.password && (
              <p
                id="password-error"
                className="mt-1 text-sm text-red-600"
              >
                {errors.password.message}
              </p>
            )}
          </div>

          {/* Backend authentication error. */}
          {error && (
            <div
              role="alert"
              className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700"
            >
              {error}
            </div>
          )}

          {/* Disable duplicate submissions while authentication is pending. */}
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-black px-4 py-2.5 font-medium text-white transition hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>
      </div>
    </div>
  );
}