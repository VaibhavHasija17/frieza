---
name: pr
description: Open a pull request in the company format - pre-flight checks, push, and a description with a visual summary, before/after evidence, test results, review status, and merge danger. Use when work on a branch is ready for review, or when asked to open, create, or write a PR.
argument-hint: [--draft]
---

# Pull request

Args: $ARGUMENTS

The **Workflow** section of `CLAUDE.md` overrides the defaults here (protected branches, PR template, title format). Never rebase, merge, or push to a protected branch (default `main`, `master`, `develop`).

## 1. Pre-flight

1. The branch is not protected and the tree is clean. If not, stop and say what to do (commit first, or create a branch).
2. Find the default branch (`git symbolic-ref --short refs/remotes/origin/HEAD`). Run `git fetch origin` and `git rev-list --count HEAD..origin/<default>`. If behind, say by how many commits. Do not rebase or merge.
3. Run the lint and tests from `CLAUDE.md`. Do not open the PR if they fail.
4. If there is a test sheet for this work (solution docs folder, matching the branch's ticket or slug), read it with `python3 <this skill's directory>/../dev/testsheet.py dump <sheet>` (or `uv run` if `openpyxl` is missing). Do not open the PR with `Not run` or `Retrying` cases, or Failed P0 cases, unless the developer accepts them.
5. If the project has `docs/quality-bar.md`, run the `workflow:quality-bar` skill in `check` mode. Do not open the PR with failures unless the developer accepts them.
6. If the code was not reviewed since its last change, run the `workflow:review` skill. Do not open the PR with open Critical or Major findings unless the developer accepts them.

## 2. Push and create

`git push -u origin HEAD`, then `gh pr create` (add `--draft` if asked). Title: same format as the main commit, with the ticket ID if there is one.

Body: if the repo has a PR template, fill it, and put the Evidence and Merge danger content below into its closest sections (or append them). Otherwise use:

```markdown
## Summary
<1-2 sentences: what and why>

<the smallest visual that makes the change clear - see below>

## Ticket and docs
<TICKET-ID or link> · Solution doc: <path or "none"> · Test cases: <sheet path or "none">

## Evidence
- **Before:** <failing test run, error output, or screenshot>
- **After:** <passing test run, correct output, or screenshot>

Test cases: <n> passed, <n> failed, <n> need human review
<failed cases with accepted reasons; human review cases and what to check>

## Code review
<verdict; what was fixed; Minor findings and Questions left open>

## Merge danger
**Door:** one-way / two-way - <one line why>
**Blast radius:** <who or what breaks if this is wrong>
```

## Writing the sections

- Brief. No preamble. Use the project's terms.
- **Summary visual:** pick the one view that explains the change best, and keep only what matters:
  - a `diff` sketch of a call tree, component tree, or file tree when the shape already exists and the point is what changed;
  - pseudocode for new logic;
  - a Mermaid sequence diagram when the change is about how parts talk to each other.
- **Evidence:** screenshots are best for UI changes (Playwright MCP against the local dev server); test runs or command output otherwise. Show the specific test that failed before and passes now.
- **Merge danger:**
  - *Two-way door:* easy to roll back by reverting the PR.
  - *One-way door:* hard or impossible to undo: data migrations that drop or rewrite data, deleted APIs that clients use, sent emails or notifications, external side effects, changed data formats in storage.
  - *Blast radius:* be concrete: "orders API clients", "checkout page on mobile", "nightly billing job", "none outside the admin screen".

Print the PR URL when done.
