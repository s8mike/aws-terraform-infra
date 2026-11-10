// Live checklist of the password rules: each line is red with a cross until it is met, then green with a tick.
import { passwordChecks } from '../../utils/validation'

interface PasswordRulesProps {
  password: string
  required: boolean // false when editing a user, where a blank password means "keep the current one"
}

export default function PasswordRules({ password, required }: PasswordRulesProps) {
  // Editing without a new password: there is nothing to check.
  if (password === '' && !required) {
    return <p className="hint">Leave the password blank to keep the current one.</p>
  }

  return (
    <ul className="rule-list" aria-live="polite">
      {passwordChecks(password).map((check) => (
        <li key={check.label} className={check.met ? 'rule rule-met' : 'rule rule-unmet'}>
          {check.met ? '✓' : '✗'} {check.label}
        </li>
      ))}
    </ul>
  )
}