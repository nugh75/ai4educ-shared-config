# Piano refactor Carta 3.1 — Nested Index

> Piano storico: refactor completato il 2026-09-18 (commit `f34d01a` e `b1361fb`).
> Il blocco "Pending Task" è già stato rimosso. I passi seguenti documentano
> l'intervento eseguito e non sono attività pendenti.

## Obiettivo

- Ridurre l'indice globale da ~184 righe generate a **<100 righe**, mantenendo intatti i comportamenti
- L'indice contiene solo: trigger di attivazione + regole brevi operative; i dettagli migrano in `docs/`
- Verificare dopo il refactor: 4 CLI allineati, baseline invariata, nessuna regola persa

## Stato attuale (riferimento)

File generato: **184 righe** (limite 200). Sorgente: `blocks/global-guidelines.md` (~145 righe)
+ sezione sync generata (~39 righe, intoccabile).

## Decisioni sezione per sezione

| Sezione | Righe ora | Decisione | Destinazione |
|---|---|---|---|
| Session Start Check | 7 | **RESTA** (compatta e critica) | indice |
| Pending Task (3.1) | ~5 | **RIMUOVERE** a lavoro finito | — |
| Karpathy Guidelines | ~40 | **COMPRIMERE a ~4 righe**: elenco dei 4 principi con una frase ciascuno; testo integrale migra in `docs/karpathy-guidelines.md` | docs/ |
| Planning and Clarification Modes | ~30 | **COMPRIMERE a ~5 righe**: tabella trigger→modalità (plan/questions/understood) con 1 riga di comportamento; dettagli in `docs/interaction-modes.md` | docs/ |
| Caveman Mode | ~12 | **RIMUOVERE dall'indice**: esiste già la skill `caveman` che copre tutto | skill caveman |
| Session Command Discipline | 8 | **RESTA** | indice |
| ASCII Prototyping | 5 | **RESTA** | indice |
| Golden Rule + Anti-pattern | ~13 | **RESTA** (già compatta) | indice |
| Model Selection Matrix | ~15 | **RESTA** (tabella essenziale) | indice |
| Scheduled Token Audit | ~10 | **RESTA** (checklist + puntatore a docs/) | indice |
| ai4educ Infrastructure | ~6 | **RESTA** | indice |

Stima indice risultante: **~70-80 righe**.

## Passi esecutivi

1. **Branch**: `refactor/nested-index` in `ai4educ-shared-config`
2. Creare `docs/karpathy-guidelines.md` (testo integrale attuale, immutato)
3. Creare `docs/interaction-modes.md` (testo integrale di Plan/Questions/Understood)
4. Comprimere le sezioni nell'indice secondo la tabella sopra
5. Rimuovere la sezione Caveman Mode (verificare che la skill `caveman` sia allineata: `sync-skills.sh --check`)
6. Rimuovere il blocco "Pending Task"
7. `wc -l` sull'indice: deve essere <100 righe
8. Commit atomici: `docs:` per i nuovi file, `refactor:` per l'indice
9. Propagazione: `r-cl-ag` → `./scripts/sync-global.sh` → verifica `--check`
10. Verifica finale: `wc -l` sui 4 file generati (tutti <100 + sync section), aggiornare
    la tabella di stato in `docs/token-optimization.md` (3.1 → ✅)

## Verifiche post-refactor

- `./scripts/sync-global.sh --check` → allineato
- Nei 4 CLI, aprire sessione e verificare: Session Start Check visibile, comandi/mode funzionano, Caveman si attiva via skill
- Baseline contesto: non deve peggiorare (scenderà)

## Rollback

Tutto su branch: `git checkout main` annulla. Nessun dato cancellato: i testi integrali
sopravvivono in `docs/`.
