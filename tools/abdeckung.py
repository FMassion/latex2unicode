#!/usr/bin/env python3
"""Abdeckungsprüfung: alle Formeln einer Markdown-Datei umwandeln und bewerten.

    python3 tools/abdeckung.py DATEI.md

Schreibt
  ABDECKUNG.md        Bericht (Formel, Ergebnis, Status, Hinweis)
  tests/parity.json   Python-Ergebnisse als Referenz für den JavaScript-Test

Status
  OK       vollständig in Unicode umgesetzt
  Ersatz   umgesetzt mit Ersatzzeichen (z. B. ᵀ für ⊤)
  Grenze   Unicode hat das Zeichen nicht; Ersatzschreibweise x_(…) bzw. linear
  FEHLT    Befehl wird vom Modul nicht unterstützt
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from latex2unicode import convert  # noqa: E402


def extract(md):
    exprs = []

    def add(s):
        s = s.strip()
        if s and s not in exprs:
            exprs.append(s)

    for b in re.findall(r"\$\$(.+?)\$\$", md, re.S):
        add(" ".join(b.split()))
    rest = re.sub(r"\$\$(.+?)\$\$", "", md, flags=re.S)
    for line in rest.splitlines():
        for s in re.findall(r"(?<!\\)\$([^$]+?)(?<!\\)\$", line):
            add(s)
        for s in re.findall(r"`([^`]*\\[^`]*)`", line):
            for part in s.split("`, `"):
                add(part)
    return exprs


def status(warns):
    if any(w.startswith("Unbekannter Befehl") for w in warns):
        return "FEHLT"
    if any("nicht vollständig" in w or "nicht stapelbar" in w for w in warns):
        return "Grenze"
    if warns:
        return "Ersatz"
    return "OK"


def cell(s):
    return s.replace("|", "\\|").replace("\n", " ")


def main():
    if len(sys.argv) < 2:
        raise SystemExit("Aufruf: python3 tools/abdeckung.py DATEI.md")
    src = sys.argv[1]
    with open(src, encoding="utf-8") as fh:
        exprs = extract(fh.read())
    rows, parity = [], []
    for e in exprs:
        w = []
        out = convert(e, warnings=w)
        rows.append((e, out, status(w), w))
        parity.append({"in": e, "out": out, "warnings": w})
    counts = {}
    for r in rows:
        counts[r[2]] = counts.get(r[2], 0) + 1
    order = {"FEHLT": 0, "Grenze": 1, "Ersatz": 2, "OK": 3}
    lines = [
        "# Abdeckungsbericht",
        "",
        "Quelle: `%s` (%d verschiedene Formeln und LaTeX-Befehle)." % (os.path.basename(src), len(rows)),
        "Erzeugt mit `python3 tools/abdeckung.py`.",
        "",
        "| Status | Anzahl | Bedeutung |",
        "|---|---|---|",
        "| OK | %d | vollständig in Unicode umgesetzt |" % counts.get("OK", 0),
        "| Ersatz | %d | umgesetzt mit Ersatzzeichen (ᵀ für ⊤, * für ∗) |" % counts.get("Ersatz", 0),
        "| Grenze | %d | Unicode hat das Hoch-/Tiefzeichen nicht; Ersatzschreibweise. Im Bild-Export der App als echte Hoch-/Tiefstellung bzw. gestapelt dargestellt |" % counts.get("Grenze", 0),
        "| FEHLT | %d | Befehl nicht unterstützt |" % counts.get("FEHLT", 0),
        "",
        "## Einzelergebnisse (FEHLT und Grenze zuerst)",
        "",
        "| Status | LaTeX | Unicode-Ergebnis | Hinweis |",
        "|---|---|---|---|",
    ]
    for e, out, st, w in sorted(rows, key=lambda r: order[r[2]]):
        lines.append("| %s | `%s` | %s | %s |" % (st, cell(e), cell(out), cell("; ".join(w))))
    with open(os.path.join(ROOT, "ABDECKUNG.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    with open(os.path.join(ROOT, "tests", "parity.json"), "w", encoding="utf-8") as fh:
        json.dump(parity, fh, ensure_ascii=False, indent=0)
    print(len(rows), "Formeln:", counts)
    return 1 if counts.get("FEHLT") else 0


if __name__ == "__main__":
    sys.exit(main())
