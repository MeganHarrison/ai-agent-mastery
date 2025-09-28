# Playwright Browser Testing

Scope: Local development inside Visual Studio Code using Claude CLI.
Rule: If Claude says “done” without today’s Playwright evidence bundle, the task is NOT done.

0) Non-negotiable principles
	•	No hallucinations. No lies. If something wasn’t run now, say so.
	•	Primary Claude is accountable. Sub-agents may help, but Claude must run the commands and attach evidence.
	•	Real UX, not page loads. “It loads” ≠ functionality. We validate real user flows, end-to-end.
	•	No “authorization required” excuses. Use Playwright auth patterns (storage state, service tokens, seed routes).
Docs: https://playwright.dev/docs/auth

⸻

1) What Claude must do locally before saying “done”

Claude CLI must execute all of the following, and paste the outputs/paths into the chat:
	1.	Generate/refresh auth (global setup)

npx playwright test --global-setup
# produces: e2e/.auth/storageState.json

	2.	Run the specific e2e tests for this feature (not just the whole suite)

npx playwright test e2e/<feature>.spec.ts --project=chromium

	3.	Save and show evidence

	•	Screenshots at key steps (explicit page.screenshot() in tests)
	•	Trace: on first retry or failures (per config)
	•	Run stamp (e2e/.artifacts/run-stamp.json with commit/baseURL/timestamp)
	•	Console/network check: fail if unexpected errors or “authorization required” appear

	4.	For RAG/AI: assert must/must-not content and citation presence in the DOM.

If any of the above cannot be completed right now, Claude must say “NOT DONE: <reason + next step>” — never “done”.

⸻

2) Required local config (baseline)

playwright.config.ts

import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: 'e2e',
  timeout: 90_000,
  expect: { timeout: 10_000 },
  fullyParallel: true,
  retries: process.env.CI ? 2 : 0,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    storageState: 'e2e/.auth/storageState.json',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 15_000,
    navigationTimeout: 30_000
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  outputDir: 'e2e/.artifacts',
  globalSetup: './e2e/global-setup.ts'
});

e2e/global-setup.ts (no excuses for auth)
Creates storageState.json via test user login or non-interactive session.

import { chromium, FullConfig } from '@playwright/test';

export default async function globalSetup(_: FullConfig) {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto(`${process.env.BASE_URL}/login`);
  await page.fill('#email', process.env.E2E_USER_EMAIL!);
  await page.fill('#password', process.env.E2E_USER_PASSWORD!);
  await Promise.all([page.waitForURL('**/dashboard'), page.click('button[type=submit]')]);
  await page.context().storageState({ path: 'e2e/.auth/storageState.json' });
  await browser.close();
}

If SSO blocks UI login, use a service token or a test-only seed route to mint a session cookie and write storageState.json. Reference: https://playwright.dev/docs/auth

⸻

3) “Real functionality” test skeletons (local)

Positive UX flow (RAG chat example):

// e2e/rag-chat.spec.ts
import { test, expect } from '@playwright/test';

const MUST = ['Pro plan', '$49', 'monthly'];
const NEVER = ['lifetime $29', 'N/A'];

test('RAG Chat — answers real question with citations', async ({ page }, testInfo) => {
  await page.goto('/chat');
  await expect(page.getByTestId('chat-input')).toBeVisible();

  await page.getByTestId('chat-input').fill('What is included in the Pro plan?');
  await page.getByTestId('chat-send').click();

  const resp = page.getByTestId('chat-message-last');
  await expect(resp).toBeVisible({ timeout: 20_000 });

  const text = await resp.innerText();
  for (const m of MUST) expect.soft(text).toContain(m);
  for (const n of NEVER) expect.soft(text).not.toContain(n);
  await expect(page.locator('[data-test="citation-id"]')).toBeVisible();

  await page.screenshot({ path: `e2e/.artifacts/rag-proof-${testInfo.retry}.png`, fullPage: true });
});

Negative path (graceful failure):

test('RAG Chat — retrieval failure handled', async ({ page }) => {
  await page.goto('/chat?injectFailure=true');
  await page.getByTestId('chat-input').fill('Trigger failure');
  await page.getByTestId('chat-send').click();
  await expect(page.getByText(/we’re having trouble/i)).toBeVisible();
});

