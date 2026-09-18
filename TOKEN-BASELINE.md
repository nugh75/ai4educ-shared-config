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
