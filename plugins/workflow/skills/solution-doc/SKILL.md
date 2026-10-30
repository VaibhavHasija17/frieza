---
name: solution-doc
description: Turn a PRD into a technical solution document - analyse the codebase, follow its existing patterns, and list API, database, and code changes in the company format. Use when a developer provides a PRD, feature spec, or requirements and wants a technical design before implementation.
argument-hint: <path to PRD file, or paste the PRD>
---

# Technical solution document

PRD: $ARGUMENTS

Output is a document only. Do not modify source code, run migrations, or create branches.

## 1. Read the PRD

- Load the PRD from the given path, link, or pasted text. If none is given, ask for it and stop.
- List every requirement and give each an ID (`R1`, `R2`, ...). Include acceptance criteria and non-functional asks (performance, security, roles).
- Anything ambiguous or missing goes to **Open questions**. Do not invent product behaviour.

## 2. Analyse the codebase

Read `CLAUDE.md` first. Then establish, with file paths as evidence:

- **Stack and layout:** languages, frameworks, how the code is layered (e.g. route, controller, service, repository, model).
- **Closest existing feature:** find the feature most like this one and trace it end to end, from entry point through to storage and tests. This is the pattern the solution follows.
- **API conventions:** URL naming, versioning, auth middleware, request validation, response and error format, pagination.
- **Database conventions:** DB engine, ORM or query layer, migration tool and file location, naming (tables, columns, indexes), soft deletes, timestamps, audit fields.
- **Reusable pieces:** helpers, services, components, and types that the solution should reuse instead of re-creating.
- **Test conventions:** framework, location, fixtures, what kinds of tests exist.

For a broad sweep across many files, use an Explore subagent and keep only its conclusions. Before proposing anything new, confirm it does not exist already: search for existing endpoints, tables, and columns.

## 3. Write the document

Use the format in `template.md` in this skill's directory. Keep every section heading and its order. If a section does not apply, write "None".

**Writing style** - the reader is a developer, reviewer, or tech lead who should understand the plan in about 5 minutes:
- Plain, simple English. Short sentences. One idea per bullet.
- Say each thing once. Do not repeat details across sections.
- Explain *why* only where it is not obvious, in one line.
- No filler, no marketing words, no restating the PRD at length.
- Use exact technical names (endpoints, tables, columns, files) but explain any project-specific term on first use.

**Content rules:**
- Include every API, database, and code change. Less wording, not less detail.
- Each change names the existing file or pattern it follows (`path/to/file.ts:42`).
- Statements about the current code must come from code you read. List anything inferred under **Assumptions**.
- Show contracts, not implementations: request/response examples, columns, signatures. No full code.
- Every requirement ID appears in section 2 and in at least one test.
- Prefer extending existing code over adding new modules. Say why when something new is needed.

## 4. Save and report

- Save to `<solution docs folder>/YYYY-MM-DD-<feature-slug>.md`. The folder comes from the **Workflow** section of CLAUDE.md; default `docs/solutions/`.
- Reply with the file path, a 3-line summary of the approach, and the open questions that block implementation.