Run stamp helper (called in a beforeAll or last step):

// e2e/saveRunStamp.ts
import fs from 'node:fs';
export function saveRunStamp() {
  const stamp = {
    commit: process.env.GIT_COMMIT || 'local',
    baseURL: process.env.BASE_URL,
    date: new Date().toISOString()
  };
  fs.writeFileSync('e2e/.artifacts/run-stamp.json', JSON.stringify(stamp, null, 2));
}


⸻

4) VS Code integration (tasks & commands Claude must run)

.vscode/tasks.json (so Claude can call tasks deterministically)

{
  "version": "2.0.0",
  "tasks": [
    { "label": "e2e:auth", "type": "shell", "command": "npx playwright test --global-setup" },
    { "label": "e2e:feature", "type": "shell", "command": "npx playwright test e2e/${input:spec} --project=chromium" },
    { "label": "e2e:open-report", "type": "shell", "command": "npx playwright show-report" }
  ],
  "inputs": [{ "id": "spec", "type": "promptString", "description": "Path to spec (e.g., rag-chat.spec.ts)" }]
}

In chat, Claude should run:

	•	Task: e2e:auth
	•	Task: e2e:feature (e2e/rag-chat.spec.ts)
	•	Task: e2e:open-report (optional to preview locally)

⸻

5) The only acceptable “DONE” message in local CLI chat

Claude must paste this exact block, filled out, when claiming completion:

✅ LOCAL COMPLETION PROOF (Playwright)

Feature: <name>
Base URL: <http://localhost:3000 or staging URL>
Run At: <ISO timestamp>

Tests:
- e2e/<file>.spec.ts :: <test name> — PASSED
- e2e/<file>.spec.ts :: <negative test name> — PASSED

Artifacts:
- Screenshot(s): e2e/.artifacts/<proof>.png
- Trace: e2e/.artifacts/trace.zip (if retry/failure occurred)
- Run Stamp: e2e/.artifacts/run-stamp.json

Auth:
- storageState: e2e/.auth/storageState.json (generated now via global-setup)

RAG Assertions (if applicable):
- MUST: "<term1>", "<term2>", "<term3>"
- MUST-NOT: "<termA>", "<termB>"
- Citation selector visible: [data-test="citation-id"]

Terminal excerpts:
<last ~40 lines of `npx playwright test ...` output, including PASS summary>

If any line above is missing or paths don’t exist on disk → “NOT DONE.”

⸻

6) Auto-fail triggers Claude must respect (locally)
	•	“authorization required” appears in terminal/logs/screenshots → NOT DONE (fix auth via storage state; see docs above).
	•	Only page load was tested, no user action/result → NOT DONE.
	•	No screenshot of the final, meaningful state → NOT DONE.
	•	No negative path → NOT DONE (unless feature is read-only and justified).
	•	Evidence timestamp isn’t today for the active environment → NOT DONE.

⸻

7) Quick command palette for Claude CLI
	•	npx playwright test --global-setup
	•	npx playwright test e2e/<feature>.spec.ts --project=chromium
	•	npx playwright show-report (optional)
	•	(RAG) Ensure tests include must/must-not and citation checks.

⸻

8) Allowed excuses

None. If something blocks execution, Claude must return “NOT DONE:  + exact next command(s) to unblock” — not a success claim.

⸻

Ideas to go deeper / make it better
	•	Claude task macro: one VS Code task that runs global-setup → feature spec → stamps artifacts → prints completion block automatically.
	•	Local artifact viewer: lightweight npm run artifacts:open to open the latest proof screenshot and trace viewer.
	•	RAG golden answers: keep JSON of expected strings/IDs per intent; import into tests so adding a new use case is trivial.
	•	Claude guardrail: a CLI preflight script that refuses to allow Claude to send “done” unless the artifact files exist and are touched within the last X minutes.

Want me to generate the .vscode/tasks.json and a tiny scripts/local-proof.ts that prints the DONE block automatically after a run?

https://playwright.dev/docs/auth