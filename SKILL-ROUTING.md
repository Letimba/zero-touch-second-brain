# SKILL-ROUTING — Kuratierter Skill-Index (Stand 2026-11-27)

Zweck: Bei ~670 installierten Skills nicht den ganzen Ordner scannen. Der
Supervisor und jeder Subagent prüft zuerst diese Datei. Nur wenn hier nichts
passt, wird `~/.config/opencode/skills/` nach Namen gefiltert.

**Budget: 1–3 Skills pro Arbeitspaket.** Jeder Skill braucht einen Grund im
Delegations-Brief. Nur tatsächlich geladene Skills als geladen bezeichnen.

## 0. Schnellzuordnung (häufige Task-Typen)

| Task-Typ | Skills |
|---|---|
| VPS/Service antwortet falsch, nginx/Deploy, 401/502 | `systematic-debugging` + `devops-automator` |
| Tailwind-v4/shadcn/Next.js-UI kaputt | `tailwind-theme-builder` + `shadcn-ui` |
| OWASP/Auth/CSRF/Secrets-Audit ohne Änderung | `code-security-audit` + `security-review` |
| Unabhängiger QA-Gegencheck, Datenverlust, Automation | `code-security-audit` + `verification-before-completion` |
| Visuelle Richtung, Designsystem, Premium-Landingpage | `frontend-design` + `design-review` |
| Architektur erklären **plus Implementierungspfad** | `writing-plans` |
| Multi-Step-Plan, Migration in Schritten | `writing-plans` |
| E2E-Tests flaky, Playwright | `playwright-e2e-tester` + `test-automation-expert` |
| DNS-Records, TLS-Zertifikat, E-Mail-Auth | `devops-automator` |
| Session-Digest → atomare Lektionen, Lernindex | `obsidian-second-brain` |
| Mehrere Domänen gleichzeitig prüfen | `agent-architecture-audit` + `code-security-audit` |
| Obsidian-Inventar, Vault-Struktur, Archivierung | `obsidian-second-brain` |

Nur wenn hier nichts passt: Abschnitte 1–6 unten prüfen.

## 1. Prozess & Orchestrierung

| Situation | Skill |
|---|---|
| Preflight vor nicht-trivialer Aufgabe | `using-superpowers` |
| Idee/Feature klären, bevor Code entsteht | `brainstorming` |
| Multi-Step-Implementierungsplan | `writing-plans`, `executing-plans` |
| Bug / unerwartetes Verhalten | `systematic-debugging` |
| Neue Features/Bugs test-first | `test-driven-development` |
| Abschluss prüfen | `verification-before-completion` |
| 2+ unabhängige Tasks parallelisieren | `dispatching-parallel-agents`, `parallel-execution-optimizer` |
| Plan mit Subagents umsetzen | `subagent-driven-development` |
| Skill/Command-Auswahl mehrstufig | `orchestrator` |

## 2. Web / React / Next.js

| Situation | Skill |
|---|---|
| Next.js 16 App Router, RSC, Server Actions | `nextjs` |
| React 18/19 Hooks, Komponenten, Rendering | `react-patterns` |
| React/Next.js Performance | `vercel-react-best-practices`, `react-performance` |
| UI-Review, Guideline-Check | `web-design-guidelines`, `design-review` |
| Distinkte visuelle Richtung | `frontend-design` |
| Tailwind v4 / shadcn Theming | `tailwind-theme-builder`, `shadcn-ui` |
| Motion/Animation | `motion-foundations` |
| A11y WCAG 2.2 | `accessibility` |
| Formulare, Multi-Step-Wizard | `form-validation-architect` (falls installiert), sonst `react-patterns` |

## 3. Tests & Qualität

| Situation | Skill |
|---|---|
| Code-Review von Diffs | `code-review`, `code-review-checklist` |
| Security-Audit OWASP/ASVS | `code-security-audit`, `security-review` |
| Unit-/Komponententests | `vitest` |
| Browser-E2E/Playwright | `playwright-e2e-tester` |
| Teststrategie, Flaky-Tests, Coverage | `test-automation-expert` |
| Skill-Qualität bewerten | `skill-grader` |
| Agent-Stack auditieren | `agent-architecture-audit`, `agent-eval` |

## 4. Backend / Daten / Infra

| Situation | Skill |
|---|---|
| REST-API-Design | `api-design` |
| Node/Express/Next API-Routes | `backend-patterns` |
| DB-Schema, Migrationen | `database-migrations`, `postgres-patterns` |
| Supabase/RLS | `supabase-admin` |
| Caching/Invalidierung | `caching-strategies` |
| Logging/Observability | `logging-observability` |
| CI/CD, Deployment | `devops-automator`, `vercel-deployment` |
| Docker/Kubernetes | `docker-patterns`, `kubernetes-patterns` |
| Sprache: Python/Go/Rust | `python-patterns`, `golang-patterns`, `rust-patterns` |

## 5. SEO / Growth / Content

| Situation | Skill |
|---|---|
| Technisches/On-Page-SEO-Audit | `seo`, `seo-optimizer` |
| Voll-Score-Audit + AI Search | `ultimate-seo-geo-skill` |
| Keyword-Cluster, Hub/Spoke | `seo-keyword-cluster-builder` |
| Discoverability, llms.txt, AEO | `seo-visibility-expert` |
| Positionierung/ICP/Brand Voice | `product-marketing`, `consulting-growth` |
| Copy/Page-Text | `copywriting`, `copy-editing` |
| Jobs/CV/Anschreiben | `ai-job-career-agent` |

## 6. Wissen / Vault / Agenten

| Situation | Skill |
|---|---|
| Obsidian-Second-Brain-Architektur | `obsidian-second-brain` |
| Geteilter Kontext zwischen Sessions | `unified-memory` |
| Neue Skills anlegen | `skill-creator`, `skill-architect` |
| Neue Agenten/MCPs anlegen | `agent-creator` |
| Skill finden, bevor neu bauen | `skill-scout`, `find-skills` |
| Doku/Runbooks | `technical-writer`, `document-writing` |

## 7. Nicht im Index

Wenn kein Eintrag passt: `ls ~/.config/opencode/skills/ | grep <stichwort>`,
dann `SKILL.md` nur so weit lesen, wie der Workflow verlangt. Keine Audit-
Skills „auf Verdacht" laden. Bei Überschneidung: den enger passenden Skill
nehmen, den anderen dem Owner als Alternative nennen.
