# Compatibility matrix

Adapter scripts are community ports of the same Markdown learning loop. They
install context files and, where the CLI supports them, agent definitions.
They are **not independently tested on every CLI**; treat them as a starting
point and verify with the CLI's own `/memory` or equivalent command.

| CLI | Native in 0.1.0 | Adapter in 0.2.0 | Installed files | Verification |
|---|---|---|---|---|
| OpenCode | yes | — | agents + commands in `~/.config/opencode/` | `opencode run --agent brain-scribe` |
| Claude Code | no | yes | `~/.claude/AGENTS.md`, `~/.claude/agents/{brain-scribe,brain-curator}.md` | check `~/.claude/agents/` |
| OpenAI Codex | no | yes | `~/.codex/AGENTS.md`, `~/.codex/skills/zero-touch-second-brain/SKILL.md` | `codex` reads AGENTS.md |
| Gemini CLI | no | yes | `~/.gemini/GEMINI.md` | `/memory show` |
| Cursor | no | yes | `AGENTS.md` + `.cursor/rules/*.mdc` in project | rule appears in Rules UI |
| Windsurf | no | yes | global rules + optional project rule | rule appears in Cascade |

Install:
```bash
VAULT="$HOME/SecondBrain" bash scripts/install-adapters.sh claude
VAULT="$HOME/SecondBrain" bash scripts/install-adapters.sh cursor "$HOME/my-project"
```

Only OpenCode supports the full orchestration (scheduler, session API export,
command wrappers). Other CLIs get the retrieval/capture rules; automation must
be started manually or via the scheduler script.

The shared rule text in `adapters/common/LEARNING-LOOP.md` is the single source
of truth. This is a deliberate subset of the
[Agent Skills specification](https://agentskills.io/specification): the rules
are portable, but they are not yet packaged as spec-compliant skills. See
[Obsidian ecosystem](OBSIDIAN-ECOSYSTEM.md) for why that direction was chosen.
