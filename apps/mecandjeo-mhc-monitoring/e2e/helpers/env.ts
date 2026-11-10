// Finds the admin login for the tests: environment variables first, then the stack's own .env.docker settings file.
import fs from 'node:fs'
import path from 'node:path'

// Read one KEY=value setting from .env.docker (the folder above e2e/), ignoring Windows line endings.
function readEnvFileValue(key: string): string | undefined {
  const file = path.resolve(__dirname, '..', '..', '.env.docker')
  if (!fs.existsSync(file)) return undefined
  const line = fs
    .readFileSync(file, 'utf-8')
    .split(/\r?\n/)
    .find((candidate) => candidate.startsWith(`${key}=`))
  return line?.slice(key.length + 1)
}

export const adminEmail =
  process.env.E2E_ADMIN_EMAIL ?? readEnvFileValue('BOOTSTRAP_ADMIN_EMAIL') ?? 'admin@example.com'

export const adminPassword = process.env.E2E_ADMIN_PASSWORD ?? readEnvFileValue('BOOTSTRAP_ADMIN_PASSWORD')