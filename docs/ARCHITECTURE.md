# Architecture

## Components

| Path | Role |
|---|---|
| `automation/clipboard_capture.sh` | Clip → raw archive + inbox draft, SHA-256 dedupe |
| `automation/session_export.py` | Local OpenCode API export, redaction, digest queue |
| `automation/brain-auto.sh` | Orchestrator with lock, state, retry and status |
| `automation/brain_hygiene.py` | Vault lint, inbox/queue counts, secret scan, health JSON |
| `agents/brain-scribe.md` | Digest → ≤5 lessons + 1 protocol |
| `agents/brain-curator.md` | Inbox triage with manifest and daily protocol |

## Data flow

1. Capture writes raw data into `00_Rohdaten/` and a draft into `00_Eingang/`.
2. Export writes a redacted digest into `automation/queue/`.
3. The orchestrator picks one digest and dispatches `brain-scribe`.
4. Lessons and the protocol land in the vault's memory area; `_Lernindex.md` is
   updated with at most ten top rules.
5. The curator files inbox drafts with a manifest; originals stay untouched.
6. Hygiene writes `state/health.json` and a human-readable report.

## Boundaries

- Raw layers are immutable.
- Only curated agents write curated notes.
- Runtime data (`queue/`, `logs/`, `state/`) is never committed.
- The supervisor is the only dispatcher.
