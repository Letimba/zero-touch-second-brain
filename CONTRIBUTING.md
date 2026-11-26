# Contributing

## Ground rules

1. Never commit runtime data: `automation/{logs,state,queue}/`, `.env*`, keys.
2. Never commit a real vault. Use `examples/vault/` with synthetic content.
3. One package, one owner, one write scope. See `AGENT-ROUTING.md`.
4. Every change needs a command and its real output in the PR description.

## Workflow

1. Open an issue with the problem and the smallest reproduction.
2. Add or update a test in `tests/`.
3. Implement the smallest change that makes the test pass.
4. Run `bash scripts/verify.sh` and `python3 -m unittest discover -s tests`.
5. Update `CHANGELOG.md`.

## Review

Code changes need an independent reviewer (`qa-security` or the language
specific reviewer). A green test run alone is not an approval.
