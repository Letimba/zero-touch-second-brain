# Security policy

## What this project never does

- stores tokens, passwords or API keys in the vault or the repository
- sends vault content to an external service
- deletes or moves raw source files
- starts other agents without the supervisor's explicit dispatch

## What it does

- reads the local OpenCode service config at runtime to authenticate the API
- redacts token-shaped strings (`0t…`, `sk-…`, `ghp_…`, `AKIA…`) in exports
- skips clips below 20 characters and deduplicates by SHA-256
- reports secret-shaped strings in the health check

## Known limitation

Redaction is pattern-based. It does **not** remove names, project codenames,
local paths or private conversations from session digests. Generated `queue/`,
`logs/` and `state/` files are runtime data, are gitignored, and must never be
committed or pasted into an issue.

## Reporting

Open a private security advisory. Do not attach real digests, logs or vault
files. Include only the affected path and a description of the issue.
