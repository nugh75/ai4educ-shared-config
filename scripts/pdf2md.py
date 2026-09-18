#!/usr/bin/env python3
"""pdf2md — converte PDF in Markdown preservando struttura (Token Optimization 4.1).

Preserva: capitoli/titoli (da dimensioni font relativamente al corpo), grassello,
corsivo, elenchi puntati/numerati, paragrafi. ROI ~4x vs lettura visiva del PDF.

Uso:
    pdf2md file.pdf                 # crea file.md accanto al PDF (se assente o datato)
    pdf2md file.pdf -o out.md       # destinazione esplicita
    pdf2md file.pdf --force         # riconverte anche se il .md è aggiornato
    pdf2md file.pdf --stdout        # stampa a video senza salvare
"""
import argparse
import os
import statistics
import sys

import pymupdf  # fitz deprecato

BULLET_PREFIXES = ("•", "●", "▪", "◦", "‣", "·", "○", "■", "□")


def span_flags(span):
    """Ritorna (bold, italic) da un span PyMuPDF."""
    f = span.get("flags", 0)
    font = span.get("font", "").lower()
    bold = bool(f & 16) or "bold" in font or "black" in font
    italic = bool(f & 2) or "italic" in font or "oblique" in font
    return bold, italic


def line_to_markdown(line, body_size):
    """Converte una riga (lista di span) in markdown con inline bold/italic."""
    parts = []
    for span in line:
        text = span["text"]
        if not text.strip():
            if parts:
                parts.append(" ")
            continue
        bold, italic = span_flags(span)
        if bold and italic:
            text = f"***{text.strip()}***"
        elif bold:
            text = f"**{text.strip()}**"
        elif italic:
            text = f"*{text.strip()}*"
        parts.append(text)
    return "".join(parts).strip()


def heading_level(size, bold, body_size, max_size):
    """Livello di titolo in base al rapporto fra dimensione font e corpo."""
    if size >= max_size - 0.5:
        return 1
    ratio = size / body_size
    if ratio >= 1.5:
        return 2
    if ratio >= 1.2 and bold:
        return 3
    return 0


def pdf_to_markdown(path):
    doc = pymupdf.open(path)
    all_sizes = []
    pages_lines = []  # per pagina: lista di (block_id, [righe markdown], primo_span)
    for page in doc:
        blocks = page.get_text("dict", sort=True)["blocks"]
        page_data = []
        for b in blocks:
            if b.get("type") != 0:
                continue
            block_lines = []
            for line in b["lines"]:
                spans = [s for s in line["spans"] if s["text"].strip()]
                if not spans:
                    continue
                block_lines.append(spans)
                all_sizes.extend(s["size"] for s in spans)
            if block_lines:
                page_data.append((b["number"], block_lines))
        pages_lines.append(page_data)

    if not all_sizes:
        return ""
    body_size = statistics.median(all_sizes)
    max_size = max(all_sizes)

    out = []
    for page_data in pages_lines:
        for _block_id, block_lines in page_data:
            # dimensione media e bold della riga per riconoscere i titoli
            first_spans = block_lines[0]
            line_size = statistics.mean(s["size"] for s in first_spans)
            line_bold = all(s.get("flags", 0) & 16 for s in first_spans)
            md_lines = [line_to_markdown(l, body_size) for l in block_lines]
            text = " ".join(md_lines).replace("  ", " ").strip()
            if not text:
                continue

            level = heading_level(line_size, line_bold, body_size, max_size)
            raw = "".join(s["text"] for s in first_spans).strip()
            is_list = raw.startswith(BULLET_PREFIXES) or (
                len(raw) > 2 and raw[0].isdigit() and raw[1] in ".)")
            if level and len(text) < 120:
                out.append(f"\n{'#' * level} {text.lstrip('# ')}\n")
            elif is_list:
                out.append(f"- {text.lstrip(''.join(BULLET_PREFIXES) + ' ')}")
            else:
                out.append(f"\n{text}\n")

    title = os.path.basename(path)
    header = (f"<!-- Convertito da {title} ({doc.page_count} pagine) con pdf2md -->\n\n"
              f"# {os.path.splitext(title)[0]}\n")
    doc.close()
    return header + "\n".join(out) + "\n"


def main():
    p = argparse.ArgumentParser(description="PDF → Markdown (capitoli, grassello, corsivo).")
    p.add_argument("pdf", help="file PDF di input")
    p.add_argument("-o", "--output", help="file .md di destinazione (default: accanto al PDF)")
    p.add_argument("--force", action="store_true", help="riconverte anche se il .md esiste ed è aggiornato")
    p.add_argument("--stdout", action="store_true", help="stampa il markdown invece di salvarlo")
    args = p.parse_args()

    pdf = os.path.abspath(args.pdf)
    if not os.path.exists(pdf):
        sys.exit(f"errore: {pdf} non trovato")
    md_path = args.output or os.path.splitext(pdf)[0] + ".md"

    fresh = (os.path.exists(md_path)
             and os.path.getmtime(md_path) >= os.path.getmtime(pdf))
    if fresh and not args.force and not args.stdout:
        print(f"ok: {md_path} già aggiornato", file=sys.stderr)
        return

    md = pdf_to_markdown(pdf)
    if not md:
        sys.exit("errore: nessun testo estratto (PDF scansionato? serve OCR)")
    if args.stdout:
        print(md)
    else:
        with open(md_path, "w") as f:
            f.write(md)
        print(f"ok: {md_path} ({os.path.getsize(md_path) // 1024} KB)", file=sys.stderr)


if __name__ == "__main__":
    main()
