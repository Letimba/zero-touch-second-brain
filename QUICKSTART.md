# Quick start

## 1. Requirements

- Python 3.10+ (standard library only)
- OpenCode CLI with a running local service (for session export)
- A folder for your vault; Obsidian is optional
- Optional: `termux-clipboard-get` on Android, or `xclip`/`pbpaste` elsewhere

## 2. Install

```bash
git clone https://github.com/Letimba/zero-touch-second-brain.git
cd zero-touch-second-brain
bash scripts/install.sh
```

The installer:

- copies `agents/*.md` and `commands/*.md` into `$HOME/.config/opencode/`,
  backing up existing files with a timestamp
- copies `examples/vault/` to `${VAULT:-$HOME/SecondBrain}` if the target is empty
- does not touch an existing vault
- does not install packages, change DNS, or contact any service

## 3. Configure

```bash
export VAULT="$HOME/SecondBrain"
export SECOND_BRAIN_HOME="$HOME/zero-touch-second-brain"
```

Optional automations:

- Termux scheduler (15 min):
  `termux-job-scheduler --script "$SECOND_BRAIN_HOME/automation/brain-auto.sh" --job-id 99101 --period-ms 900000 --persisted true`
- Any new shell: add
  `bash "$SECOND_BRAIN_HOME/automation/brain-auto.sh" --bg` to your shell rc with
  a 30-minute throttle.

## 4. Verify

```bash
bash scripts/verify.sh
python3 -m unittest discover -s tests
```

## 5. First run

```text
/session-learn
/brain-status
```

`/session-learn` needs at least one finished OpenCode session. The example
vault contains a sample digest you can use instead.
