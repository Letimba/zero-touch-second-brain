# AGENT-ROUTING — Kanonische Registry (Stand 2026-11-27)

Zweck: Eindeutige Zuweisung von Aufgaben zu Agenten, ohne Suche, ohne
Überschneidung, ohne Doppelarbeit. Der Supervisor liest diese Datei vor jeder
Delegation. Sie ist die einzige Wahrheit für Rollen und Fallbacks.

## 0. Entscheidungsbaum (vor jeder Delegation)

1. **Ein Dateibereich, < 30 Min Arbeit?** → selbst erledigen. Kein Agent.
2. **Nur Lesen/Analyse?** → 1–4 Subagents parallel (read-only).
3. **Implementierung?** → genau 1 Owner pro Dateibereich, seriell.
4. **Cross-Domain?** → nach Dateibereichen splitten, 1 Owner je Bereich.
5. **Unklar/Architektur?** → `architect-researcher` zuerst, dann dispatchen.
6. **Review?** → immer anderer Agent als der Implementierer.

## 1. Tier-Modell

| Tier | Rolle | Agenten |
|---|---|---|
| T0 | Orchestrierung, Integration, Endverantwortung | `supervisor` |
| T1 | Kanonische Domain-Owner (erste Wahl) | siehe Tabelle §2 |
| T2 | Spezialisten/Fallbacks (nur wenn T1 blockiert oder tiefer spezialisiert) | siehe Tabelle §2 |
| T3 | Sprach-/Tool-spezifische Reviewer & Build-Resolver | siehe §3 |
| T4 | Nur auf expliziten Auftrag (autonome Läufe, Nischen) | `ai-hedge-fund`, `bewerbungs-orchestrator`, `architect`, `build` |

## 2. Domain-Routing (kanonisch → Fallback)

| Aufgabe / Trigger | Primär (T1) | Fallback (T2) | Niemals |
|---|---|---|---|
| Codebase verstehen, Systemarchitektur, Implementierungspfad | `architect-researcher` | `ecc-architect` | `architect` (T4) |
| Multi-Step-Plan, Zerlegung | `planner` | `architect-researcher` | — |
| Next.js/React/TS/Node/API/DB implementieren | `fullstack-engineer` | `web-coder` | `ui-designer` |
| Web-Architektur, Stack-Entscheid, Performance-Design | `web-architect` | `fullstack-engineer` | — |
| UI/UX, Designsystem, Landingpage, visuelle Politur | `design-director` | `ui-designer` | `web-coder` |
| Accessibility, Interaktionsdesign, Wireframes | `uiux-accessibility` | `design-director` | — |
| Typecheck, Lint, Build, Tests, Edge-Cases | `qa-tester` | `tdd-guide` | `qa-security` |
| Browser-E2E, Performance, Responsive, A11y-Audit | `qa-performance` | `e2e-runner` | — |
| Unabhängiger QA-/Regressions-/Datenverlust-Gegencheck | `qa-security` | `security-reviewer` | — |
| OWASP, XSS/CSRF/CSP, Secrets, Auth-Audit (read-only) | `sec-auditor` | `security-reviewer` | — |
| SEO, Keywords, SERP, Technical SEO | `seo-intelligence` | `marketing-growth` | — |
| Affiliate, Partnerprogramme, Funnel, Review-Content | `affiliate-growth` | `marketing-growth` | — |
| Consulting-Positionierung, Premium-Copy, Case Studies | `consulting-growth` | `marketing-growth` | — |
| Growth, Content-Systeme, TikTok, CRO | `marketing-growth` | `consulting-growth` | — |
| Termux/Android, pkg, termux-api, on-device Shell | `termux-specialist` | `devops-termux` | — |
| VPS/Linux, SSH, Services, Deployment, nginx | `devops-termux` | `termux-specialist` | — |
| Domain, DNS, TLS, E-Mail-Auth | `domain-dns` | `devops-termux` | — |
| Obsidian, Vault, durable Memory, Retrieval | `data-memory` | `brain-curator` | — |
| Inbox-Triage, Vault-Hygiene, Tagesnotiz | `brain-curator` | `data-memory` | — |
| Session-Digest → Lektionen/Protokoll | `brain-scribe` | `data-memory` | — |
| Neue Agenten/Skills, Rollen-Design | `agent-factory` | `skill-evolver` | — |
| Skill-Qualität, Skill-Evolution, Benchmarking | `skill-evolver` | `agent-factory` | — |
| Recht, Fristen, Risiko, Vertragsprüfung | `legal-counsel` | — | — |
| Solana, Pump.fun, Helix, On-Chain-Ausführung | `solana-helix` | `quant-trading` | — |
| Crypto/Forex-Backtests, Quant-Strategie, Risiko | `quant-trading` | `solana-helix` | — |
| Harness/Automation-Audit, Loop-Betrieb | `harness-optimizer` | `loop-operator` | — |
| Jobsuche, Stellenanalyse, CV, Anschreiben | `job-scout` / `job-analyzer` / `cv-tailor` / `cover-letter-writer` | `bewerbungs-orchestrator` | — |
| Dokumentation, Codemaps, API-Docs | `doc-updater` | `docs-lookup` | — |
| Bibliotheks-/API-Doku nachschlagen | `docs-lookup` | `context7`-MCP | — |

**Cross-Domain-Regel:** Bei gleichzeitigen, unabhängigen Prüfungen aus mehreren
Domänen koordiniert `supervisor`; Fallback für Integration und unabhängigen
Gegencheck ist `qa-security`.

### 2b. Skill-Pflicht pro Task-Typ (Detail: `SKILL-ROUTING.md`)

