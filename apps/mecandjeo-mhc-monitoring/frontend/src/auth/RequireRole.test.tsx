// Tests for the route guard: allowed roles pass, wrong roles go to their own home, and signed-out users go to /login.
import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import type { Role } from '../api/types'
import { makeAuth, makeUser } from '../test/authTestUtils'
import { AuthContext, type AuthContextValue } from './AuthContext'
import { homePathForRole } from './roles'
import RequireRole from './RequireRole'

// Render a small app where /manager is guarded for managers and admins, starting at the given path.
function renderGuarded(path: string, auth: AuthContextValue) {
  return render(
    <AuthContext.Provider value={auth}>
      <MemoryRouter initialEntries={[path]}>
        <Routes>
          <Route path="/login" element={<p>Login page</p>} />
          <Route element={<RequireRole allowed={['manager', 'admin']} />}>
            <Route path="/manager" element={<p>Manager page</p>} />
          </Route>
          <Route path="/operator" element={<p>Operator home</p>} />
          <Route path="/admin" element={<p>Admin home</p>} />
        </Routes>
      </MemoryRouter>
    </AuthContext.Provider>,
  )
}

describe('RequireRole', () => {
  it.each<Role>(['manager', 'admin'])('lets a %s open the guarded page', (role) => {
    renderGuarded('/manager', makeAuth({ user: makeUser(role) }))

    expect(screen.getByText('Manager page')).toBeInTheDocument()
  })

  it('sends an operator back to the operator home instead of the manager page', () => {
    renderGuarded('/manager', makeAuth({ user: makeUser('operator') }))

    expect(screen.getByText('Operator home')).toBeInTheDocument()
    expect(screen.queryByText('Manager page')).not.toBeInTheDocument()
  })

  it('sends a signed-out visitor to the login page', () => {
    renderGuarded('/manager', makeAuth({ user: null }))

    expect(screen.getByText('Login page')).toBeInTheDocument()
  })

  it('waits while the saved session is being checked', () => {
    renderGuarded('/manager', makeAuth({ user: null, loading: true }))

    expect(screen.getByText('Loading…')).toBeInTheDocument()
    expect(screen.queryByText('Login page')).not.toBeInTheDocument()
  })
})

describe('homePathForRole', () => {
  it('maps every role to its own home page', () => {
    expect(homePathForRole('operator')).toBe('/operator')
    expect(homePathForRole('manager')).toBe('/manager')
    expect(homePathForRole('admin')).toBe('/admin')
  })
})