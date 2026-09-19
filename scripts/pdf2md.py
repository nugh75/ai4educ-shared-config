#!/usr/bin/env python3
"""Convert local, text-based PDFs to Markdown without OCR or network calls."""
import argparse
from collections import Counter
import contextlib
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import sys
import tempfile

VERSION = "2"
PREFIX = "<!-- pdf2md "


def digest(data):
    return hashlib.sha256(data).hexdigest()


def retained_words(native, markdown):
    def words(text):
        text = re.sub(r"-\s*\n\s*", "", text.lower())
        return Counter(re.findall(r"[^\W_]{3,}", text))
    expected = words(native)
    return sum((expected & words(markdown)).values()) / max(1, sum(expected.values()))


def parse_pages(value, count):
    """Accept one-based pages/ranges; return sorted, unique zero-based indices."""
    if value is None:
        return list(range(count))
    selected = set()
    for part in value.split(","):
        match = re.fullmatch(r"\s*(\d+)(?:\s*-\s*(\d+))?\s*", part)
        if not match:
            raise ValueError("pagine non valide: usa ad esempio 1-3,5")
        start = int(match[1])
        end = int(match[2] or match[1])
        if not 1 <= start <= end <= count:
            raise ValueError(f"intervallo pagine fuori limite (1-{count}): {part}")
        selected.update(range(start - 1, end))
    return sorted(selected)


def existing_output(path):
    """Never follow output symlinks, including dangling ones."""
    if path.is_symlink():
        raise ValueError(f"destinazione symlink non consentita: {path}")
    return path.read_bytes() if path.exists() else None


def metadata(content):
    if content is None:
        return None
    try:
        first, body = content.decode("utf-8").split("\n", 1)
        if not first.startswith(PREFIX) or not first.endswith(" -->"):
            return None
        value = json.loads(first[len(PREFIX):-4])
        if not isinstance(value, dict) or value.get("body_sha256") != digest(body.encode()):
            return None
        return value
    except (ValueError, UnicodeError):
        return None


def atomic_write(path, content, previous):
    """Publish a complete file; refuse an output changed during conversion."""
    fd, temp = tempfile.mkstemp(prefix=".pdf2md-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        if existing_output(path) != previous:
            raise ValueError("destinazione modificata durante la conversione; riprova")
        if previous is None:
            os.link(temp, path)
        else:
            os.replace(temp, path)
    finally:
        Path(temp).unlink(missing_ok=True)


def convert(source, output=None, *, pages=None, force=False):
    """Return (Markdown, cache_hit); output=None performs no filesystem writes."""
    source = Path(source).expanduser().resolve(strict=True)
    if source.suffix.lower() != ".pdf":
        raise ValueError("la sorgente deve essere un file PDF")
    previous = None
    if output is not None:
        output = Path(output).expanduser().absolute()
        if output.suffix.lower() != ".md":
            raise ValueError("la destinazione deve avere estensione .md")
        if output.resolve() == source or (output.exists() and output.samefile(source)):
            raise ValueError("la destinazione coincide con il PDF sorgente")
        previous = existing_output(output)
        if previous is not None and metadata(previous) is None and not force:
            raise ValueError("Markdown esistente non gestito o modificato: scegli -o oppure --force")

    # Native libraries must not pollute --stdout or the hook's JSON protocol.
    with contextlib.redirect_stdout(sys.stderr):
        try:
            import pymupdf
            import pymupdf4llm
        except ImportError as exc:
            raise ValueError("dipendenze mancanti: installa requirements/pdf2md.txt nella venv") from exc
        pymupdf4llm.use_layout(False)
        data = source.read_bytes()
        with pymupdf.open(stream=data, filetype="pdf") as doc:
            if not doc.is_pdf:
                raise ValueError("il file non contiene un PDF valido")
            if doc.needs_pass:
                raise ValueError("PDF protetto da password: fornisci una copia sbloccata")
            selected = parse_pages(pages, doc.page_count)
            identity = {
                "version": VERSION,
                "engine": importlib.metadata.version("pymupdf4llm"),
                "pymupdf": importlib.metadata.version("pymupdf"),
                "source_sha256": digest(data),
                "pages": [p + 1 for p in selected],
            }
            saved = metadata(previous)
            if not force and saved and all(saved.get(k) == v for k, v in identity.items()):
                warn_missing(saved.get("textless_pages", []))
                warn_plain(saved.get("plain_text_pages", []))
                return previous.decode("utf-8"), True
            textless = [p + 1 for p in selected if not doc[p].get_text().strip()]
            if len(textless) == len(selected):
                raise ValueError("nessun testo estraibile: PDF vuoto o scansionato; serve OCR separato")
            chunks = pymupdf4llm.to_markdown(
                doc, pages=selected, page_chunks=True, show_progress=False,
                # Legacy extraction has no OCR; use_ocr only applies to layout mode.
                write_images=False, embed_images=False, margins=0,
            )
            sections = []
            plain_pages = []
            for page, chunk in zip(selected, chunks, strict=True):
                text = chunk["text"].strip()
                native = doc[page].get_text("text", sort=True).strip()
                # Some PDFs lose text in layout reconstruction (OCR layers,
                # tiny fonts, overlays). Prefer complete text over layout.
                if native and (not text or retained_words(native, text) < 0.98):
                    text = native
                    plain_pages.append(page + 1)
                if page + 1 in textless or not text:
                    if page + 1 not in textless:
                        textless.append(page + 1)
                    text = "[Nessun testo estraibile: pagina vuota o scansione; OCR non eseguito.]"
                sections.append(f"<!-- pagina {page + 1} -->\n\n{text}\n")
            if len(textless) == len(selected):
                raise ValueError("la conversione non ha prodotto testo; verifica il PDF")
            body = "\n" + "\n".join(sections)
            identity.update(body_sha256=digest(body.encode()), textless_pages=sorted(textless),
                            plain_text_pages=plain_pages)
            markdown = PREFIX + json.dumps(identity, sort_keys=True) + " -->\n" + body
    warn_missing(textless)
    warn_plain(plain_pages)
    if output is not None:
        atomic_write(output, markdown.encode("utf-8"), previous)
    return markdown, False


def warn_missing(pages):
    if pages:
        print("avviso: pagine senza testo estraibile (OCR non eseguito): " +
              ", ".join(map(str, pages)), file=sys.stderr)


def warn_plain(pages):
    if pages:
        print("avviso: struttura semplificata per conservare il testo, pagine: " +
              ", ".join(map(str, pages)), file=sys.stderr)


def main(argv=None):
    parser = argparse.ArgumentParser(description="PDF → Markdown locale, senza OCR.")
    parser.add_argument("pdf", type=Path)
    target = parser.add_mutually_exclusive_group()
    target.add_argument("-o", "--output", type=Path)
    target.add_argument("--stdout", action="store_true")
    parser.add_argument("--pages", help="pagine 1-based: ad esempio 1-3,5")
    parser.add_argument("--force", action="store_true", help="riconverte e autorizza la sostituzione del Markdown")
    args = parser.parse_args(argv)
    output = None if args.stdout else (args.output or args.pdf.with_suffix(".md"))
    try:
        markdown, cached = convert(args.pdf, output, pages=args.pages, force=args.force)
        if args.stdout:
            sys.stdout.write(markdown)
        else:
            print(f"ok: {output} ({'cache valida' if cached else 'convertito'})", file=sys.stderr)
        return 0
    except Exception as exc:
        print(f"errore: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
