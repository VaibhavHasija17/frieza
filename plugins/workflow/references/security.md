# Security checklist

Check what applies to the change. Skip sections that do not.

## Threats first
- Trust boundaries named: incoming requests, uploads, webhooks, third-party APIs, LLM output, queue messages, files other processes write.
- Assets named: credentials, personal data, payment data, admin actions, money movement.
- For each boundary, ask how it could be abused: spoofed identity, tampered data, denied actions, leaked data, overload, privilege gain.

## Secrets
- No secrets in code, config, tests, or logs. `.env`, `*.pem`, `*.key` are in `.gitignore`; `.env.example` holds placeholders only.
- Check staged changes: `git diff --cached -i -G'password|secret|api_key|token' --name-only` (lists file names only, never values).

## Authentication
- Passwords hashed with bcrypt (12+ rounds), scrypt, or argon2. Never stored or logged in plain text.
- Session cookies `httpOnly`, `secure`, `sameSite=lax`; sessions expire.
- Login and password reset are rate-limited; reset tokens are single-use and expire within an hour.

## Authorization
- Every protected endpoint checks the caller is signed in.
- Every record access checks the caller may access *that record* (owner, tenant, or role), not just that they are signed in.
- Admin actions check the admin role on the server. API keys and tokens have the least permissions needed; JWTs are checked for signature, expiry, and issuer.

## Input
- All input validated at the boundary (API route, form handler, message consumer) with an allowlist: types, lengths, ranges, formats.
- SQL is parameterized; no string-built queries. HTML output is escaped by the framework.
- Redirect targets and server-side fetch URLs are allowlisted; private and internal IPs are blocked (SSRF).
- File uploads: type and size limited, content checked, stored outside the web root.
- Delete, move, and overwrite operations on paths resolve symlinks and stay inside an allowed root.

## Data protection
- Sensitive fields (password hashes, tokens, internal IDs that matter) are never returned by APIs.
- Personal data is collected for a stated purpose, kept no longer than needed, and can be deleted (including caches and indexes).
- HTTPS for all external calls. Personal data encrypted at rest where regulation requires.

## Dependencies
- CI installs from the lockfile (`npm ci`, `pnpm install --frozen-lockfile`, `pip install -r` with pinned versions).
- Known-vulnerability audit runs (`npm audit`, `pnpm audit`, `pip-audit`, `osv-scanner`); nothing high or critical is added.
- New dependencies are maintained, widely used, and needed.

## Errors
- Users see generic messages; stack traces, SQL, and internal paths stay in server logs.
- Failures deny by default: an error in an auth or permission check blocks the action.

## LLM features
- Model output is treated as untrusted input: never executed, used in queries, or rendered as HTML without validation.
- Prompts do not contain secrets. Tools the model can call have the least permissions needed.
