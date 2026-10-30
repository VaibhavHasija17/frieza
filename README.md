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

Requirements: Node.js 20+, `python3`, `git`, `gh`. Private repo: each developer needs git access to it.

## What you get

| Piece | What it does |
|-------|--------------|
| `/workflow:setup` | Inspects machine and project, shows an adapted plan, then installs the machine-level plugins below, configures `.claude/settings.json` (plugin, protected branches, allowed lint/test commands), creates or updates `CLAUDE.md` from the repo, and writes a brief `CLAUDE.md` in each module folder (purpose, key files, connections, notes). Safe to re-run. |
| `/workflow:solution-doc <prd>` | Reads a PRD, analyses the codebase, writes a technical solution doc (APIs, DB, code changes) to `docs/solutions/`. Format: `plugins/workflow/skills/solution-doc/template.md`. |
| `/workflow:start <ticket> <desc>` | Checks working tree, suggests a `type/TICKET-slug` branch name (never creates it), plans before editing. |
| `/workflow:commit` | Runs checks, stages explicitly, writes a Conventional Commit with `Refs: TICKET`. |
| `/workflow:pr` | Warns if behind the default branch (never rebases), runs checks, self-reviews the diff, pushes, opens a PR with the standard body. |
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

## Change the workflow

1. Edit files under `plugins/workflow/`. The plugin list lives in `skills/setup/SKILL.md`; the CLAUDE.md starting point in `skills/setup/CLAUDE.md.template`.
2. Bump `version` in `plugins/workflow/.claude-plugin/plugin.json`.
3. Run `python3 plugins/workflow/hooks/test_guard.py` after guard changes.
4. Merge to the default branch. Developers get the update via `/plugin marketplace update dev-workflow`.

Test locally before merging: `claude --plugin-dir ./plugins/workflow`.
