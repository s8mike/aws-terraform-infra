// Runs the tests for the folder you are standing in: "cd src/utils" then "npm run test:here" runs only the utils tests.
// From the frontend folder itself it runs every test. npm records where it was started in INIT_CWD.
import { spawnSync } from 'node:child_process'
import path from 'node:path'

const root = process.cwd()
const startedIn = process.env.INIT_CWD ?? root

// The folder you started in, relative to the frontend folder, with forward slashes (what Vitest expects).
const relative = path.relative(root, startedIn).split(path.sep).join('/')
const args = [path.join(root, 'node_modules', 'vitest', 'vitest.mjs'), 'run']
if (relative !== '' && !relative.startsWith('..')) args.push(relative)

// Run Vitest with the same Node that is running this script, so no shell or extra tools are needed.
const result = spawnSync(process.execPath, args, { stdio: 'inherit' })
process.exit(result.status ?? 1)