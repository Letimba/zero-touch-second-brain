# FAQ

### Do I need Obsidian?
No. It is a Markdown viewer. Any editor works.

### Does this need a cloud account?
No. Everything runs locally. The only optional external service is your existing
OpenCode CLI, whose local API is used for session export.

### Why a scheduler?
Because a learning loop that depends on remembering to run it does not happen.
The scheduler runs one cycle every 15 minutes; a shell hook catches missed runs.

### Can I use it with Claude Code or Codex?
Not natively yet. The agent and command files are plain Markdown, so adapters
are straightforward, but they are not shipped in 0.1.0.

### Why does Termux need a wrapper script?
The portable scripts use `#!/usr/bin/env bash` for Linux/macOS. Android has no
`/usr/bin/env`, so the scheduler must start
`scripts/termux/brain-auto-termux.sh`, which invokes them through `$PREFIX/bin/bash`.

### What if my vault already exists?
`install.sh` never overwrites an existing vault. Point `VAULT` at it and review
the curated agents before the first run.

### How do I know it worked?
`/brain-status` shows last run, steps, health, queue, inbox, lessons and
protocols. `bash scripts/verify.sh` checks the release surface.
