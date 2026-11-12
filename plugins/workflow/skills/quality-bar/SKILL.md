---
name: quality-bar
description: Set or check a project's quality bar - measurable limits for types, lint, tests and coverage, secrets, dependency vulnerabilities, performance, and accessibility, with today's numbers recorded so they can only improve. Use when setting up a project, when asked about quality standards or gates, or to check a change against the bar.
argument-hint: [check]
---

# Quality bar

Mode: $ARGUMENTS (`check` to check the current changes against an existing bar; otherwise create or update it)

The bar lives in `docs/quality-bar.md`, committed. `/workflow:build`, `/workflow:review`, `/workflow:pr`, and the Test stage of `/workflow:dev` enforce it.

## Create or update

### 1. Detect before asking
Find out from the repo, not the developer:
- Stack and package manager; type checker; linter and formatter configs.
- Test runner and whether coverage is configured; run the suite once with coverage if it is cheap.
- CI config and what it already runs; pre-commit hooks.
- Existing security tooling (Semgrep, gitleaks, Dependabot, `npm audit` in CI).
- Whether there is a UI (performance and accessibility checks apply) and its local URL.

### 2. Propose limits, with defaults
Ask only about dimensions where you cannot pick a sensible default. Each question comes with a recommended answer the developer can accept with "yes". Defaults:

| Dimension | Default limit |
|-----------|---------------|
| Types | Zero type errors |
| Lint | Zero errors with the project's config |
| Tests | All pass |
| Coverage | Changed lines at least 80% covered; overall coverage must not fall |
| Secrets | No secrets in the repo (`gitleaks`, or the staged-diff check in `security.md` in this plugin's `references/` folder, two folders up from this skill) |
| Dependencies | No new high or critical vulnerabilities (`npm audit` / `pip-audit` / `osv-scanner`) |
| Security (code) | No high or critical findings, if a scanner is set up |
| Performance (UI) | LCP 2.5 s or less, CLS 0.1 or less on key pages |
| Performance (API) | p95 under 200 ms for normal endpoints |
| Accessibility (UI) | Zero critical or serious axe findings on changed pages |

Use the tools the project already has. Suggest installing a missing tool only with its install command, and only install it if the developer agrees.

### 3. Record today's numbers
For anything measurable that the project does not meet yet (coverage at 62%, 140 lint warnings, bundle at 310 KB), do not fail everything at once. Record today's value as the baseline, with the rule **must not get worse**.

### 4. Write `docs/quality-bar.md`

```markdown
# Quality bar

## Enforced
| Dimension | Rule | Command | When |
|-----------|------|---------|------|
| Types | Zero errors | `npx tsc --noEmit` | every change |

## Must not get worse
| Metric | Baseline (YYYY-MM-DD) | Command |
|--------|-----------------------|---------|
| Overall coverage | 62.4% | `npm test -- --coverage` |

## Exceptions
| ID | Rule | Where | Reason | Owner | Expires |
|----|------|-------|--------|-------|---------|
| E1 | no-explicit-any | `src/legacy/**` | Rewrite in ABC-441 | name | YYYY-MM-DD |
```

Every exception has an owner and an expiry date. Add a pointer in `CLAUDE.md`'s **Workflow** section: `Quality bar: docs/quality-bar.md`.

## Check

1. Read `docs/quality-bar.md`. If there is none, say so and offer to create one.
2. Run each **Enforced** command that applies to the changed files, and each **Must not get worse** command. Compare with the baselines.
3. Report per dimension: pass, fail (with the output that shows why), or not applicable. Flag expired exceptions.
4. If a baseline improved, offer to raise it to the new value. Never lower a limit or a baseline without the developer's explicit agreement, and record who agreed and why under **Exceptions**.
