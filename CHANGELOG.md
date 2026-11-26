# Changelog

All notable changes are documented here. Format: Keep a Changelog.

## [0.1.0] - 2026-11-27

### Added

- Sanitized public release candidate: MIT license, `.gitignore`, CI, smoke tests.
- Portable defaults via `VAULT` and `SECOND_BRAIN_HOME`.
- Synthetic example vault without personal data.
- `AGENT-ROUTING.md` and `SKILL-ROUTING.md` from the internal benchmark
  (64.5 → 100.0 on the 11-scenario routing suite).
- `RELEASE-CHECKLIST.md` and `DISTRIBUTION-PLAN.md`.

### Changed

- Removed session digests, logs, runtime state and the personal vault from the
  release scope after the publishability audit.
- Clipboard capture is opt-in (`CLIPBOARD_CAPTURE=1`).

### Not shipped

- Adapters for Claude Code, Codex and Gemini CLI.
- Demo video and docs site (see distribution plan).
