// Login screen: collects email and password, shows server errors, then sends the user to their role's home page.
import { useState, type FormEvent } from 'react'
import { Navigate } from 'react-router-dom'
import { ApiError } from '../api/client'
import { homePathForRole } from '../auth/roles'
import { useAuth } from '../auth/useAuth'
import PasswordInput from '../components/PasswordInput'

export default function LoginPage() {
  const { user, loading, login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  // Submit the form: on success the user state changes and the redirect below takes over.
  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      await login(email.trim(), password)
    } catch (caught) {
      setError(
        caught instanceof ApiError ? caught.message : 'Could not reach the server. Is the API running?',
      )
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <p className="status-message">Loading…</p>
  // Already signed in: skip the form.
  if (user) return <Navigate to={homePathForRole(user.role)} replace />

  return (
    <div className="login-wrap">
      <form className="login-card" onSubmit={handleSubmit}>
        <h1>Mecandjeo MHC Monitoring</h1>
        <p>Sign in to continue</p>

        {error && (
          <p className="error-message" role="alert">
            {error}
          </p>
        )}

        {/* Plain email input. */}
        <div className="form-field">
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            autoComplete="username"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </div>

        {/* Password input with the show/hide eye button. */}
        <PasswordInput id="password" label="Password" value={password} onChange={setPassword} />

        <button type="submit" className="primary-button" disabled={submitting}>
          {submitting ? 'Signing in…' : 'Sign in'}
        </button>
      </form>
    </div>
  )
}