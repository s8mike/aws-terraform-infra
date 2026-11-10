// Dialog where a signed-in user changes their own password: current password, new password with the live rule checklist, and a confirmation.
import { useEffect, useState, type FormEvent } from 'react'
import { changePassword } from '../api/auth'
import { errorMessage } from '../utils/errors'
import { passwordProblem } from '../utils/validation'
import PasswordRules from './admin/PasswordRules'
import PasswordInput from './PasswordInput'

export default function ChangePasswordDialog({ onClose }: { onClose: () => void }) {
  const [current, setCurrent] = useState('')
  const [next, setNext] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [done, setDone] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  // Close the dialog when the Escape key is pressed.
  useEffect(() => {
    function handleKey(event: KeyboardEvent) {
      if (event.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [onClose])

  // Live mismatch warning shown as soon as the confirmation differs from the new password.
  const mismatch = confirm !== '' && confirm !== next

  // Check everything locally first, then call the API; a wrong current password shows the server's message.
  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)

    const problem = passwordProblem(next)
    if (problem) {
      setError(problem)
      return
    }
    if (next !== confirm) {
      setError('The new password and its confirmation do not match.')
      return
    }
    if (next === current) {
      setError('The new password must be different from the current one.')
      return
    }

    setSubmitting(true)
    try {
      await changePassword({ current_password: current, new_password: next })
      setDone(true)
    } catch (caught) {
      setError(errorMessage(caught))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    // Clicking the dimmed area outside the panel also closes the dialog.
    <div
      className="dialog-backdrop"
      onClick={(event) => {
        if (event.target === event.currentTarget) onClose()
      }}
    >
      <div className="panel dialog" role="dialog" aria-modal="true" aria-labelledby="change-password-title">
        <h2 id="change-password-title">Change password</h2>

        {done ? (
          <>
            <p className="success-message">Your password has been changed. Use it the next time you sign in.</p>
            <button type="button" className="primary-button retry-button" onClick={onClose}>
              Close
            </button>
          </>
        ) : (
          <form onSubmit={handleSubmit}>
            {error && (
              <p className="error-message" role="alert">
                {error}
              </p>
            )}

            <PasswordInput id="current-password" label="Current password" value={current} onChange={setCurrent} autoComplete="current-password" />
            <PasswordInput id="new-password" label="New password" value={next} onChange={setNext} autoComplete="new-password" />
            <PasswordRules password={next} required />
            <PasswordInput id="confirm-password" label="Confirm new password" value={confirm} onChange={setConfirm} autoComplete="new-password" />
            {mismatch && <p className="rule rule-unmet">✗ The two new passwords do not match.</p>}

            <div className="form-actions">
              <button type="submit" className="primary-button retry-button" disabled={submitting}>
                {submitting ? 'Saving…' : 'Change password'}
              </button>
              <button type="button" className="secondary-button" onClick={onClose}>
                Cancel
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}