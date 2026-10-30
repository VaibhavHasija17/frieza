---
name: pr
description: Open a pull request following company conventions - checks, self-review, push, and a filled-in PR description. Use when work on a branch is ready for review.
argument-hint: [--draft]
---

# Open a pull request

Args: $ARGUMENTS

The **Workflow** section of CLAUDE.md overrides the defaults below (protected branches, PR template, title format).

1. Confirm the current branch is not protected (default: `main`, `master`, `develop`). Confirm the tree is clean; if not, run the commit workflow first.
2. Find the default branch (`git symbolic-ref --short refs/remotes/origin/HEAD`). Run `git fetch origin` and `git rev-list --count HEAD..origin/<default>`. If the branch is behind, tell the developer how many commits behind it is. Do not rebase or merge.
3. Run the project's lint and test commands from CLAUDE.md. Do not open the PR if they fail.
4. Self-review `git diff origin/<default>...HEAD`. Look for: bugs, missing tests, leftover debug code or TODOs, secrets, and CLAUDE.md convention violations. Fix real problems before continuing and mention what you fixed.
5. `git push -u origin HEAD`.
6. Create the PR with `gh pr create` (add `--draft` if requested):
   - Title: same format as the main commit, `<type>(<scope>): <summary>`, with the ticket ID if there is one.
   - Body: use `.github/pull_request_template.md` if the repo has one. Otherwise:
     ```
     ## Summary
     <what and why, 1-3 sentences>

     ## Ticket
     <TICKET-ID or link, or "none">

     ## Changes
     - <bullet per notable change>

     ## Testing
     <commands run and what was verified manually>

     ## Notes for reviewers
     <risky areas, follow-ups, screenshots for UI changes>
     ```
7. Print the PR URL.