| Task-Typ | Skill(s), die gesetzt werden |
|---|---|
| VPS/Service/Debug/nginx/Deployment | `systematic-debugging` + `devops-automator` |
| Tailwind/shadcn/Next.js-UI-Fix | `tailwind-theme-builder` + `shadcn-ui` |
| OWASP/Auth/Secrets-Audit (read-only) | `code-security-audit` + `security-review` |
| Unabhängiger QA-/Security-Gegencheck | `code-security-audit` + `verification-before-completion` |
| Visuelle Richtung / Designsystem / Landingpage | `frontend-design` + `design-review` |
| Architektur erklären **und Implementierungspfad zeigen** | `writing-plans` (Plananteil); `agent-architecture-audit` nur bei Stack-Audit |
| Multi-Step-Plan / Zerlegung | `writing-plans` |
| E2E flaky / Browser-Tests | `playwright-e2e-tester` + `test-automation-expert` |
| DNS/TLS/E-Mail-Auth | `devops-automator` (Agent: `domain-dns`) |
| Session-Digest → Lektionen | `obsidian-second-brain` (Agent: `brain-scribe`) |
| Cross-Domain-Parallel-Prüfung | `agent-architecture-audit` + `code-security-audit` |
| Obsidian/Wissen archivieren/retrieval | `obsidian-second-brain` |

## 3. Sprachspezifische Reviewer & Build-Resolver (T3)

Nur einsetzen, wenn die Sprache eindeutig ist. Sonst `code-reviewer` bzw.
`build-error-resolver`.

| Sprache | Review | Build-Fix |
|---|---|---|
| Python | `python-reviewer` | `build-error-resolver` |
| Go | `go-reviewer` | `go-build-resolver` |
| Rust | `rust-reviewer` | `rust-build-resolver` |
| Java/Spring | `java-reviewer` | `java-build-resolver` |
| Kotlin/Android | `kotlin-reviewer` | `kotlin-build-resolver` |
| C++ | `cpp-reviewer` | `cpp-build-resolver` |
| Ruby/Rails | `ruby-reviewer` | `build-error-resolver` |
| PHP/Laravel | `php-reviewer` | `build-error-resolver` |
| SQL/Postgres | `database-reviewer` | — |
| Sprachunabhängig | `code-reviewer` | `build-error-resolver` |

## 4. Parallelisierungsmatrix

| Arbeitstyp | Parallel erlaubt | Max. Fan-out | Bedingung |
|---|---|---|---|
| Read-only Recherche/Analyse | ja | 4 | keine Schreibzugriffe |
| Reviews verschiedener Packages | ja | 3 | getrennte Dateibereiche |
| Implementierung | nein | 1 | pro Dateibereich strikt seriell |
| QA + Security nach Implementierung | ja | 2 | beide read-only |
| Vault-/Memory-Schreibzugriffe | nein | 1 | ein Schreiber, Lock beachten |
| Deployments | nein | 1 | Freigabe erforderlich |

Gerätegrenze: **max. 3 gleichzeitige `opencode run`-Prozesse** (952 MB RAM,
Swap). Bei RAM-Druck auf 2 reduzieren. Read-only-Subagents im selben Prozess
zählen nicht als eigener Prozess.

## 5. Context-Brief (max. 20 Zeilen)

Jede Delegation enthält exakt:

```
Ziel:        ein prüfbares Ergebnis
Kontext:     max. 5 Dateipfade + 3 Fakten, die der Agent nicht selbst finden kann
Umfang:      erlaubte Schreibpfade; alles andere tabu
Skills:      1–3 Skill-IDs + je ein Grund
Erwartung:   Handoff-Block (§6)
Grenzen:     keine Deploys/Secrets/destruktiven Befehle; max. 2 Versuche
```

Verboten: „explore das Repo", „schau mal", ganze Chatverläufe, ungefilterte
Logs, Secrets. Der Agent liest nur die genannten Pfade plus das, was er für
die Aufgabe zwingend braucht.

## 6. Handoff (max. 15 Zeilen)

```
status:        done | partial | blocked
findings:      belegt mit Pfad:Zeile oder Befehl
changed_paths: exakte Liste
tests:         Befehl + echtes Ergebnis
skills:        tatsächlich geladen + Grund
risks:         verbleibend + nächste konkrete Aktion
```

## 7. Eskalation & Abbruch

- Nach **2 erfolglosen Versuchen** eines Agenten: stoppen, Befund an den
  Supervisor, neu entscheiden (anderer Agent oder selbst lösen).
- Bei `blocked`: nur die konkrete Blockade melden, keine Spekulation.
- Bei widersprüchlichen Handoffs: Supervisor prüft Evidenz, entscheidet,
  dokumentiert die Entscheidung im Abschlussbericht.
- Kein Agent darf einen anderen Agenten starten, außer `supervisor` und
  `architect` (T4, nur autonome Läufe).

## 8. Verifikationsgate (Pflicht)

Jedes implementierende Package endet mit:

1. dem engsten sinnvollen Test (Unit/Typecheck/Build/E2E),
2. einem unabhängigen Review bei Code-Änderungen (`qa-security` oder
   sprachspezifischer Reviewer),
3. einer expliziten Aussage, was **nicht** geprüft werden konnte.

**Verifikation ist immer konkret:** ein Befehl oder ein messbares Ergebnis
(`curl … → 200`, `dig …`, `pytest → 12 passed`, `vault-lint → 0 critical`,
`Manifest: Pfad:Zeile`). Wörter wie „prüfen", „sicherstellen", „kontrollieren"
allein genügen nicht. Bei DNS/TLS gilt: `dig`-Ausgabe **und** TLS-Check **und**
Freigabe vor der Änderung.

Ein grüner Build allein ist kein Abschlussnachweis.
