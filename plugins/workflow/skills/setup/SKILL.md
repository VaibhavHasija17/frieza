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
  - Changes: edit only the lines those changes made wrong, then update the stamp. Do not reword lines that are still accurate.
  - Sha not found (shallow clone or rewritten history): review the file but make minimal edits only.
- **Repo facts only.** Committed files contain only what comes from the repo itself, so every machine sees the same input. Never write absolute paths, usernames, OS-specific commands, locally installed tool versions, or ports from local `.env` files. Machine-specific notes go in `CLAUDE.local.md`, which must be in `.gitignore`.
- **Fixed shape.** Follow the templates exactly: same sections, same order. Detect modules with the rule in step 2 and process them sorted by path. Sort lists of files alphabetically. Sort new `permissions.allow` entries alphabetically; do not reformat existing entries.

## 1. Inspect the machine

- OS and shell (`uname -s`, or Windows).
- Tools: `node --version` (needs 20+), `python3` (or `python` on Windows; the guard hook needs it), `git`, `gh` and whether `gh auth status` passes.
- `claude plugin list` and `claude plugin marketplace list`.

Required user-level plugins (active in every project on the machine):

| Plugin | Marketplace to add if missing |
|--------|-------------------------------|
| `ponytail@ponytail` | `DietrichGebert/ponytail` |
| `claude-mem@thedotmack` | `thedotmack/claude-mem` |
| `playwright@claude-plugins-official` | built in |
| `claude-md-management@claude-plugins-official` | built in |
| `security-guidance@claude-plugins-official` | built in |
| `superpowers@claude-plugins-official` | built in |

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
| PR description | Standard body in `/workflow:pr` | The repo has a PR template. |
| Solution docs | `docs/solutions/` | The repo already keeps design docs elsewhere. |

Also decide:
- **Allowed commands:** the project's verified lint, test, typecheck, and build commands, to add to `permissions.allow` (e.g. `Bash(npm run lint:*)`). Never allow deploy, publish, migrate, or destructive commands.
- **Existing AI config:** if `AGENTS.md` or another tool's rules exist, import them into CLAUDE.md (`@AGENTS.md`) instead of copying their content.

## 4. Show the plan and confirm

Show a short plan:
- Machine: plugins and marketplaces to add; missing tools with the install command for this OS (e.g. `brew install gh`, `sudo apt install gh`, `winget install GitHub.cli`).
- Project: what was detected, each choice from step 3 and why, and the exact files to create or change, including the list of module CLAUDE.md files to create or update.

Wait for the developer to confirm or adjust. Install system tools only if they explicitly agree.

## 5. Apply

**Machine:** add missing marketplaces (`claude plugin marketplace add <repo>`), then install missing plugins (`claude plugin install <plugin> --scope user`). If one fails, report it and continue.

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

- Machine: installed now, already present, failed; tools still missing.
- Project: files created, changed, or skipped as up to date, and each adaptation made with its reason.
- Next steps:
  1. Restart Claude Code so new plugins and settings load.
  2. Review, then commit `.claude/settings.json`, `CLAUDE.md`, and the module `CLAUDE.md` files.
  3. claude-mem asks you to sign in and choose a memory provider. Follow the company policy on which provider is allowed for company code.
