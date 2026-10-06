"""Render Markdown files to PDF next to them, using the installed Chrome browser.

Usage (from literature-review/):  python scripts/md_to_pdf.py protocol.md search-log.md
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CSS = """
@page { size: A4; margin: 18mm 16mm; }
body { font-family: "Segoe UI", Arial, sans-serif; font-size: 10pt; line-height: 1.45; color: #1a1a1a; }
h1 { font-size: 18pt; margin: 0 0 8pt; }
h2 { font-size: 12.5pt; margin: 16pt 0 5pt; border-bottom: 1px solid #bbb; padding-bottom: 2pt; break-after: avoid; }
h3 { font-size: 10.5pt; margin: 12pt 0 4pt; break-after: avoid; }
p, ul, ol { margin: 5pt 0; }
table { border-collapse: collapse; width: 100%; margin: 6pt 0; font-size: 8.5pt; }
th, td { border: 1px solid #999; padding: 3pt 5pt; text-align: left; vertical-align: top; }
th { background: #eee; }
tr { break-inside: avoid; }
code { font-family: Consolas, monospace; font-size: 0.92em; overflow-wrap: anywhere; }
pre { background: #f4f4f4; border: 1px solid #ddd; padding: 5pt 7pt; white-space: pre-wrap; font-size: 8pt; }
"""


def main():
    for name in sys.argv[1:]:
        src = Path(name).resolve()
        body = markdown.markdown(src.read_text(encoding="utf-8"), extensions=["tables", "fenced_code", "nl2br"])
        html = src.with_suffix(".tmp.html")
        html.write_text(
            f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>{src.stem}</title>"
            f"<style>{CSS}</style></head><body>{body}</body></html>", encoding="utf-8")
        pdf = src.with_suffix(".pdf")
        pdf.unlink(missing_ok=True)
        # a throwaway profile keeps this run apart from any Chrome window already open
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as profile:
            subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                            f"--user-data-dir={profile}", f"--print-to-pdf={pdf}", html.as_uri()],
                           check=True, capture_output=True, timeout=120)
        html.unlink()
        if not pdf.exists():
            sys.exit(f"Chrome did not produce {pdf}")
        print(f"written {pdf}")


if __name__ == "__main__":
    main()
