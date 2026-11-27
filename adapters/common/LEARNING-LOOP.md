# Second Brain learning loop (shared context)

Read `{{VAULT}}/95_System/Agentenverwaltung/04_Gedaechtnis_und_Kontext/_Lernindex.md`
at the start of a non-trivial session. Read only the top-rules table. Open a
full lesson only if its title or scope matches the current task. Apply the rules
silently.

At the end of non-trivial work (5+ tool calls, debugging, architecture, deploy):

1. Run `bash {{SRC}}/automation/brain-auto.sh --session-now`.
2. Keep at most five new lessons per session, each under 400 words, deduplicated
   against `{{VAULT}}/95_System/Agentenverwaltung/04_Gedaechtnis_und_Kontext/Lektionen/`.
3. Write session protocols to `Lernprotokolle/`, never raw chat transcripts.
4. Never store secrets in the vault. Raw layers are immutable.
5. Check `{{VAULT}}/95_System/Agentenverwaltung/02_Aufgaben/_brain-health.md`
   when health is reported as critical.

If the script is unavailable, say so and continue without inventing results.
