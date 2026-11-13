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

<"None" if there are no API changes. Otherwise one block per endpoint, new or changed. Every block has full request and response bodies, and the developer confirms each one.>

### New: `POST /api/v1/<resource>`

<One line: what it does.> **Auth:** <who can call it> · **Confirmed by developer:** <yes / not yet>

Path / query params: `<name>` (<type>, required/optional, <rule>) · or "None"

Request body:
```json
{
  "name": "Blue mug",          // string, required, 1-120 chars
  "quantity": 2,               // integer, optional, default 1, min 1
  "tags": ["kitchen"]          // string[], optional
}
```

Response `201`:
```json
{
  "id": "ord_8f2k",            // string
  "name": "Blue mug",
  "quantity": 2,
  "createdAt": "2026-11-13T10:00:00Z"
}
```

Errors (same body shape as the project's existing errors):

| Status | When | Body |
|--------|------|------|
| `400` | invalid input | `{ "error": "VALIDATION_FAILED", "fields": { "name": "required" } }` |
| `403` | caller not allowed | `{ "error": "FORBIDDEN" }` |
| `409` | <conflict case> | `{ "error": "<CODE>" }` |

### Changed: `GET /api/v1/<resource>`

<What changes and whether existing clients are affected.> **Confirmed by developer:** <yes / not yet>

Request: <unchanged, or full new body/params as above>

Response `200`, before → after:
```diff
 {
   "id": "ord_8f2k",
-  "total": 40
+  "total": { "amount": 40, "currency": "INR" }
 }
```

### Screen → data map

<Only when designs were used. "None: no design available; APIs designed from the PRD" otherwise.>
Design source: <Figma links / screenshot paths>

| Screen | Element | Data / action | Served by |
|--------|---------|---------------|-----------|
| Orders list | table columns: id, customer, total, status | list of orders | `GET /api/v1/orders` (existing) |
| Orders list | status filter, search box, pages | `status`, `q`, `page` query params | `GET /api/v1/orders` (changed) |
| New order form | name (required, max 120), quantity | create order | `POST /api/v1/orders` (new) |

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

**Migration:** `<migration file path>`. <Expand / migrate / contract steps if anything in use changes. Backfill needed? Rollback? Locks on large tables?>

## 6. Code changes

| File | Change | Why |
|------|--------|-----|
| `<path>` | Modify: <what changes> | R1 |
| `<path>` | New: <what it contains, follows `<similar file>`> | R2 |

**UI** (only with designs): <screen> → reuses `<existing component>`; new `<component>` follows `<similar component>`; tokens from `<tokens file>`; states: loading, empty, error.

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
