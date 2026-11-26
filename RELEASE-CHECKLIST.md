# Release checklist (manual gates)

Nothing here happens automatically. Each item needs a human decision.

- [ ] `bash scripts/verify.sh` → 0 findings
- [ ] `python3 -m unittest discover -s tests` → OK
- [ ] `grep -r` for personal names, phone numbers, vault paths → 0 hits
- [ ] No `queue/`, `logs/`, `state/`, `imports/`, or real vault in the repo
- [ ] LICENSE matches the README claim (MIT)
- [ ] README describes the real tree and real commands
- [ ] Replace `<owner>` in README/QUICKSTART with the real GitHub owner
- [ ] Decide the repository name and description/topics
- [ ] Add a hero image or 30-second demo (no fake screenshots)
- [ ] Create the repo as **private**, review the file list, then flip to public
- [ ] Announce: Show HN, r/ObsidianMD, r/LocalLLaMA, Product Hunt
- [ ] Git push and any DNS/domain change need explicit user approval

**Never** publish generated session digests, logs, or the personal vault.
