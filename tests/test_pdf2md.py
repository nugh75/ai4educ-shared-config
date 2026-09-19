"""Behavioral checks with real PDFs, including CLI and native hook payloads."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import pdf2md
import pdf_read_hook


def make_pdf(path, *, text="Testo del documento", blank=False, mixed=False, password=False):
    with pymupdf.open() as doc:
        page = doc.new_page()
        if not blank:
            page.insert_text((50, 60), "Titolo principale", fontsize=22, fontname="hebo")
            page.insert_textbox((50, 90, 500, 160),
                                text + "\nUn paragrafo italiano: perché, qualità.\n"
                                "Seconda riga con testo da conservare.", fontsize=11)
            page.insert_text((50, 185), "Importante", fontsize=11, fontname="hebo")
            page.insert_text((50, 210), "Corsivo", fontsize=11, fontname="heit")
            page.insert_text((50, 240), "- Primo elemento\n- Secondo elemento", fontsize=11)
            for x in (50, 200, 350):
                page.draw_line((x, 300), (x, 390))
            for y in (300, 330, 360, 390):
                page.draw_line((50, y), (350, y))
            for x, y, word in [(60, 320, "Nome"), (210, 320, "Valore"),
                               (60, 350, "Alfa"), (210, 350, "10"),
                               (60, 380, "Beta"), (210, 380, "20")]:
                page.insert_text((x, y), word, fontsize=11)
        if blank or mixed:
            # An actual raster-only page, not just missing test fixture text.
            scan = page if blank else doc.new_page()
            pix = pymupdf.Pixmap(pymupdf.csRGB, (0, 0, 50, 50))
            pix.clear_with(220)
            scan.insert_image(scan.rect, pixmap=pix)
        if mixed:
            doc.new_page().insert_text((50, 60), "Solo terza pagina", fontsize=11)
        kwargs = dict(encryption=pymupdf.PDF_ENCRYPT_AES_256,
                      owner_pw="owner", user_pw="secret") if password else {}
        doc.save(path, **kwargs)


class ConversionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.pdf = self.root / "documento con spazi.pdf"
        self.md = self.pdf.with_suffix(".md")
        make_pdf(self.pdf)

    def cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT / "scripts/pdf2md.py"), *map(str, args)],
                              capture_output=True, text=True)

    def test_structure_and_utf8(self):
        text, cached = pdf2md.convert(self.pdf, self.md)
        self.assertFalse(cached)
        for part in ["# **Titolo principale**", "**Importante**", "_Corsivo_",
                     "- Primo elemento", "|Nome|Valore|", "|Alfa|10|", "perché, qualità",
                     "<!-- pagina 1 -->"]:
            self.assertIn(part, text)
        self.assertEqual(self.md.read_text(), text)

    def test_incomplete_layout_output_falls_back_to_complete_native_text(self):
        small = self.root / "small.pdf"
        with pymupdf.open() as doc:
            doc.new_page().insert_text((50, 60), "Testo piccolo da conservare integralmente", fontsize=2)
            doc.save(small)
        output = small.with_suffix(".md")
        warning = io.StringIO()
        with contextlib.redirect_stderr(warning), \
             patch("pymupdf4llm.to_markdown", return_value=[{"text": "Testo piccolo"}]):
            text, _ = pdf2md.convert(small, output)
            self.assertTrue(pdf2md.convert(small, output)[1])
        self.assertIn("Testo piccolo da conservare integralmente", text)
        self.assertEqual(pdf2md.metadata(output.read_bytes())["plain_text_pages"], [1])
        self.assertIn("struttura semplificata", warning.getvalue())

    def test_cache_hash_not_mtime_and_force(self):
        pdf2md.convert(self.pdf, self.md)
        before = self.md.stat().st_mtime_ns
        self.assertTrue(pdf2md.convert(self.pdf, self.md)[1])
        self.assertEqual(self.md.stat().st_mtime_ns, before)
        stamp = self.pdf.stat()
        replacement = self.root / "changed.pdf"
        make_pdf(replacement, text="Contenuto nuovo")
        replacement.replace(self.pdf)
        os.utime(self.pdf, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
        text, cached = pdf2md.convert(self.pdf, self.md)
        self.assertFalse(cached)
        self.assertIn("Contenuto nuovo", text)
        self.assertFalse(pdf2md.convert(self.pdf, self.md, force=True)[1])

    def test_preserves_authored_or_edited_markdown(self):
        self.md.write_text("Appunti dell'autore")
        with self.assertRaisesRegex(ValueError, "non gestito"):
            pdf2md.convert(self.pdf, self.md)
        self.assertEqual(self.md.read_text(), "Appunti dell'autore")
        pdf2md.convert(self.pdf, self.md, force=True)
        self.md.write_text(self.md.read_text() + "Modifica manuale")
        with self.assertRaisesRegex(ValueError, "modificato"):
            pdf2md.convert(self.pdf, self.md)
        self.assertTrue(self.md.read_text().endswith("Modifica manuale"))

    def test_symlink_and_source_alias_rejected_even_with_force(self):
        original = self.pdf.read_bytes()
        self.md.symlink_to(self.pdf)
        with self.assertRaises(ValueError):
            pdf2md.convert(self.pdf, self.md, force=True)
        self.md.unlink()
        os.link(self.pdf, self.md)
        with self.assertRaises(ValueError):
            pdf2md.convert(self.pdf, self.md, force=True)
        self.assertEqual(self.pdf.read_bytes(), original)
        with self.assertRaises(ValueError):
            pdf2md.convert(self.pdf, self.pdf, force=True)

    def test_mixed_pdf_warns_in_output_and_on_cache_hits(self):
        self.pdf.unlink()
        make_pdf(self.pdf, mixed=True)
        for _ in range(2):
            warning = io.StringIO()
            with contextlib.redirect_stderr(warning):
                text, _ = pdf2md.convert(self.pdf, self.md)
            self.assertIn("pagine senza testo estraibile", warning.getvalue())
            self.assertIn("pagina 2", text)
            self.assertIn("OCR non eseguito", text)
            self.assertIn("Solo terza pagina", text)

    def test_pages_are_selected_and_invalidate_cache(self):
        self.pdf.unlink()
        make_pdf(self.pdf, mixed=True)
        text, _ = pdf2md.convert(self.pdf, self.md, pages="3")
        self.assertIn("Solo terza pagina", text)
        self.assertNotIn("Titolo principale", text)
        self.assertEqual(pdf2md.metadata(self.md.read_bytes())["pages"], [3])
        text, cached = pdf2md.convert(self.pdf, self.md, pages="1")
        self.assertFalse(cached)
        self.assertIn("Titolo principale", text)
        self.assertNotIn("Solo terza pagina", text)

    def test_invalid_page_ranges(self):
        for value in ["0", "9", "2-1", "1,", "word", "-1", ""]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                pdf2md.convert(self.pdf, self.md, pages=value)
        self.assertFalse(self.md.exists())
        self.assertEqual(pdf2md.parse_pages("3,1-2,2", 3), [0, 1, 2])

    def test_scanned_encrypted_and_corrupt_preserve_output(self):
        self.md.write_text("Conservare")
        for kind in ["scan", "encrypted", "corrupt"]:
            with self.subTest(kind=kind):
                bad = self.root / f"{kind}.pdf"
                if kind == "corrupt":
                    bad.write_bytes(b"not a PDF")
                else:
                    make_pdf(bad, blank=kind == "scan", password=kind == "encrypted")
                result = self.cli(bad, "-o", self.md, "--force")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("errore:", result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(self.md.read_text(), "Conservare")

    def test_stdout_is_clean_and_does_not_write(self):
        result = self.cli(self.pdf, "--stdout")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.startswith(pdf2md.PREFIX))
        self.assertIsNotNone(pdf2md.metadata(result.stdout.encode()))
        self.assertFalse(self.md.exists())
        result = self.cli(self.pdf, "--stdout", "-o", self.md)
        self.assertNotEqual(result.returncode, 0)

    def test_atomic_write_detects_concurrent_changes(self):
        self.md.write_bytes(b"new author version")
        with self.assertRaisesRegex(ValueError, "durante"):
            pdf2md.atomic_write(self.md, b"replacement", b"old version")
        self.assertEqual(self.md.read_bytes(), b"new author version")
        self.assertFalse(list(self.root.glob(".pdf2md-*")))


class HookTests(unittest.TestCase):
    def event(self, name="paper.pdf", **params):
        return {"hook_event_name": "PreToolUse", "tool_name": "Read",
                "cwd": "/tmp/project", "tool_input": {"file_path": name, **params}}

    def test_pdf_requests_cli_without_reading_or_approving(self):
        with patch.dict(os.environ, {"PDF2MD_NATIVE_READ": "0"}), \
             patch.object(Path, "read_bytes", side_effect=AssertionError("unexpected read")):
            result = pdf_read_hook.response(self.event("missing paper.PDF", pages="2-4"))
        output = result["hookSpecificOutput"]
        self.assertEqual(output["permissionDecision"], "deny")
        self.assertNotIn("updatedInput", output)
        self.assertIn("--pages 2-4", output["permissionDecisionReason"])
        self.assertIn("missing paper.PDF", output["permissionDecisionReason"])

    def test_non_pdf_and_opt_out_pass_through(self):
        self.assertIsNone(pdf_read_hook.response(self.event("paper.md")))
        with patch.dict(os.environ, {"PDF2MD_NATIVE_READ": "1"}):
            self.assertIsNone(pdf_read_hook.response(self.event()))
        event = self.event()
        event["tool_name"] = "Write"
        self.assertIsNone(pdf_read_hook.response(event))

    def test_hook_json_and_shell_quoting_end_to_end(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pdf = root / "paper ' $(touch INJECTED).PDF"
            make_pdf(pdf)
            env = dict(os.environ, XDG_CACHE_HOME=str(root / "cache"), PDF2MD_NATIVE_READ="0")
            result = subprocess.run([sys.executable, str(ROOT / "scripts/pdf_read_hook.py")],
                                    input=json.dumps(self.event(str(pdf), pages="1")),
                                    capture_output=True, text=True, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            reason = json.loads(result.stdout)["hookSpecificOutput"]["permissionDecisionReason"]
            command = reason.split("file: ", 1)[1].split("\n", 1)[0]
            converted = subprocess.run(command, shell=True, cwd=root, env=env,
                                       capture_output=True, text=True)
            self.assertEqual(converted.returncode, 0, converted.stderr)
            markdown = list((root / "cache/pdf2md").glob("*.md"))
            self.assertEqual(len(markdown), 1)
            self.assertIn("Testo del documento", markdown[0].read_text())
            self.assertFalse((root / "INJECTED").exists())
            self.assertFalse(pdf.with_suffix(".md").exists())


if __name__ == "__main__":
    unittest.main()
