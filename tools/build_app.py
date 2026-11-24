#!/usr/bin/env python3
"""Baut die App als eine einzige HTML-Datei: docs/index.html.

1. Zeichentabellen aus Python exportieren (web/tables.js)
2. web/app.html mit eingebetteten Skripten nach docs/index.html schreiben

    python3 tools/build_app.py
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "export_tables.py")], check=True)
    with open(os.path.join(ROOT, "web", "app.html"), encoding="utf-8") as fh:
        html = fh.read()

    def inline(m):
        name = m.group(1)
        with open(os.path.join(ROOT, "web", name), encoding="utf-8") as fh:
            code = fh.read()
        if "</script" in code:
            raise SystemExit("'</script' in %s" % name)
        return "<script>/* %s */\n%s\n</script>" % (name, code)

    out, n = re.subn(r'<script src="([a-z]+\.js)"></script>', inline, html)
    if n != 3:
        raise SystemExit("erwartet 3 Skripte, gefunden %d" % n)
    os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True)
    path = os.path.join(ROOT, "docs", "index.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(out)
    print("geschrieben:", path, len(out.encode("utf-8")), "Bytes")


if __name__ == "__main__":
    main()
