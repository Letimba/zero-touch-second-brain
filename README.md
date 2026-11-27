# zero-touch-second-brain

**Turn every agent session into Markdown you can reuse.**

Clipboard drops and finished OpenCode sessions become atomic lessons, a
ten-rule index and a health report. The files stay on your machine in plain
Markdown, including on Android through Termux.

![License: MIT](https://img.shields.io/badge/license-MIT-green)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![Platform: Termux, Linux, macOS](https://img.shields.io/badge/platform-Termux%20%7C%20Linux%20%7C%20macOS-orange)
![Release: v0.4.0](https://img.shields.io/badge/release-v0.4.0-blue)
![Routing benchmark: 100/100](https://img.shields.io/badge/routing%20benchmark-100%2F100-brightgreen)

A self-hosted AI second brain for developers: persistent agent memory in an
Obsidian-compatible vault, with capture, distillation, retrieval, inbox triage
and verification on autopilot.

![The five steps: capture, distill, retrieve, triage, verify](docs/assets/hero.svg)

## Contents

- [Why this exists](#why-this-exists)
- [What it does](#what-it-does)
- [See it work](#see-it-work)
- [Install](#install)
- [What is in the repo](#what-is-in-the-repo)
- [Works with your agents](#works-with-your-agents)
- [Safety and privacy](#safety-and-privacy)
- [Commands](#commands)
- [FAQ](#faq)
- [Proof: routing benchmark](#proof-routing-benchmark)
- [Docs](#docs)

## Why this exists

You finish a long session with an agent. The useful part is a decision, a root
cause or a rule you will need next week. By then the transcript is buried, so
you retype the lesson or skip it.

This project gives that job to the agent. One cycle turns raw input into
reusable notes, then the next session reads a short index instead of a whole
archive. The format is Markdown you can open, move and delete without asking
any tool for permission.

## What it does

1. **Capture.** Clipboard text and completed sessions become drafts. Clips are
   deduplicated by SHA-256 and token-shaped strings are redacted.
2. **Distill.** `brain-scribe` writes at most five atomic lessons and one
   protocol per session, checked against the lessons you already have.
3. **Retrieve.** Each new session reads a ten-rule index first. Full lessons
   open only when their topic matches the task.
4. **Triage.** `brain-curator` files inbox drafts into curated notes and writes
   a manifest, so every move has a trace.
5. **Verify.** A hygiene check reports broken links, missing frontmatter,
   secret-shaped strings and scheduler state.

Each step writes text back into the vault. Obsidian is a viewer here; the vault
works in any editor.

## See it work

[Open the static demo](docs/demo/index.html). It shows a real command sequence:
one session captured, two lessons written, a protocol stored, health green and
the queue empty.

## Install

```bash
git clone https://github.com/Letimba/zero-touch-second-brain.git
cd zero-touch-second-brain
bash scripts/install.sh
bash scripts/verify.sh
```

The installer copies two agents and two commands into `$HOME/.config/opencode/`,
creates a minimal example vault at `$VAULT` (default `$HOME/SecondBrain`) and
backs up any file it replaces. Clipboard capture starts off. Set
`CLIPBOARD_CAPTURE=1` when you want it.

On Termux, schedule the wrapper script. Android has no `/usr/bin/env`, so the
portable scripts are called through `$PREFIX/bin/bash`:

```bash
termux-job-scheduler --script "$HOME/zero-touch-second-brain/scripts/termux/brain-auto-termux.sh" \
  --job-id 99101 --period-ms 900000 --persisted true
```

[Full quick start](QUICKSTART.md)

## What is in the repo

| File | What you get |
|---|---|
| `agents/brain-scribe.md` | Session notes become reusable rules |
| `agents/brain-curator.md` | Inbox drafts become filed notes with a manifest |
| `commands/session-learn.md` | `/session-learn` runs the loop on demand |
| `commands/brain-status.md` | `/brain-status` shows runs, health and queue |
| `AGENT-ROUTING.md` | One owner per task, clear fallbacks, parallel limits |
| `SKILL-ROUTING.md` | A short skill index instead of scanning hundreds of skills |
| `automation/` | Capture, export, orchestration, redaction and hygiene scripts |
| `examples/vault/` | Synthetic vault plus a JSON Canvas overview of the loop |
| `tests/` | Eight tests covering release hygiene and core logic |

## Works with your agents

OpenCode runs the full loop. Community adapters carry the same learning rules
to Claude Code, Codex, Gemini CLI, Cursor and Windsurf. Each adapter writes the
context file or subagent definition its client reads.

| Agent | What the adapter installs |
|---|---|
| OpenCode | Agents and commands, native |
| Claude Code | `AGENTS.md` plus two subagents in `~/.claude/agents/` |
| Codex | `AGENTS.md` plus a skill in `~/.codex/skills/` |
| Gemini CLI | `~/.gemini/GEMINI.md` |
| Cursor | `AGENTS.md` and a `.mdc` project rule |
| Windsurf | Global rules and an optional project rule |

[Compatibility matrix and limits](docs/COMPATIBILITY.md)

## Safety and privacy

Tokens are read from the local OpenCode service config at runtime. The export
step redacts token-shaped strings, personal paths and hostnames before a digest
is written. Raw captures stay immutable; the curator writes new files and a
manifest. Runtime data in `queue/`, `logs/` and `state/` is gitignored.

Generated digests can still contain project codenames from your sessions. Keep
them out of issues and public repositories. [SECURITY.md](SECURITY.md) explains
the boundary and what to redact before sharing.

## Commands

| Command | Effect |
|---|---|
| `bash automation/brain-auto.sh` | One full cycle |
| `bash automation/brain-auto.sh --session-now` | Export and distill the latest session |
| `bash automation/brain-auto.sh --status` | Last run, health and queue |
| `python3 automation/brain_hygiene.py` | Vault, inbox, secrets and scheduler report |
| `python3 automation/verify_learning.py` | Validate lessons, protocols and index |
| `bash scripts/verify.sh` | Release hygiene gate |

## FAQ

### Does it send my notes anywhere?

Every step runs locally. The scheduler starts a local script and the session
export talks to the local OpenCode API.

### Does it read my chats?

It reads the local OpenCode session API when you trigger an export. Clipboard
capture is opt-in and skips text under 20 characters.

### Do I need Obsidian?

No. The vault is plain Markdown with an optional `.canvas` overview. Any editor
opens it.

### Where do the lessons come from?

They are generated from your sessions. The example vault contains synthetic
placeholders and two sample rules.

### Can I use it with Claude Code or Codex?

Yes, with the included adapters. They install the same rules as context files
or subagents. The full scheduler and session API live in OpenCode.

### What happens when a run fails?

The lock prevents overlapping runs, state records the failed step and the next
cycle retries. Health stays readable through `/brain-status`.

## Proof: routing benchmark

Eleven dispatch scenarios, the same model, one tool-free router agent. The old
routing table scored 64.5/100. The current registry and skill index scored
100/100. Scoring covers agent choice, fallback, parallelisation, skills, write
scope and verification.

[Benchmark setup and limits](docs/BENCHMARK.md)

## Docs

[Quick start](QUICKSTART.md) · [Architecture](docs/ARCHITECTURE.md) ·
[Learning loop](docs/LEARNING-LOOP.md) · [Compatibility](docs/COMPATIBILITY.md) ·
[Obsidian ecosystem](docs/OBSIDIAN-ECOSYSTEM.md) · [Benchmark](docs/BENCHMARK.md) ·
[Demo](docs/demo/index.html) · [Security](SECURITY.md) · [FAQ](docs/FAQ.md) ·
[Roadmap](DISTRIBUTION-PLAN.md) · [Changelog](CHANGELOG.md) ·
[llms.txt](llms.txt)

## Contributing

[CONTRIBUTING.md](CONTRIBUTING.md) covers the ground rules. Every code change
needs a command and its real output in the pull request, plus a release gate
run before review.

## License

MIT. See [LICENSE](LICENSE).
