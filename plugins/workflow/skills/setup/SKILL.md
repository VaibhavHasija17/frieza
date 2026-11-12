---
name: setup
description: Set up the company dev workflow on this machine and in the current project, adapting to the OS, stack, and existing conventions. Use when onboarding a new machine or project, or when asked to set up, install, or refresh the dev workflow.
disable-model-invocation: true
---

# Set up the dev workflow

Projects and machines differ. Inspect first, adapt to what you find, show a plan, and change nothing until the developer confirms. Safe to re-run: skip what is already in place, and update what has drifted.

## Same result on every machine

Generated project files (`CLAUDE.md`, module `CLAUDE.md`, `.claude/settings.json`) are written once and committed. After that, git is the source of truth, not this skill. Other machines reuse the committed files instead of generating their own.

- **Check the remote first.** Run `git fetch origin`. If the current branch is behind its upstream, or `origin/<default>` has `CLAUDE.md` files this branch lacks, tell the developer another machine may already have generated them and suggest pulling first. Do not pull yourself.
- **Never regenerate a committed file.** If it exists, only edit it, and only where the code it describes has changed (see the stamp rule below).
- **Stamp generated files.** End each generated `CLAUDE.md` with `<!-- workflow:setup <short commit sha of HEAD> -->`. On a re-run, check `git diff --quiet <sha> HEAD -- <folder> ':!<folder>/CLAUDE.md'`:
  - No changes: skip the file.
  - Changes: run the `workflow:drift` skill on that file to find the lines those changes made wrong, edit only those, then update the stamp. Do not reword lines that are still accurate.
  - Sha not found (shallow clone or rewritten history): review the file but make minimal edits only.
- **Repo facts only.** Committed files contain only what comes from the repo itself, so every machine sees the same input. Never write absolute paths, usernames, OS-specific commands, locally installed tool versions, or ports from local `.env` files. Machine-specific notes go in `CLAUDE.local.md`, which must be in `.gitignore`.
- **Fixed shape.** Follow the templates exactly: same sections, same order. Detect modules with the rule in step 2 and process them sorted by path. Sort lists of files alphabetically. Sort new `permissions.allow` entries alphabetically; do not reformat existing entries.

## 1. Inspect the machine

- OS and shell (`uname -s`, or Windows).
- Tools: `node --version` (needs 20+), `python3` (or `python` on Windows; the guard hook needs it), `openpyxl` (`python3 -c "import openpyxl"`) or `uv` (the test case sheet needs one of them), `git`, `gh` and whether `gh auth status` passes.
- `claude plugin list` and `claude plugin marketplace list`.
- `claude --version` (usage tracking needs 2.1.269+ for repository tagging) and the `env` block of `~/.claude/settings.json` (existing telemetry settings and team).

Required user-level plugins (active in every project on the machine):

| Plugin | Marketplace to add if missing |
|--------|-------------------------------|
| `ponytail@ponytail` | `DietrichGebert/ponytail` |
| `playwright@claude-plugins-official` | built in |
| `claude-md-management@claude-plugins-official` | built in |
| `security-guidance@claude-plugins-official` | built in |
| `superpowers@claude-plugins-official` | built in |

### Usage tracking

Claude usage is sent to the company dashboard through Claude Code's built-in OpenTelemetry export. Company settings are in `telemetry.json` in this skill's directory. If its `endpoint` is empty, skip usage tracking and say so in the report.

Claude Code ignores telemetry variables in a project's `.claude/settings.json`, so they go in the **user** settings, `~/.claude/settings.json`, under `env`:

| Variable | Value |
|----------|-------|
| `CLAUDE_CODE_ENABLE_TELEMETRY` | `1` |
| `OTEL_METRICS_EXPORTER` | `otlp` |
| `OTEL_LOGS_EXPORTER` | `otlp` if `export_events` is true; otherwise leave unset |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | `protocol` from `telemetry.json` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `endpoint` from `telemetry.json` |
| `OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE` | `temporality` from `telemetry.json` (`cumulative` for Prometheus and Grafana) |
| `OTEL_METRICS_INCLUDE_REPOSITORY` | `true` (tags every metric with the git repo) |
| `OTEL_RESOURCE_ATTRIBUTES` | `team.id=<team>`: ask the developer for their team once; lowercase, no spaces |
| `OTEL_SERVICE_NAME` | `service_name` from `telemetry.json`, if set |
| `OTEL_EXPORTER_OTLP_HEADERS` | Only if `needs_token` is true: `Authorization=<auth_scheme> <token>`, with the token the developer gives you (see below). |

