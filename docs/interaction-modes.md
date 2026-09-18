# Planning and Clarification Modes

Modalità di interazione attivabili da trigger. Testo integrale puntato dall'indice
(nested index: l'indice contiene solo i trigger e il comportamento essenziale).

## Plan Mode

Activated when user says: "plan mode", "modalità piano", "prima fai un piano", or `/plan`.
Deactivated with: "stop plan mode", "normal mode", or `/plan off`.

When active, before making code changes or running destructive/long-running commands:
- Restate the goal in 1-3 bullets.
- List assumptions and unknowns.
- Ask precise questions if required information is missing.
- Provide a short step-by-step plan.
- Wait for user confirmation before implementing, unless the user explicitly says to proceed.

For trivial read-only tasks, answer directly and keep the plan minimal.

## Precise Questions Mode

Activated when user says: "fammi domande", "domande precise", "question mode", or `/questions`.
Deactivated with: "stop questions", "normal mode", or `/questions off`.

When active:
- Ask only necessary questions.
- Prefer numbered multiple-choice questions when possible.
- Do not ask for information already available from files, context, or previous messages.
- If there are multiple valid interpretations, ask before choosing.

## "Hai capito?" Understanding Check

Activated when user asks: "hai capito?", "cosa hai capito?", "dimmi cosa hai capito", or `/understood`.

Respond with:
- **Obiettivo capito**: concise summary of the requested outcome.
- **Vincoli/Preferenze**: constraints, style, tools, or workflow requirements understood.
- **Dati mancanti**: only missing information needed to proceed.
- **Prossimo passo**: the next action, or ask for confirmation if needed.

Do not implement during an understanding check unless the user explicitly asks to proceed.

## Caveman Mode

Gestito dalla skill `caveman` (allineata su tutte le 4 root skill): attivazione con
"caveman mode", "talk like caveman", "use caveman", "less tokens", "be brief", `/caveman`;
disattivazione con "stop caveman" o "normal mode". Livelli: lite / full (default) / ultra.
Code, commits, PRs: always write normal regardless of mode.
