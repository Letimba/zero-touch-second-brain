# Obsidian ecosystem — what we borrowed

Source: Reddit thread `r/SATNA_PROJECT/s/zkhj2qM4Yh` (2026-11-24),
„Obsidian's CEO shared his vault setup on GitHub. Here are 8 repos worth
bookmarking." The advice: borrow a working structure, add only tools that solve
a real problem.

## The eight repositories (stars checked 2026-11-27 via GitHub API)

| Repo | Stars | Idea |
|---|---:|---|
| `kepano/kepano-obsidian` | 6,482 | Bottom-up vault template, explicitly not dogmatic |
| `obsidianmd/obsidian-skills` | 54,001 | Agent Skills per agentskills.io spec, portable across clients |
| `kepano/obsidian-minimal` | 5,773 | Distraction-free theme; UI tuning is not note-taking |
| `obsidianmd/obsidian-importer` | 1,861 | Import from other apps into durable Markdown |
| `obsidianmd/obsidian-clipper` | 5,694 | Web capture into Markdown you can read offline |
| `obsidianmd/jsoncanvas` | 3,982 | Open `.canvas` format for spatial data |
| `obsidianmd/obsidian-help` | 2,054 | Docs as standalone vaults; English first, translations later |
| `obsidianmd/obsidian-sample-plugin` | 4,765 | TypeScript plugin template with typed API definitions |

The post says "Sample Plugin" without a URL; the official repository is
`obsidianmd/obsidian-sample-plugin`.

## What this project adopted

1. **Bottom-up structure** — `examples/vault/` is a small starting point, not a
   complete brain. Copy it, then make it yours.
2. **Durable Markdown** — every generated artifact is `.md`, regardless of the
   producing agent.
3. **Open spatial format** — `examples/vault/learning-loop.canvas` uses JSON
   Canvas so the loop can be viewed as a board without a proprietary app.
4. **Client independence** — the same learning-loop rules are the source of
   truth; adapters only change paths and file formats. Full agentskills.io
   packaging is the next step, not a current feature.
5. **Focus over UI** — no theme or appearance work is part of the automation.

## What we deliberately did not adopt

- Importer and Web Clipper as runtime dependencies: capture stays local and
  script-driven; both tools remain optional user choices.
- A plugin: everything here works without installing an Obsidian plugin.
- Translations of this README: one canonical English document first.

See `docs/COMPATIBILITY.md` for the current adapter matrix and
`docs/ANNOUNCEMENTS.md` for distribution drafts.
