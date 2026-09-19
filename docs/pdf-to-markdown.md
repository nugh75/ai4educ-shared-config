# PDF → Markdown per gli agenti

Carta 4.1: convertitore locale e hook di lettura, completati il 2026-09-19.
Il PDF resta la fonte; il Markdown è un derivato per leggere il testo senza
passare tutte le pagine a un modello visivo. Non viene eseguita una sintesi.

## Scelta del motore

Confronto documentale delle alternative richieste dal piano; non è un benchmark
comparativo di qualità o velocità:

| Libreria | Valutazione per questo uso |
|---|---|
| [PyMuPDF4LLM](https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/api.html) | Scelta: esportazione Markdown, titoli, stili, tabelle e segmentazione per pagina. Versione 1.28.2, modalità legacy con `use_layout(False)`: nessuna inferenza del layout e nessun OCR. |
| [Marker](https://github.com/datalab-to/marker) | Alternativa per conversioni con OCR e modelli; la configurazione corrente richiede ulteriori componenti di inferenza. Non necessario per il percorso leggero di lettura dei PDF con testo. |
| [Docling](https://docling-project.github.io/docling/usage/advanced_options/) | Alternativa con modello documentale più ampio, pipeline native e pipeline con modelli. Per questo strumento basta l'esportazione diretta offerta dal motore scelto. |

PyMuPDF4LLM installa anche il pacchetto layout e le sue dipendenze; la modalità
scelta non lo usa per inferenza. Nessuna chiamata a servizi o download durante
la conversione. Le dipendenze si scaricano durante l'installazione.

## Installazione e uso

Python 3.11 o successivo; launcher shell per Linux. Dalla root del repository:

```bash
uv venv .venv-pdf2md
uv pip install --python .venv-pdf2md/bin/python -r requirements/pdf2md.txt
./scripts/pdf2md documento.pdf
./scripts/pdf2md documento.pdf -o /tmp/documento.md
./scripts/pdf2md documento.pdf --pages 1-3,5 --stdout
```

Alternativa senza uv: `python3 -m venv .venv-pdf2md`, poi
`.venv-pdf2md/bin/python -m pip install -r requirements/pdf2md.txt`.
Per usare il comando da ogni progetto, collegare `~/bin/pdf2md` al launcher
`scripts/pdf2md` (non al file Python). La directory `~/bin` deve essere nel PATH.
Codex, pi e OpenCode possono invocare la stessa CLI attraverso il terminale.

- Default: scrive un `.md` accanto al PDF; `-o` sceglie un altro file Markdown.
  La directory di destinazione deve già esistere.
- `--stdout`: stampa solo il Markdown e non scrive file; incompatibile con `-o`.
- `--pages`: numeri 1-based e intervalli inclusivi, ordinati senza duplicati.
- `--force`: riconverte e permette di sostituire anche Markdown dell'autore.
  Non permette mai di sostituire il PDF o seguire un symlink di destinazione.
- La cache confronta SHA-256 del PDF, versioni del convertitore/motore, pagine
  richieste e integrità del Markdown. Le modifiche al PDF vengono rilevate anche
  se il timestamp non cambia. Una modifica manuale al Markdown blocca la
  sostituzione senza `--force`.
- Scrittura UTF-8 atomica; gli errori non lasciano un risultato parziale.
- Log e avvisi su stderr; codice 0 per successo/cache, nonzero per errore.

Il commento iniziale contiene la provenienza tecnica e l'hash del corpo;
`<!-- pagina N -->` conserva la numerazione del PDF. Questi commenti fanno
parte del derivato gestito: non eliminarli se si vuole riusare la cache.

## Hook Claude Code

Il modello di configurazione è `templates/pdf-read-hook.settings.json`.
Integrare la sua voce in `hooks.PreToolUse` di `~/.claude/settings.json`,
conservando eventuali altre voci e adattando il percorso al checkout locale.
L'hook usa soltanto la libreria standard Python.

Quando `Read` richiede un PDF, l'hook restituisce il comando per convertirlo
nella cache `~/.cache/pdf2md` (o `$XDG_CACHE_HOME/pdf2md`) e invita l'agente a
leggere il Markdown. L'agente esegue quel comando tramite il normale tool shell.
La selezione `pages` viene conservata. Non vengono creati derivati nel progetto.

L'hook non legge il PDF e non riscrive `file_path` prima dei controlli di accesso:
il protocollo [PreToolUse](https://code.claude.com/docs/en/hooks#pretooluse-decision-control)
applicherebbe i permessi al percorso modificato. Non restituisce approvazioni;
il comando di conversione attraversa i controlli del tool shell. Le chiamate
non PDF passano senza output. Questo è un instradamento alla CLI, non una
sostituzione invisibile del risultato del tool.

Per lettura visiva diretta avviare Claude con `PDF2MD_NATIVE_READ=1`, oppure
usare un tool di rendering delle pagine richieste. Per disinstallare l'hook,
rimuovere solo la relativa voce da `hooks.PreToolUse`. Riavviare la sessione
dell'agente dopo cambiamenti alla configurazione. Non si afferma che questo
protocollo sia un hook universale per Codex, pi o OpenCode.

## Limiti e verifiche

- PDF senza testo: errore con indicazione di OCR separato, nessun output salvato.
- PDF misti: avviso su stderr e segnaposto per ogni pagina priva di testo,
  anche quando il risultato viene letto dalla cache.
- PDF protetti da password o corrotti: errore senza sovrascrivere il Markdown.
- Figure, grafici, formule e parti scansionate dentro pagine che contengono
  anche testo non sono interpretati. La presenza di testo non prova che tutto
  il contenuto visivo sia stato recuperato.
- Titoli, tabelle e ordine di lettura sono ricostruiti: verificare il PDF per
  citazioni, impaginazioni complesse o informazioni contenute nelle immagini.
- Per pagina si confrontano le parole del Markdown con il testo nativo. Se
  ne viene conservato meno del 98%, si usa il testo nativo ordinato, rinunciando
  alla ricostruzione del layout. Le pagine sono elencate in `plain_text_pages`
  e segnalate su stderr. È un controllo di completezza lessicale, non una
  validazione semantica o della correttezza dell'OCR.
- Il risparmio di token dipende dal documento e dal lettore: nessuna garanzia
  quantitativa di riduzione 4×.

Test ripetibili senza rete:

```bash
.venv-pdf2md/bin/python -m unittest discover -s tests -v
bash -n scripts/pdf2md
git diff --check
```

La suite genera PDF reali per verificare struttura, cache, pagine selezionate,
protezione dei file, scansioni, cifratura, CLI e protocollo hook. Il test hook
esegue anche il comando restituito, inclusi nomi file con spazi e metacaratteri.
Non avvia una sessione LLM Claude.

Prova locale aggiuntiva: PDF accademico `savickas_2024_career_studies_self_making_life_designing.pdf`
del corpus CounselorBot, 3 pagine, 12.308 caratteri nativi, 12.749 caratteri
nel derivato con metadati, tre riferimenti pagina e cache riutilizzata. Il PDF
e il suo contenuto non sono inclusi in questo repository.
