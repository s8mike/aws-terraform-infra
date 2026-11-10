// Tests for the login screen: fields, success and error messages, the busy state, and the redirect for a signed-in user.
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import { ApiError } from '../api/client'
import { AuthContext, type AuthContextValue } from '../auth/AuthContext'
import { makeAuth, makeUser } from '../test/authTestUtils'
import LoginPage from './LoginPage'

// Render the login page at /login with a stand-in operator home page for the redirect.
function renderLogin(auth: AuthContextValue) {
  return render(
    <AuthContext.Provider value={auth}>
      <MemoryRouter initialEntries={['/login']}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/operator" element={<p>Operator home</p>} />
        </Routes>
      </MemoryRouter>
    </AuthContext.Provider>,
  )
}

// Type credentials and press Sign in.
async function signIn(user: ReturnType<typeof userEvent.setup>, email: string, password: string) {
  await user.type(screen.getByLabelText('Email'), email)
  await user.type(screen.getByLabelText('Password'), password)
  await user.click(screen.getByRole('button', { name: 'Sign in' }))
}

describe('LoginPage', () => {
  it('shows an email field and a hidden password field', () => {
    renderLogin(makeAuth())

    expect(screen.getByLabelText('Email')).toHaveAttribute('type', 'email')
    expect(screen.getByLabelText('Password')).toHaveAttribute('type', 'password')
  })

  it('calls login with the typed email and password', async () => {
    const user = userEvent.setup()
    const login = vi.fn<AuthContextValue['login']>().mockResolvedValue(makeUser('operator'))
    renderLogin(makeAuth({ login }))

    await signIn(user, 'operator1@example.com', 'Securepass123!')

    expect(login).toHaveBeenCalledWith('operator1@example.com', 'Securepass123!')
  })

  it('shows the server message for a wrong email or password', async () => {
    const user = userEvent.setup()
    const login = vi.fn<AuthContextValue['login']>().mockRejectedValue(new ApiError(401, 'Invalid email or password'))
    renderLogin(makeAuth({ login }))

    await signIn(user, 'operator1@example.com', 'wrong')

    expect(await screen.findByRole('alert')).toHaveTextContent('Invalid email or password')
  })

  it('shows a helpful message when the API cannot be reached', async () => {
    const user = userEvent.setup()
    const login = vi.fn<AuthContextValue['login']>().mockRejectedValue(new Error('network down'))
    renderLogin(makeAuth({ login }))

    await signIn(user, 'operator1@example.com', 'Securepass123!')

    expect(await screen.findByRole('alert')).toHaveTextContent('Could not reach the server. Is the API running?')
  })

  it('disables the button and shows progress while signing in', async () => {
    const user = userEvent.setup()
    const login = vi.fn<AuthContextValue['login']>().mockReturnValue(new Promise(() => {}))
    renderLogin(makeAuth({ login }))

    await signIn(user, 'operator1@example.com', 'Securepass123!')

    expect(screen.getByRole('button', { name: 'Signing in…' })).toBeDisabled()
  })

  it('skips the form and goes to the role home when someone is already signed in', () => {
    renderLogin(makeAuth({ user: makeUser('operator') }))

    expect(screen.getByText('Operator home')).toBeInTheDocument()
    expect(screen.queryByLabelText('Email')).not.toBeInTheDocument()
  })
})