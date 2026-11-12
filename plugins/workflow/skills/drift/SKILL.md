---
name: drift
description: Find where documentation and code have diverged - module CLAUDE.md files, the root CLAUDE.md, solution docs, and READMEs checked against the current source - and report only the differences. Use when asked to check docs against code, find stale or outdated docs, after large changes or refactors, or when /workflow:setup is re-run on a project.
argument-hint: [folder or files; defaults to all CLAUDE.md files and the solution docs folder]
---

# Drift report

Scope: $ARGUMENTS

Default scope: every `CLAUDE.md` in the repo (root and modules), the solution docs folder (from the **Workflow** section of `CLAUDE.md`, default `docs/solutions/`), and READMEs that describe code. Skip generated, vendored, and build folders.

Read-only: report differences; change docs or code only when the developer chooses.

## 1. For each document

1. **Read it.** Note every concrete claim: file and folder paths, functions, classes, endpoints, tables and columns, commands, config keys, patterns ("all handlers validate with X"), and connections ("used by the billing module").
2. **Find the code.** Follow the paths it names. Where it does not name them, search for the symbols, endpoints, or tables. If finding them took a search, suggest adding the path to the doc so the next check is cheaper.
3. **Compare.** Read the current code; never rely on memory. Look for:
   - **Missing:** described but not in the code (a feature, endpoint, field, file, command).
   - **Different:** exists but works differently (other fields, other pattern or library, hard-coded values where the doc describes real logic, renamed or moved files).
   - **Undocumented:** important code the document should cover but does not (a new key file in a module, a new endpoint in a module's API, a new command).
   - **Broken commands:** commands in `CLAUDE.md` that no longer exist in `package.json`, `Makefile`, or similar.

For many documents, split them across parallel subagents (one per group of modules) and keep only their reports. Check each reported difference yourself before including it.

Solution docs describe a planned change at a point in time. For them, report only where the implemented code differs from what the doc says was decided, not later unrelated changes.

## 2. Report

Write `docs/drift/YYYY-MM-DD-drift-report.md` (and summarise in chat):

```markdown
## <document path>
- [Missing] <claim> - not found in <where you looked>
- [Different] <claim> - code does <what>, at `path:line`
- [Undocumented] `path` - <what it is>
- [Broken command] `<command>` - <why>
```

List only differences. A document with none gets `No drift.` Do not describe what matches.

## 3. Decide

For each difference, ask the developer which side is right:
- **Doc is stale:** update the document. For a module `CLAUDE.md`, keep human-written content, change only the wrong lines, and refresh its `<!-- workflow:setup <sha> -->` stamp.
- **Code is wrong:** list it as work to do (a ticket or a `/workflow:dev` task). Do not fix code here.
