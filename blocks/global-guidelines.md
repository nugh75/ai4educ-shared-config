# Global Guidelines

## Session Start Check (credits & context)

Applicare a ogni sessione in qualsiasi agente terminale (Claude Code, Codex, OpenCode, pi), prima di qualsiasi lavoro:

1. **Crediti/Limiti**: verificare che l'agente abbia crediti o quota disponibili (es. `/usage` in Claude Code, limiti in Codex, provider configurato in OpenCode/pi). Se i crediti sono esauriti o non disponibili, notificare immediatamente l'utente e fermarsi: non iniziare lavori che rischiano di interrompersi a metà.
2. **Baseline context**: se lo strumento lo espone (`/context`, status line), rilevare l'occupazione iniziale del contesto. Se il baseline è anomalo (>10% prima del primo prompt), segnalarlo all'utente prima di procedere.

## Session Command Discipline

Gestione della storia di conversazione per contenere la crescita dei token:

- **`/rewind`**: scelta preferita per correzioni a metà sessione — ripristina uno stato precedente senza consumare token aggiuntivi e senza rielaborare la storia.
- **`/clear`**: reset al baseline, obbligatorio quando si pivota a un workstream non correlato. Prima di un `/clear` su lavoro non finito, scrivere un Handoff File (skill `handoff`).
- **`/compact`**: da evitare. Consuma token per generare la sintesi e introduce rischi: il modello decide soggettivamente quali dettagli tecnici sono "disponibili". Preferire `/rewind` o l'Handoff File.

## Model Selection Matrix

Abbinare l'intelligenza del modello alla complessità del task: usare un modello frontier per una routine è spesa inutile.

| Task | Tier | Esempi |
|---|---|---|
| Architettura, debugging complesso, codice di produzione | Frontier | modelli di ragionamento massimo disponibili sul provider |
| Routine standardizzate, drafting, refactoring semplice | Medio | il modello di fascia media del provider |
| Sub-agent, browsing, estrazione bulk, analisi multi-fonte | Economico | modelli leggeri/veloci (efficiency leader) |

**Mid-Session Switch Penalty**: non cambiare modello o effort level a conversazione in corso — il nuovo modello ricarica e rielabora tutta la storia, con costo di token massiccio e ridondante. Scegliere il modello all'inizio della sessione in base al task.

## Golden Rule: AI for Judgment, Code for Execution

Usare l'AI per il **judgment** (decisioni, progettazione, analisi); usare il **codice** per l'esecuzione. Qualsiasi routine AI che ripete sempre lo stesso task è candidata alla migrazione a script Python/Bash deterministico: progetto con l'AI una volta, poi lo script garantisce ripetibilità 100%, velocità massima e costo ricorrente zero.

### Anti-pattern vietati

- **Text screenshots**: non usare screenshot per catturare testo. Usare testo diretto o hook ottimizzati (es. PDF-to-Text): il parsing visivo costa in modo sproporzionato.
- **Prompt poveri di contesto**: prompt brevi e vaghi generano interazioni multi-turno costose. Fornire fin da subito contesto, vincoli e output atteso.
- **Bloatware di efficienza**: evitare wrapper di terze parti che promettono risparmi omettendo dati critici; preferire gli strumenti nativi dello strumento in uso.

## Scheduled Token Audit

Checklist di audit periodico (dettagli: `ai4educ-shared-config/docs/token-optimization.md`):

1. **Script Conversion**: il task judgment-free è migrabile a Python/Bash?
2. **Model Distillation**: la routine si può abbassare di tier?
3. **Index Integrity**: i file globali restano sotto le 200 righe?
4. **Baseline Audit**: la sessione parte a 3-6%? Token Leakage da MCP/skill inutilizzati?

## ASCII Prototyping

Per lavori UI/UX, finalizzare la **struttura** in un diagramma ASCII (layout, gerarchie, stati) prima di generare codice (HTML/CSS/JSX). Iterare sul diagramma, non sul codice: elimina il ciclo costoso di rigenerazione di blocchi interi per aggiustamenti estetici. Passare al codice solo quando l'utente ha validato la struttura.

## Karpathy Coding Guidelines

Behavioral guidelines to reduce common LLM coding mistakes. Bias toward caution over speed. For trivial tasks, use judgment.

### 1. Think Before Coding

Before implementing:
- State assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

Minimum code that solves the problem. Nothing speculative.

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

### 3. Surgical Changes

Touch only what you must. Clean up only your own mess.

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

### 4. Goal-Driven Execution

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

---

## Planning and Clarification Modes

### Plan Mode

Activated when user says: "plan mode", "modalità piano", "prima fai un piano", or `/plan`.
Deactivated with: "stop plan mode", "normal mode", or `/plan off`.

When active, before making code changes or running destructive/long-running commands:
- Restate the goal in 1-3 bullets.
- List assumptions and unknowns.
- Ask precise questions if required information is missing.
- Provide a short step-by-step plan.
- Wait for user confirmation before implementing, unless the user explicitly says to proceed.

For trivial read-only tasks, answer directly and keep the plan minimal.

### Precise Questions Mode

Activated when user says: "fammi domande", "domande precise", "question mode", or `/questions`.
Deactivated with: "stop questions", "normal mode", or `/questions off`.

When active:
- Ask only necessary questions.
- Prefer numbered multiple-choice questions when possible.
- Do not ask for information already available from files, context, or previous messages.
- If there are multiple valid interpretations, ask before choosing.

### "Hai capito?" Understanding Check

Activated when user asks: "hai capito?", "cosa hai capito?", "dimmi cosa hai capito", or `/understood`.

Respond with:
- **Obiettivo capito**: concise summary of the requested outcome.
- **Vincoli/Preferenze**: constraints, style, tools, or workflow requirements understood.
- **Dati mancanti**: only missing information needed to proceed.
- **Prossimo passo**: the next action, or ask for confirmation if needed.

Do not implement during an understanding check unless the user explicitly asks to proceed.

---

## Caveman Mode

Activated when user says: "caveman mode", "talk like caveman", "use caveman", "less tokens", "be brief", or `/caveman`.
Deactivated with: "stop caveman" or "normal mode".

When active: respond terse like smart caveman. All technical substance stay. Only fluff die.

Drop: articles (a/an/the), filler, pleasantries, hedging. Fragments OK. Short synonyms. Technical terms exact. Code blocks unchanged.

Default level: **full**. Switch: `/caveman lite|full|ultra`.

Code, commits, PRs: always write normal regardless of mode.

---

## ai4educ Infrastructure

- **Sync delle istruzioni**: vedi sezione generata in fondo al file (istruzioni di sync).
- **\`r-cl-ag\`**: alias per \`sudo systemctl restart cloudflared-agent\`, riavvia l'host-agent dopo modifiche. Disponibile in \`~/bin/\`, nel PATH.
- **Console**: disponibile su ai4educ.org, pannello "Config Docs" per gestire regole condivise e monitorare allineamento CONTEXT.md.
- **Skill**: ogni agente legge una root diversa (`~/.claude/skills`, `~/.agents/skills`, `~/.pi/agent/skills`, `~/.config/opencode/skills`) e nessuno legge quelle degli altri. `./scripts/sync-skills.sh` allinea tutte e quattro le root a partire da `~/.agents/skills` e `~/ai4educ-console/workspace-skills`; viene eseguito in automatico da `sync-global.sh`.
