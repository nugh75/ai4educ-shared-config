# ai4educ-shared-config

Istruzioni canoniche per tutti i coding agent dei progetti ai4educ.

## Struttura

```
blocks/
  shared-rules.md          ← regole di processo (git, commit, Docker, ...)
  global-guidelines.md     ← linee guida comportamentali (Karpathy, modalità)
templates/
  CONTEXT.md.template      ← template per CONTEXT.md di progetto
scripts/
  sync-project.sh          ← genera AGENTS.md + CLAUDE.md per un progetto
  sync-global.sh           ← genera i file globali per ogni tool
projects.txt               ← elenco dei progetti
```

## Uso

### Modificare le regole di processo
1. Modifica `blocks/shared-rules.md`
2. `./scripts/sync-project.sh --all`

### Modificare le linee guida globali
1. Modifica `blocks/global-guidelines.md`
2. `./scripts/sync-global.sh`

### Aggiungere un nuovo progetto
1. Aggiungi il path in `projects.txt`
2. `./scripts/sync-project.sh --project /path/to/project`
3. Crea `CONTEXT.md` nel progetto partendo da `templates/CONTEXT.md.template`

### Verificare allineamento (CI)
```bash
./scripts/sync-project.sh --check --project /path/to/project
./scripts/sync-global.sh --check
```

## File generati vs manuali

| File | Generato? | Sincronizzato da |
|---|---|---|
| `AGENTS.md` (progetto) | ✅ | `sync-project.sh` |
| `CLAUDE.md` (progetto) | ✅ | `sync-project.sh` |
| `CONTEXT.md` (progetto) | ❌ | Scritto a mano |
| `~/.pi/agent/AGENTS.md` | ✅ | `sync-global.sh` |
| `~/.claude/CLAUDE.md` | ✅ | `sync-global.sh` |
| `~/.codex/AGENTS.md` | ✅ | `sync-global.sh` |
| `~/.opencode/AGENTS.md` | ✅ | `sync-global.sh` |

**Non modificare mai a mano i file generati.** Per modificare le istruzioni, modifica i blocchi canonici in `blocks/` e rilancia lo script di sync.
