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
| `/workflow:dev <prd or bug>` | One flow, pausing for approval after each stage: **1 solution** (runs `/workflow:clarify`, writes a technical solution doc with APIs, DB and code changes plus a `-test-cases.xlsx` sheet in `docs/solutions/` written from the PRD by the independent tester agent, then runs `/workflow:challenge` on the doc) or **1 diagnose** for bugs (runs `/workflow:diagnose`: reproduce, root cause, test sheet) → **start** (asks you for the branch name, then creates it; never invents a name) → **build** (runs `/workflow:build`) → **test** (the tester agent runs every case, then end-to-end journeys and smoke checks of critical existing flows in the browser, and marks it Passed / Failed / Human review needed with evidence; 3 fix-and-retest attempts, shown as Retrying, before Failed; then definition of done and `/workflow:quality-bar check`) → **review** (runs `/workflow:review`; fixes Critical and Major findings) → **commit** (checks, explicit staging, Conventional Commit with `Refs: TICKET`) → **pr** (runs `/workflow:pr`). Run with no input to resume where the work is, or name a stage to jump to it. |
| `/workflow:clarify <prd or plan>` | Interviews you in rounds until every decision is settled. Each question comes with a recommended answer ("yes" accepts it); Claude looks up facts itself and only asks for decisions. Ends with a confirmed Decisions list. |
| `/workflow:diagnose <bug>` | Bug loop: a fast command that reproduces the bug first, then minimise, hypothesise, confirm the root cause, fix, regression test, clean up. |
| `/workflow:build <plan>` | Standard way to build any new module or multi-file change: thin vertical slices (or contract-first / risk-first), each tested, working, and reviewed and approved by you before the next starts. New modules start from a skeleton copied from the closest existing module and end with their `CLAUDE.md`. Stays in scope, unfinished features behind a flag, safe defaults. |
| `/workflow:challenge <doc or decision>` | Fresh agents, without your reasoning, try to prove it wrong. A document gets five parallel reviewers: simplicity (not needed yet, could reuse existing code), comprehension (undefined terms, gaps for a new reader), design risk (scale, cost, failure, security), codebase fit (every claim about existing code checked), implementation readiness (no decisions left to the implementer). A single claim gets one adversarial reviewer. Valid findings get fixed; one round. |
| `/workflow:drift [paths]` | Checks `CLAUDE.md` files, solution docs, and READMEs against the current code and reports only differences (missing, different, undocumented, broken commands) to `docs/drift/`. You decide per difference whether the doc or the code is wrong. |
| `/workflow:quality-bar [check]` | Creates `docs/quality-bar.md`: measurable limits (types, lint, tests, changed-line coverage, secrets, vulnerable dependencies, performance, accessibility) using the project's own tools, today's numbers as must-not-get-worse baselines, and exceptions with owner and expiry. `check` runs it against current changes. |
| `/workflow:review [PR \| files]` | Code review of the current branch (default), a PR, or files, as three parallel reviewers, each an isolated read-only plugin agent (`plugins/workflow/agents/`) that starts with no chat context and gets only the diff and source file paths: correctness and safety, project standards (plus a code smell list), and match with the spec (solution doc, test sheet). Every finding verified with a concrete scenario; Critical / Major / Minor / Question per axis, then a verdict. Read-only; posts to a PR only if you agree. |
| `/workflow:pr [--draft]` | Pre-flight checks (tests, test sheet, review), push, and a PR with a visual summary, before/after evidence, test and review results, and merge danger (one-way or two-way door, blast radius). Never rebases. |
| Tester agent (`plugins/workflow/agents/tester.md`) | Independent tester with no chat context that cannot edit files. Writes test cases from the PRD alone (never sees the solution doc) and runs them (automated tests it has read, API calls, Playwright, read-only DB queries), recording Passed / Failed / Human review needed with evidence. The builder fixes; only the tester marks results. |
| Checklists (`plugins/workflow/references/`) | Security, performance, accessibility, observability, safe migrations (expand, migrate, contract), and definition of done. Used by the solution doc, review, build, and test stages. |
| Guard hook | Blocks force push, direct push to protected branches (default `main`/`master`/`develop`; per project via `WORKFLOW_PROTECTED_BRANCHES` in `.claude/settings.json`, globs allowed), `rm -r` on `/` or `~`, and edits to `.env*` files. |

Machine-level plugins installed by `/workflow:setup` (user scope, active in every project):

