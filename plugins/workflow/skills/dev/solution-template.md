# <Feature name> - Technical Solution

**PRD:** <link or path> · **Ticket:** <TICKET-ID or none> · **Author:** <name> · **Date:** <YYYY-MM-DD> · **Status:** Draft

## 1. Overview

<2-4 sentences. What we are building, how it will work, and which parts of the system change.>

## 2. Requirements

What the PRD asks for, and how this solution covers it.

- **R1** <requirement in one line> - <how it is covered, or "Not covered: reason">
- **R2** ...

**Not included:** <anything the PRD mentions that this solution leaves out, and why. "None" if nothing.>

## 3. How it works today

<2-4 sentences on the current code in this area.>

We will follow the pattern of **<closest existing feature>**:
`<route file>` → `<service file>` → `<model/repository file>` → `<test file>`

Reusing: `<existing helper or service>` for <purpose>, ...

## 4. API changes

<"None" if there are no API changes. Otherwise one block per endpoint.>

### New: `POST /api/v1/<resource>`

<One line: what it does. Who can call it.>

Request:
```json
{ "name": "string, required", "quantity": "number, optional, default 1" }
```

Response `201`:
```json
{ "id": "string", "name": "string", "createdAt": "ISO date" }
```

Errors: `400` invalid input · `403` not allowed · `409` <conflict case>

### Changed: `GET /api/v1/<resource>`

<What changes and whether existing clients are affected.>

## 5. Database changes

<"None" if there are no database changes. Otherwise one block per table.>

### New table: `<table>`

<One line: what it stores.>

| Column | Type | Notes |
|--------|------|-------|
| `id` | uuid | primary key |
| `<column>` | `<type>` | required; references `<table.column>`; indexed |

### Changed table: `<table>`

- Add `<column>` (`<type>`, <nullable/default>) - <why>

**Migration:** `<migration file path>`. <Backfill needed? Can it be rolled back? Any risk on large tables?>

## 6. Code changes

| File | Change | Why |
|------|--------|-----|
| `<path>` | Modify: <what changes> | R1 |
| `<path>` | New: <what it contains, follows `<similar file>`> | R2 |

**Suggested build order:** 1. <migration> 2. <backend> 3. <frontend>

## 7. Testing

Test cases: `<path to the -test-cases.xlsx sheet>` (<n> cases).

- <Test approach: which levels (unit / integration / e2e / manual), where automated tests go, test data needed>

## 8. Rollout and risks

- **Config / feature flags:** <new env vars or flags, or "None">
- **Deploy order and rollback:** <short plan>
- **Risks:** <security, performance, data, compatibility concerns and how they are handled>

## 9. Open questions

- <Question> - for <PM / Design / Backend / DevOps>

**Assumptions:** <what was assumed where the PRD or code was unclear, or "None">
