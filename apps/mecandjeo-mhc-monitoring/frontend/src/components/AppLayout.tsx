// Page frame shown to signed-in users: header with navigation (admins), the user's name and role, theme picker, change-password, sign-out, and the page below.
// The data-role attribute gives each role its accent color; the theme picker changes the page and panel colors.
import { useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../auth/useAuth'
import { THEMES, isThemeId } from '../theme/themes'
import { useTheme } from '../theme/useTheme'
import ChangePasswordDialog from './ChangePasswordDialog'

export default function AppLayout() {
  const { user, logout } = useAuth()
  const { theme, setTheme } = useTheme(user?.id)
  const [changingPassword, setChangingPassword] = useState(false)

  return (
    <div className="app-shell" data-role={user?.role}>
      <header className="app-header">
        <strong>Mecandjeo MHC Monitoring</strong>
        {/* Admins can open both the manager screens and the admin screens. */}
        {user?.role === 'admin' && (
          <nav className="app-nav">
            <NavLink to="/manager">Manager view</NavLink>
            <NavLink to="/admin">Admin</NavLink>
          </nav>
        )}
        <span className="app-user">
          {user?.full_name} ({user?.role})
        </span>
        <select
          className="theme-select"
          aria-label="Color theme"
          value={theme}
          onChange={(event) => {
            if (isThemeId(event.target.value)) setTheme(event.target.value)
          }}
        >
          {THEMES.map((option) => (
            <option key={option.id} value={option.id}>
              {option.label}
            </option>
          ))}
        </select>
        <button type="button" className="link-button" onClick={() => setChangingPassword(true)}>
          Change password
        </button>
        <button type="button" className="link-button" onClick={logout}>
          Sign out
        </button>
      </header>
      <main className="app-main">
        <Outlet />
      </main>

      {changingPassword && <ChangePasswordDialog onClose={() => setChangingPassword(false)} />}
    </div>
  )
}