# Token Baseline Audit

Baseline dell'occupazione del contesto a sessione pulita (nessun prompt inviato), per i quattro agenti terminale in uso.

Riferimento framework: baseline atteso 3-6%; >10% prima del primo prompt indica Token Leakage (MCP inutilizzati, skill bloatate, system prompt pesante).

## Come misurare

| Agente | Metodo |
|---|---|
| Claude Code | `/context` e `/usage` a sessione appena aperta |
| Codex | status line / indicatore di contesto a sessione appena aperta |
| OpenCode | status line / indicatore di contesto a sessione appena aperta |
| pi | status line / indicatore di contesto a sessione appena aperta |

## Risultati

| Agente | Baseline misurata | Data | Note (MCP/skill sospetti) |
|---|---|---|---|
| Claude Code | — | — | — |
| Codex | — | — | — |
| OpenCode | — | — | — |
| pi | — | — | — |

> Aggiornare questa tabella dopo ogni misurazione. Se il baseline supera il 10%, aprire un audit dell'inventario MCP/skill (carta 0.2 del backlog Token Optimization).

## Inventario MCP / Skill (audit carta 0.2 — 2025, audit automatico)

### MCP server

| Agente | MCP attivi | Costo stimato | Esito |
|---|---|---|---|
| Claude Code | nessuno | 0 | ✅ ottimale |
| Codex | rimosso `genimg` MCP → sostituito da CLI `~/bin/genimg` | 0 | ✅ ottimale (carta 3.2) |
| OpenCode | nessuno | 0 | ✅ ottimale |
| pi | nessuno | 0 | ✅ ottimale |

### Istruzioni globali (AGENTS.md / CLAUDE.md)

| File | Righe | Token stimati | Limite 200 righe |
|---|---|---|---|
| tutti e 4 gli agenti (identici) | 141 | ~1.6k | ✅ sotto soglia |

### Skill (46 totali, allineate su 4 root via symlink)

- Frontmatter aggregato (caricato nel context a ogni sessione): **~21.1k chars ≈ ~5.3k token**
- Descrizioni più pesanti: `treccani` (847 chars), `cli-anything-web` (751), `hooks-audit` (734), `pptx` (696), `ponytail` (661)
- Cluster più voluminoso: **animazioni** (~13 skill — animate, animate-expo, animejs, gsap-scrolltrigger, lottie-animations, motion-framer, scroll-reveal-libraries, improve-animations, find-animation-opportunities, review-animations, didactic-animations, fireworks-tech-graph, animation-vocabulary) ≈ ~5.5k chars di frontmatter

### Stima baseline complessiva

~1.6k (istruzioni) + ~5.3k (skill) + schema tools ≈ **~7k token ≈ 3-4%** su contesto 200k → entro la soglia 3-6%, nessun Token Leakage strutturale rilevato.

### Azioni derivate (candidate per il backlog)

1. **Slack descrizioni skill**: comprimere le descrizioni >400 chars (top 5) — carta livello 1
2. **Cluster animazioni**: valutare se tutte le 13 skill servono attivamente o possono essere archiviate — carta livello 1
3. **genimg MCP**: monitorare l'uso; se occasionale, sostituire con CLI — carta livello 3 (3.2)