Never set `OTEL_LOG_USER_PROMPTS`, `OTEL_LOG_ASSISTANT_RESPONSES`, `OTEL_LOG_TOOL_DETAILS`, `OTEL_LOG_TOOL_CONTENT`, or `OTEL_LOG_RAW_API_BODIES`: prompts, code, and commands stay private.

If managed settings already set these variables, leave them alone.

**The access token.** If `needs_token` is true, check whether `OTEL_EXPORTER_OTLP_HEADERS` is already set (test only that the key exists, see below). If it is, ask whether to keep it or replace it. If it is not, ask the developer:

> Usage tracking needs an access token. Get it from your team lead or the team password manager and paste it here, and I will save it to your `~/.claude/settings.json`. Or reply "skip" to add it later yourself.

When they paste it:
- Save it straight away with a command that writes it into the `env` block and prints nothing back:
  ```sh
  python3 - <<'EOF'
  import json, os
  path = os.path.expanduser("~/.claude/settings.json")
  data = json.load(open(path)) if os.path.exists(path) else {}
  data.setdefault("env", {})["OTEL_EXPORTER_OTLP_HEADERS"] = "Authorization=<auth_scheme> <token>"
  json.dump(data, open(path, "w"), indent=2)
  EOF
  ```
- Then reply only "Token saved". Never repeat the token, show it, summarise it, or include it in any report.
- Never write it anywhere else: not `telemetry.json`, not project files, not `CLAUDE.md`, not shell profiles, not a commit.
- If the developer replies "skip", tell them the line to add later themselves: `"OTEL_EXPORTER_OTLP_HEADERS": "Authorization=<auth_scheme> <your token>"` in the `env` block of `~/.claude/settings.json`. Everything else works without it; usage is just not sent.

To check it is present without exposing it, only test whether the key exists (for example `python3 -c "import json,os; print('OTEL_EXPORTER_OTLP_HEADERS' in json.load(open(os.path.expanduser('~/.claude/settings.json'))).get('env', {}))"`).

## 2. Inspect the project

Find the root with `git rev-parse --show-toplevel`. If this is not a git repo, ask whether to continue.

Work out each of these from the repo, not from assumptions. Note the evidence (file or command) for each.

- **Stack:** languages, frameworks, package managers, monorepo or workspaces (and the packages in it).
- **Commands:** install, dev server (and its local URL), build, lint, format, typecheck, test, single test, DB migrate. Source: `package.json`, `Makefile`, `composer.json`, `pyproject.toml`, `build.gradle`, `Gemfile`, CI config (`.github/workflows`, `.gitlab-ci.yml`, `bitbucket-pipelines.yml`), `README`.
- **Git conventions:**
  - Default branch: `git symbolic-ref --short refs/remotes/origin/HEAD`.
  - Long-lived branches (e.g. `develop`, `staging`, `release/*`): `git branch -r`.
  - Branch naming in use: recent remote branch names.
  - Commit format in use: `git log --oneline -30`, plus `commitlint`, `husky`, `lefthook`, or `pre-commit` config.
  - PR template: `.github/pull_request_template.md` or similar.
- **Data and APIs:** DB engine, ORM, migration tool and folder, API style (REST, GraphQL, RPC).
- **Docs:** where design docs live, if anywhere.
- **Frontend:** whether there is a UI that Playwright can test, and its dev URL.
- **Modules:** the directories that each own one feature, domain, or package (e.g. `src/modules/*`, `apps/*`, `packages/*`, Django apps, Laravel modules, Go packages). Skip generated code, vendored code, build output, test-only, and config-only folders.
- **Existing AI config:** `CLAUDE.md` (root and nested), `AGENTS.md`, `.cursorrules`, `.cursor/rules`, `.github/copilot-instructions.md`, `.claude/settings.json`, `.claude/settings.local.json`.

## 3. Decide

Company defaults apply unless the project already does something different on purpose. Then the project wins, and the difference is recorded in CLAUDE.md.

