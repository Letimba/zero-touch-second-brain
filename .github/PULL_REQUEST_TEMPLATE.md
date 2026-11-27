## What changed

<!-- One paragraph, no secrets, no real vault content. -->

## Evidence

| Command | Result |
|---|---|
| `bash scripts/verify.sh` | `findings=0` |
| `python3 -m unittest discover -s tests` | `OK` |

## Scope

- [ ] One owner, one write area
- [ ] No runtime data (`automation/{logs,state,queue}/`) committed
- [ ] Docs and CHANGELOG updated if behavior changed
