# Routing benchmark

## Question

Do explicit routing rules produce measurably better agent dispatch decisions
than the old informal table?

## Setup

- Eleven dispatch scenarios covering debugging, UI fixes, audits, planning, E2E,
  DNS, vault learning and cross-domain parallel work.
- Same model (`hy4-flash-free`) and the same tool-free router agent for both runs.
- Baseline: the old routing table. Optimized: `AGENT-ROUTING.md` plus
  `SKILL-ROUTING.md`, a decision tree, parallel limits and a verification rule.
- Scoring, 0 to 100: primary agent 40, fallback 10, parallelisation 15, skills 15,
  write scope 10, verification 10.

## Result

| Variant | Score |
|---|---:|
| Old routing table | 64.5 / 100 |
| Registry only | 91.4 / 100 |
| Registry plus skill index | 100.0 / 100 |
| Improvement | +35.5 points |

All eleven scenarios reached full marks in the final run: correct owner,
fallback, parallel decision, one to three relevant skills, isolated write scope
and a concrete verification command.

## Reproduce

```bash
cd ~/.config/opencode/bench
python3 gen_prompts.py
opencode run --agent dispatch-bench --auto --title "Baseline" "$(cat prompt-baseline.txt)" > out-baseline.txt 2>&1
opencode run --agent dispatch-bench --auto --title "Optimized" "$(cat prompt-optimized.txt)" > out-optimized.txt 2>&1
python3 score.py out-baseline.txt out-optimized.txt
```

`scenarios.json`, `gen_prompts.py` and `score.py` live in that local benchmark
directory; they are not part of this repository.

## Limits

100/100 applies to these eleven scenarios only. One run per variant was scored,
model outputs are not deterministic, and the benchmark measures dispatch
decisions rather than execution quality. The expected answers were set by the
author. Treat the number as a regression gate for routing rules, not as a claim
about every possible task.
