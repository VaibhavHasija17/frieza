# dev-workflow

Company-standard Claude Code workflow, shipped as a plugin marketplace. Claude sets everything up itself through `/workflow:setup`.

## Get started

Once per machine, inside Claude Code:

```
/plugin marketplace add VaibhavHasija17/frieza
/plugin install workflow@dev-workflow
/workflow:setup
```

Or just tell Claude: *"Add the VaibhavHasija17/frieza plugin marketplace and install workflow@dev-workflow at user scope"*, restart Claude Code, then run `/workflow:setup`.

In each project, run `/workflow:setup`. Claude inspects the machine and the repo (OS, missing tools, stack, commands, branches, commit style, PR template, existing AI config), shows a plan adapted to that project, and applies it after you confirm. Then commit `.claude/settings.json` and `CLAUDE.md`. Teammates who open that project and trust the folder are prompted to install the workflow plugin; they run `/workflow:setup` once to set up their machine.

Restart Claude Code after setup so new plugins load.

Generated files are created once and committed; git is the source of truth. On other machines `/workflow:setup` reuses the committed files and only edits a file when the code it describes changed since the commit stamped at its end (`<!-- workflow:setup <sha> -->`). Pull before running setup on a project someone else already set up. Machine-specific notes go in the gitignored `CLAUDE.local.md`.

Project differences are recorded in the **Workflow** section of the project's CLAUDE.md (branch naming, commit format, protected branches, PR template, solution docs folder). All `/workflow:*` skills follow it.

Requirements: Node.js 20+, `python3`, `openpyxl` or `uv` (for the test case sheet), `git`, `gh`. Private repo: each developer needs git access to it.

## What you get

| Piece | What it does |
|-------|--------------|
| `/workflow:setup` | Inspects machine and project, shows an adapted plan, then installs the machine-level plugins below, configures `.claude/settings.json` (plugin, protected branches, allowed lint/test commands), creates or updates `CLAUDE.md` from the repo, and writes a brief `CLAUDE.md` in each module folder (purpose, key files, connections, notes). Safe to re-run. |
| `/workflow:dev <prd>` | One flow, pausing for approval after each stage: **solution** (PRD + codebase analysis → technical solution doc with APIs, DB and code changes, in `docs/solutions/`; format in `plugins/workflow/skills/dev/solution-template.md`; plus a `-test-cases.xlsx` sheet generated from the PRD) → **start** (checks tree, suggests a `type/TICKET-slug` branch, never creates it) → **build** (implements the doc task by task, tests as it goes) → **test** (runs every test case and marks it Passed / Failed / Human review needed, with evidence; a failing case gets 3 fix-and-retest attempts, shown as Retrying, before it is marked Failed) → **review** (runs `/workflow:review`; fixes Critical and Major findings, re-tests) → **commit** (checks, explicit staging, Conventional Commit with `Refs: TICKET`) → **pr** (warns if behind, never rebases; self-review, push, PR linking the solution doc). Run with no input to resume where the work is, or `/workflow:dev commit` / `/workflow:dev pr` to jump to a stage. |
| `/workflow:review [PR \| files]` | Code review of the current branch (default), a PR, or files. Checks correctness, security, data, API contract, tests, conventions, and the solution doc. Verifies each finding with a concrete scenario; reports Critical / Major / Minor / Question with a verdict. Read-only; posts to a PR only if you agree. |
| Guard hook | Blocks force push, direct push to protected branches (default `main`/`master`/`develop`; per project via `WORKFLOW_PROTECTED_BRANCHES` in `.claude/settings.json`, globs allowed), `rm -r` on `/` or `~`, and edits to `.env*` files. |

Machine-level plugins installed by `/workflow:setup` (user scope, active in every project):

| Plugin | What it does |
|--------|--------------|
| [ponytail](https://github.com/DietrichGebert/ponytail) | Keeps solutions minimal (YAGNI, stdlib first). |
| [playwright](https://github.com/microsoft/playwright-mcp) | Playwright MCP server. Lets Claude drive a browser: open pages, click, fill forms, screenshot. |
| [claude-mem](https://github.com/thedotmack/claude-mem) | Persistent memory across sessions. Runs a local worker and injects relevant past work into new sessions. Asks you to sign in and pick a memory provider; follow company policy on which one is allowed. |
| [claude-md-management](https://github.com/anthropics/claude-plugins-official) | Audits and updates CLAUDE.md files with learnings from sessions. |
| [security-guidance](https://github.com/anthropics/claude-plugins-official) | Warns about insecure code patterns while editing. |
| [superpowers](https://github.com/obra/superpowers) | Brainstorming, planning, TDD, debugging, and code-review workflows. |

## Usage tracking

`/workflow:setup` turns on Claude Code's built-in OpenTelemetry export on each developer's machine, so a central dashboard shows Claude usage per developer, team, and repository.

**Turn it on (once, for the company):**

1. Run an OpenTelemetry collector that feeds your metrics backend (Grafana/Prometheus, Datadog, New Relic, Honeycomb, etc.).
2. Set its URL in `plugins/workflow/skills/setup/telemetry.json`:
   ```json
   { "endpoint": "https://otel.example.com:4318", "protocol": "http/protobuf", "temporality": "cumulative",
     "needs_token": false, "auth_scheme": "Bearer", "export_events": false }
   ```
   - `temporality`: `cumulative` for Prometheus, Grafana, and Mimir; `delta` for backends that prefer it (e.g. Datadog).
   - `auth_scheme`: `Basic` for Grafana Cloud, `Bearer` for most others.
   - `needs_token: true` means the collector needs a token. Setup uses `token` from the file if set (then developers enter nothing; use a write-only token, since everyone with repo access can read it), otherwise asks each developer and stores it only in their `~/.claude/settings.json`.
   - `service_name`: optional; shows as the `job` label in Grafana.
   - `export_events: true` also sends per-request events (API calls, tool decisions). Prompts and code stay redacted.
3. Push, and have developers re-run `/workflow:setup`. While `endpoint` is empty, setup skips usage tracking.

**On the dashboard** (metric names): `claude_code.cost.usage` and `claude_code.token.usage` (by model, skill, plugin), `claude_code.session.count`, `claude_code.active_time.total`, `claude_code.lines_of_code.count`, `claude_code.commit.count`, `claude_code.pull_request.count`. Labels include `user.email`, `team.id`, and `vcs.repository.name`. `/workflow:dev` and `/workflow:review` usage shows up under `skill.name`.

**Not sent:** prompts, responses, code, file contents, commands.

Developers can switch these settings off on their own machine. To enforce them, an admin can put the same `env` values in Claude Code managed settings instead.

## Change the workflow

1. Edit files under `plugins/workflow/`. The plugin list lives in `skills/setup/SKILL.md`; the CLAUDE.md starting point in `skills/setup/CLAUDE.md.template`.
2. Bump `version` in `plugins/workflow/.claude-plugin/plugin.json`.
3. Run `python3 plugins/workflow/hooks/test_guard.py` after guard changes, and `python3 plugins/workflow/skills/dev/test_testsheet.py` after test sheet changes.
4. Merge to the default branch. Developers get the update via `/plugin marketplace update dev-workflow`.

Test locally before merging: `claude --plugin-dir ./plugins/workflow`.
