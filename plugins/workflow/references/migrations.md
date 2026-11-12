# Safe migration rules

For any change to a database schema, stored data format, public API, event or message format, or anything other code or clients depend on.

## Expand, migrate, contract
Never change something in use in a single deploy. Split it:

1. **Expand** - add the new alongside the old: new column, table, endpoint, or field. Old code keeps working.
2. **Migrate** - write to both (or read new, fall back to old), backfill existing data in batches, move every caller to the new. Verify nothing uses the old.
3. **Contract** - remove the old in a later deploy, once the new has run in production.

Examples:
- Rename a column: add the new column, write to both, backfill, switch reads, then drop the old column in a later release.
- Make a column `NOT NULL`: add it nullable with a default, backfill, then add the constraint.
- Change an API response field: add the new field, keep the old one until all clients have moved, mark it deprecated, then remove it.

## Rules
- Every migration has a tested rollback, or the solution doc says why it cannot be rolled back (a one-way door).
- Large tables: no long locks. Add indexes concurrently where the database supports it; backfill in batches; avoid table rewrites during busy hours.
- Data backfills are idempotent: safe to run twice and to resume after failure.
- Deploy order is written down: usually migration (expand) first, then code, then a later contract migration.
- Old and new code must both work against the schema during the deploy, because they run side by side for a while.
- Deleting data or columns is a one-way door: take a backup or keep the data until the contract step is confirmed safe.