| Plugin | What it does |
|--------|--------------|
| [ponytail](https://github.com/DietrichGebert/ponytail) | Keeps solutions minimal (YAGNI, stdlib first). |
| [playwright](https://github.com/microsoft/playwright-mcp) | Playwright MCP server. Lets Claude drive a browser: open pages, click, fill forms, screenshot. |
| [claude-md-management](https://github.com/anthropics/claude-plugins-official) | Audits and updates CLAUDE.md files with learnings from sessions. |
| [security-guidance](https://github.com/anthropics/claude-plugins-official) | Warns about insecure code patterns while editing. |
| [superpowers](https://github.com/obra/superpowers) | Brainstorming, planning, TDD, debugging, and code-review workflows. |
| [figma](https://github.com/anthropics/claude-plugins-official) | Only for projects with a UI. Reads Figma designs (screens, components, tokens) for the solution doc, building, and testing. Each developer logs in to Figma once. |
| [modern-web-guidance](https://github.com/GoogleChrome/modern-web-guidance) | Only for projects with a web UI. Current HTML, CSS, and JavaScript practice from the Chrome, Edge, Firefox, and MDN teams: accessibility, performance, forms, security, lightweight fallbacks. Project `CLAUDE.md` rules (such as browser support) win. |

## Usage tracking

`/workflow:setup` turns on Claude Code's built-in OpenTelemetry export on each developer's machine, so a central dashboard shows Claude usage per developer, team, and repository.

**Turn it on (once, for the company):**

1. Run a metrics backend that accepts OTLP over HTTP: Prometheus with its OTLP receiver (`--web.enable-otlp-receiver`, endpoint `http://<host>:9090/api/v1/otlp`), Mimir, VictoriaMetrics, or an OpenTelemetry collector in front of any backend. Make sure developer laptops can reach it (office network or VPN).
2. Share its URL with developers privately (team lead, DevOps, password manager). **The URL never goes in this repository**, which is public. At the end of `/workflow:setup`, Claude asks each developer explicitly for three values, showing the current ones on a re-run: the metrics URL, their team, and their name. Team and name can be skipped one by one, or everything with "skip". Claude checks that the URL answers and saves the values to the developer's own `~/.claude/settings.json`.
3. Company-wide settings live in `plugins/workflow/skills/setup/telemetry.json`:
   ```json
   { "protocol": "http/protobuf", "temporality": "cumulative", "service_name": "claude-monitoring", "export_events": false }
   ```
   - `temporality`: `cumulative` for Prometheus, Grafana, and Mimir; `delta` for backends that prefer it (e.g. Datadog).
   - `service_name`: optional; shows as the `job` label.
   - `export_events: true` also sends per-request events (API calls, tool decisions). Prompts and code stay redacted.
   - Setup never sets `OTEL_METRICS_INCLUDE_SESSION_ID=false`: without the session label, parallel sessions merge into one series and the counts go wrong.

**On the dashboard** (Prometheus names): `claude_code_cost_usage_USD_total` and `claude_code_token_usage_tokens_total` (by model, skill, plugin), `claude_code_session_count_total`, `claude_code_active_time_seconds_total`, `claude_code_lines_of_code_count_total`, `claude_code_commit_count_total`, `claude_code_pull_request_count_total`. Labels include `developer_name`, `user_email`, `team_id`, `session_id`, and `vcs_repository_name`. Sum across sessions in queries, e.g. `sum by (user_email, model) (increase(claude_code_cost_usage_USD_total[1d]))`. `/workflow:dev` and `/workflow:review` usage shows up under `skill_name`.

**Not sent:** prompts, responses, code, file contents, commands.

Developers can switch these settings off on their own machine. To enforce them, an admin can put the same `env` values in Claude Code managed settings instead.

## Change the workflow

1. Edit files under `plugins/workflow/`. The plugin list lives in `skills/setup/SKILL.md`; the CLAUDE.md starting point in `skills/setup/CLAUDE.md.template`.
2. Bump `version` in `plugins/workflow/.claude-plugin/plugin.json`.
3. Run `python3 plugins/workflow/hooks/test_guard.py` after guard changes, and `python3 plugins/workflow/skills/dev/test_testsheet.py` after test sheet changes.
4. Merge to the default branch. Developers get the update via `/plugin marketplace update dev-workflow`.

Test locally before merging: `claude --plugin-dir ./plugins/workflow`.
