# Global Guidelines

Indice globale (nested index, <200 righe). Documentazione profonda in `ai4educ-shared-config/docs/`, letta solo su necessità.

## Session Start Check (credits & context)

Applicare a ogni sessione in qualsiasi agente terminale (Claude Code, Codex, OpenCode, pi), prima di qualsiasi lavoro:

1. **Crediti/Limiti**: verificare che l'agente abbia crediti o quota disponibili (es. `/usage` in Claude Code, limiti in Codex, provider configurato in OpenCode/pi). Se esauriti o non disponibili, notificare immediatamente l'utente e fermarsi: non iniziare lavori che rischiano di interrompersi a metà.
2. **Baseline context**: se lo strumento lo espone (`/context`, status line), rilevare l'occupazione iniziale. Se anomala (>10% prima del primo prompt), segnalarla prima di procedere.

## Session Command Discipline

Gestione della storia di conversazione per contenere la crescita dei token:

- **`/rewind`**: preferito per correzioni a metà sessione — ripristina uno stato precedente senza token aggiuntivi.
- **`/clear`**: obbligatorio sui pivot a workstream non correlato. Prima, su lavoro non finito, scrivere un Handoff File (skill `handoff`).
- **`/compact`**: da evitare — consuma token per la sintesi e il modello decide soggettivamente quali dettagli sono "disponibili".

## Model Selection Matrix

Abbinare l'intelligenza del modello alla complessità del task: mai frontier per una routine.

| Task | Tier |
|---|---|
| Architettura, debugging complesso, codice di produzione | Frontier |
| Routine standardizzate, drafting, refactoring semplice | Medio |
| Sub-agent, browsing, estrazione bulk, analisi multi-fonte | Economico |

**Mid-Session Switch Penalty**: non cambiare modello o effort level a conversazione in corso — il nuovo modello ricarica e rielabora tutta la storia. Scegliere il modello all'inizio in base al task.

## Golden Rule: AI for Judgment, Code for Execution

Usare l'AI per il **judgment** (decisioni, progettazione, analisi); il **codice** per l'esecuzione. Ogni routine ripetitiva judgment-free è candidata alla migrazione a script Python/Bash deterministico: ripetibilità 100%, costo ricorrente zero.

Anti-pattern vietati: **text screenshots** (usare testo diretto o hook), **prompt poveri di contesto** (causano multi-turno costosi), **bloatware di efficienza** (wrapper di terze parti che omettono dati; preferire strumenti nativi).

## Scheduled Token Audit

Checklist di audit periodico (dettagli: `docs/token-optimization.md`):

1. **Script Conversion**: il task judgment-free è migrabile a Python/Bash?
2. **Model Distillation**: la routine si può abbassare di tier?
3. **Index Integrity**: i file globali restano sotto le 200 righe?
4. **Baseline Audit**: la sessione parte a 3-6%? Token Leakage da MCP/skill inutilizzati?

## ASCII Prototyping

Per lavori UI/UX, finalizzare la **struttura** in un diagramma ASCII prima di generare codice (HTML/CSS/JSX). Iterare sul diagramma, non sul codice; passare al codice solo dopo validazione della struttura.

## Karpathy Coding Guidelines

Linee guida comportamentali contro gli errori comuni di coding LLM. Testo integrale: `docs/karpathy-guidelines.md`.

1. **Think Before Coding** — assumioni esplicite; presentare le interpretazioni multiple; chiedere se qualcosa non è chiaro.
2. **Simplicity First** — minimo codice che risolve il problema; niente feature o astrazioni speculative.
3. **Surgical Changes** — toccare solo il necessario; rispettare lo stile esistente; pulire solo i propri orfani.
4. **Goal-Driven Execution** — trasformare i task in obiettivi verificabili (test prima/dopo).

## Planning and Clarification Modes

Modalità attivabili da trigger — dettagli completi: `docs/interaction-modes.md`.

- **"plan mode" / "modalità piano" / `/plan`** → prima di modifiche o comandi distruttivi: obiettivo, assunzioni, piano a passi; attendere conferma. Per task read-only banali, rispondere direttamente.
- **"fammi domande" / `/questions`** → solo domande necessarie, preferibilmente multiple-choice numerate; chiedere prima di scegliere tra interpretazioni valide.
- **"hai capito?" / `/understood`** → check di comprensione (obiettivo / vincoli / dati mancanti / prossimo passo), senza implementare.

## ai4educ Infrastructure

- **Sync delle istruzioni**: vedi sezione generata in fondo al file (istruzioni di sync).
- **\`r-cl-ag\`**: alias per \`sudo systemctl restart cloudflared-agent\`, riavvia l'host-agent dopo modifiche. Disponibile in \`~/bin/\`, nel PATH.
- **Console**: disponibile su ai4educ.org, pannello "Config Docs" per gestire regole condivise e monitorare allineamento CONTEXT.md.
- **Skill**: ogni agente legge una root diversa (`~/.claude/skills`, `~/.agents/skills`, `~/.pi/agent/skills`, `~/.config/opencode/skills`) e nessuno legge quelle degli altri. `./scripts/sync-skills.sh` allinea tutte e quattro le root a partire da `~/.agents/skills` e `~/ai4educ-console/workspace-skills`; viene eseguito in automatico da `sync-global.sh`.