| Setting | Company default | Adapt when |
|---------|-----------------|------------|
| Protected branches | `main`, `master`, `develop` | The repo uses other long-lived branches (e.g. `staging`, `release/*`). |
| Branch naming | `type/TICKET-slug` | The history shows a different consistent scheme. |
| Commit format | Conventional Commits + `Refs: TICKET` | commitlint config or a different consistent format in `git log`. |
| PR description | Standard body in `/workflow:dev` | The repo has a PR template. |
| Solution docs | `docs/solutions/` | The repo already keeps design docs elsewhere. |

Also decide:
- **Allowed commands:** the project's verified lint, test, typecheck, and build commands, to add to `permissions.allow` (e.g. `Bash(npm run lint:*)`). Never allow deploy, publish, migrate, or destructive commands.
- **Existing AI config:** if `AGENTS.md` or another tool's rules exist, import them into CLAUDE.md (`@AGENTS.md`) instead of copying their content.

## 4. Show the plan and confirm

Show a short plan:
- Machine: plugins and marketplaces to add; missing tools with the install command for this OS (e.g. `brew install gh`, `sudo apt install gh`, `winget install GitHub.cli`).
- Usage tracking: the settings to add, and plainly what is sent: your email and account ID, team, repository, session count, tokens and cost per model, active time, lines added and removed, commits and PRs created, and which skills and plugins were used. Not sent: prompts, responses, code, file contents, or commands.
- Project: what was detected, each choice from step 3 and why, and the exact files to create or change, including the list of module CLAUDE.md files to create or update.

Wait for the developer to confirm or adjust. Install system tools only if they explicitly agree.

## 5. Apply

**Machine:** add missing marketplaces (`claude plugin marketplace add <repo>`), then install missing plugins (`claude plugin install <plugin> --scope user`). If one fails, report it and continue.

**Usage tracking:** merge the variables from step 1 into the `env` block of `~/.claude/settings.json`. Keep every other key, including an existing `OTEL_EXPORTER_OTLP_HEADERS`; replace only the variables you set.

**`.claude/settings.json`** (shared, committed): merge, keep every existing key, do not duplicate entries.
```json
{
  "extraKnownMarketplaces": {
    "dev-workflow": { "source": { "source": "github", "repo": "<GitHub source of the dev-workflow entry in claude plugin marketplace list>" } }
  },
  "enabledPlugins": { "workflow@dev-workflow": true },
  "env": { "WORKFLOW_PROTECTED_BRANCHES": "<comma-separated, only if different from the default>" },
  "permissions": { "allow": ["<verified commands from step 3>"] }
}
```

**Quality bar:** if the project has no `docs/quality-bar.md`, offer to create one with the `workflow:quality-bar` skill. Skip if the developer declines.

**CLAUDE.md:**
- **Missing:** create it from `CLAUDE.md.template` in this skill's directory. Fill every section from what you found. Write `<TODO>` where you could not tell; do not guess.
- **Exists:** keep its content. Add or update only the **Workflow** section, and add missing commands you verified. Follow the stamp rule above. Show what you changed.

**Module CLAUDE.md files:** one brief `CLAUDE.md` in each module found in step 2. Claude Code loads it automatically when working in that folder, and it doubles as a quick orientation for people.
- Use `MODULE.md.template` in this skill's directory. Keep each file under about 30 lines.
- Read the module's code first. Write only what is true and specific to that module; do not repeat the root CLAUDE.md.
- **Missing:** create it.
- **Exists:** follow the stamp rule above. Keep human-written content. Fix references to files that no longer exist and add anything important that is missing.
- For many modules, use parallel subagents (one per group of modules) and keep only their results.
- In a monorepo, a package's CLAUDE.md also lists its own commands where they differ from the root.

## 6. Report

- Machine: installed now, already present, failed; tools still missing; usage tracking on (endpoint, team) or skipped.
- Project: files created, changed, or skipped as up to date, and each adaptation made with its reason.
- Next steps:
  1. If usage tracking needs a token and the developer skipped it: add it later, as described above.
  2. Restart Claude Code so new plugins and settings load. Usage data then appears on the dashboard within a few minutes (metric `claude_code.session.count`).
  3. Review, then commit `.claude/settings.json`, `CLAUDE.md`, and the module `CLAUDE.md` files.
