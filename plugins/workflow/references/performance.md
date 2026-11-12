# Performance checklist

Measure before and after any performance change. A change that does not move the measurement gets reverted.

## Database
- No N+1 queries: load related data with joins or eager loading.
- New queries have an index that matches their filter and sort. Composite index order: equality columns first, then range or sort.
- List endpoints are paginated; no unbounded `SELECT *`.
- For a slow query, capture `EXPLAIN ANALYZE` before the fix and after it.
- Indexes on write-heavy tables are justified: each one slows every insert and update.
- One connection pool per process; `instances x pool size` stays below the database's connection limit; pool waits time out.

## API and backend
- p95 response time under 200 ms for normal endpoints, unless the quality bar says otherwise.
- Slow work (emails, reports, third-party calls) runs in a background job, not in the request.
- External calls have timeouts and limited retries with backoff.
- Caching has a clear owner and invalidation rule; cache keys include everything that changes the result (user, tenant, locale).

## Frontend
- Core Web Vitals: LCP 2.5 s or less, INP 200 ms or less, CLS 0.1 or less.
- Initial JavaScript under about 200 KB gzipped; routes and heavy features are code-split.
- Images in modern formats (WebP, AVIF), sized with `srcset`, with width and height set; below-the-fold images lazy-loaded; the main hero image not lazy-loaded.
- Long lists are virtualized. Animations use `transform` and `opacity`.
- Third-party scripts load `async` or `defer`.
- Fonts: WOFF2, few weights, `font-display: swap`.

## Common mistakes
- Optimising without a measurement.
- Averages instead of p95 or p99.
- Caching to hide a missing index.
- Fetching whole records or lists to use one field.
