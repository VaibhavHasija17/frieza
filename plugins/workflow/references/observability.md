# Observability checklist

For any change that runs in production. Start from the questions on-call will ask.

## Questions first
- Write down 2-4 questions someone on call will ask about this feature ("are payments failing?", "why is this order stuck?").
- Each signal below answers one of them. Metrics show *that* something is wrong, traces show *where*, logs show *why*.

## Logs
- Structured (JSON) with stable event names, following the project's existing logger.
- Every line carries the request or correlation ID, passed on to outgoing calls and queue messages.
- Levels used consistently: `error` someone may need to act, `warn` degraded but handled, `info` business events, `debug` off in production.
- Never log secrets, tokens, passwords, full card numbers, or personal data. Log chosen fields, not whole request or response bodies.
- External calls log endpoint, status, duration, and attempt number.

## Metrics
- For each new endpoint and external dependency: request rate, error rate, duration.
- For each queue or pool: depth or usage, and processing time.
- Durations as histograms (p50, p95, p99), not averages.
- Labels only from small fixed sets (route template, status class); never user IDs, emails, raw URLs, or error text.

## Traces
- New services and outgoing calls keep the trace context the project already uses.
- Custom spans only around meaningful units of work, with no personal data as attributes.

## Alerts
- Alert on symptoms users feel (error rate, p99 latency, queue age), not causes (CPU, restarts).
- Every alert is actionable and links to a short runbook: what it means, the first query to run, who to escalate to.

## Verify
- Trigger an error locally or in staging and find it in the logs by its correlation ID.
- Send test traffic and see the new metrics with the expected labels.
