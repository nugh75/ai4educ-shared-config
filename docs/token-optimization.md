# Token Optimization — Operational Framework

Framework enterprise per ottimizzazione token e ROI dell'AI. Questo documento è la
documentazione profonda puntata dall'indice globale (AGENTS.md/CLAUDE.md): viene letto
solo quando serve il dettaglio operativo, non a ogni sessione.

## 1. Measurement Paradigm

Visibilità granulare dei token = prerequisito per efficienza e ROI. Senza misura,
il workflow AI è una black box con Recursive Cost Accumulation e degrado delle prestazioni.

| Strumento | Funzione | Rischio coperto |
|---|---|---|
| `/context`, `/usage` | % finestra di contesto; consumo vs limiti | overhead nascosto di system prompt, MCP, skill |
| Status Line | indicatore real-time di occupazione | "token shock" durante sviluppo intenso |

**Baseline Context Occupancy**: attesa 3-6% a sessione pulita. Oltre il 10% prima del
primo prompt = Token Leakage (MCP inutilizzati, skill bloatate). Audit: `TOKEN-BASELINE.md`.

## 2. Session Hygiene

- Oltre una certa soglia di riempimento il modello degrada (Quality Drift): perde sfumatura
  tecnica e hallucina logica. Non è solo più costoso, è peggiore.
- `/rewind` > `/compact` per correzioni a metà sessione; `/clear` sui pivot con Handoff
  File preventivo (skill `handoff`). Dettagli nel blocco "Session Command Discipline".
- **ASCII Prototyping**: struttura UI in diagramma ASCII validato prima del codice.

## 3. Structural Optimization

- **Nested Index**: il file globale è un indice (<200 righe), mai un dump di documentazione.
  La documentazione profonda vive in file separati (come questo) letti su trigger deterministico.
- **CLI > MCP**: gli MCP caricano tutti i metodi nel context (costo costante); una CLI
  consuma ~zero token finché non eseguita. Es.: un MCP Gmail può occupare migliaia di token
  nel baseline, una CLI ~40. Audit MCP: `TOKEN-BASELINE.md`.

## 4. Advanced Efficiency

- **PDF-to-Text Hook**: leggere un PDF di 300 pagine da costi ~600k token in parsing visivo;
  un hook deterministico che estrae il testo lo riduce a ~150k (ROI 4x). Da implementare
  come hook su operazione di read (carta 4.1 del backlog).
- **Graph-Based Retrieval**: sopra la soglia di ~500 file, la ricerca "alla cieca" spreca
  token in letture ridondanti. Map-first con grafi (code graph / graphify) porta il modello
  dritto al nodo rilevante.

## 5. Model Selection

Vedi blocco "Model Selection Matrix" nell'indice. Regola economica: mai frontier per routine.
Mid-Session Switch Penalty: il cambio modello a conversazione in corso ricarica tutta la storia.

## 6. Golden Rule

AI per judgment, codice per esecuzione. Routine ripetitive judgment-free → script
Python/Bash deterministici: ripetibilità 100%, velocità massima, costo ricorrente zero.

## 7. Governance e Anti-pattern

Anti-pattern vietati (dettagli nell'indice): text screenshots, prompt poveri di contesto,
bloatware di efficienza.

### Checklist di audit periodico

1. **Script Conversion**: questo task judgment-free è migrabile a Python/Bash?
2. **Model Distillation**: questa routine si può abbassare di tier?
3. **Index Integrity**: i file globali restano sotto le 200 righe?
4. **Baseline Audit**: la sessione parte a 3-6%? Ci sono MCP/skill inutilizzati nel baseline?

### Stato di implementazione

| Carta | Stato |
|---|---|
| 0.1 Session Start Check | ✅ blocco indice |
| 0.2 Inventario MCP/skill | ✅ `TOKEN-BASELINE.md` |
| 1.1 Status Line | ✅ pi nativa; Claude Code via `scripts/statusline.py` |
| 1.2 Handoff File | ✅ skill `handoff` |
| 1.3 ASCII Prototyping | ✅ blocco indice |
| 2.1 Command Discipline | ✅ blocco indice |
| 2.2 Golden Rule + Anti-pattern | ✅ blocco indice |
| 2.3 Model Selection Matrix | ✅ blocco indice |
| 2.4 Audit Checklist | ✅ blocco indice + questo doc |
| 3.1 Nested Index refactor | da fare |
| 3.2 MCP → CLI (genimg) | da fare |
| 4.1 PDF-to-Text Hook | da fare |
| 4.2 Graph-Based Retrieval | da fare |
