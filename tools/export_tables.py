#!/usr/bin/env python3
"""Exportiert die Zeichentabellen aus latex2unicode.py nach web/tables.js.

Die Tabellen werden nur in Python über unicodedata (offizielle Zeichennamen)
erzeugt. Die JavaScript-Fassung übernimmt sie unverändert, damit beide
Implementierungen dieselben Zeichen verwenden.
"""
import json
import os
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import latex2unicode as L  # noqa: E402


def styled_tables():
    chars = [chr(c) for c in range(0x41, 0x5B)] + [chr(c) for c in range(0x61, 0x7B)]
    chars += [str(d) for d in range(10)]
    greek = set(L.GREEK.values())
    greek |= {chr(c) for c in range(0x391, 0x3CA) if unicodedata.name(chr(c), "")}
    chars += sorted(greek)
    out = {}
    for style in L._STYLE_PREFIX:
        m = {}
        for ch in chars:
            s = L.styled(ch, style)
            if s != ch:
                m[ch] = s
        out[style] = m
    return out


def main():
    lookalike_names = {}
    for table in (L.SUP_LOOKALIKE, L.SUB_LOOKALIKE, L.SUB_Y_LOOKALIKE):
        for v in table.values():
            lookalike_names[v] = unicodedata.name(v)
    data = {
        "GREEK": L.GREEK,
        "SYMBOLS": {k: list(v) for k, v in L.SYMBOLS.items()},
        "CLASS_BY_CHAR": L._CLASS_BY_CHAR,
        "NEGATE": L.NEGATE,
        "OPNAMES": L.OPNAMES,
        "SPACES": L.SPACES,
        "ACCENTS": L.ACCENTS,
        "SPREAD_ACCENTS": sorted(L._SPREAD_ACCENTS),
        "STYLES": L.STYLES,
        "TEXTS": L.TEXTS,
        "FRACS": sorted(L.FRACS),
        "BIGS": sorted(L.BIGS),
        "ARITY": L.ARITY,
        "SUP": L.SUP,
        "SUB": L.SUB,
        "SUP_LOOKALIKE": L.SUP_LOOKALIKE,
        "SUB_LOOKALIKE": L.SUB_LOOKALIKE,
        "SUB_Y_LOOKALIKE": L.SUB_Y_LOOKALIKE,
        "SUB_UNICODE18": L.SUB_UNICODE18,
        "LOOKALIKE_NAMES": lookalike_names,
        "ROOTS": L.ROOTS,
        "VULGAR": {n + "/" + d: v for (n, d), v in L.VULGAR.items()},
        "STYLED": styled_tables(),
        "CHR_TABLE": {k: list(v) for k, v in L._CHR_TABLE.items()},
        "CONST": {"MINUS": L.MINUS, "PRIME": L.PRIME, "NBSP": L.NBSP,
                  "FRACTION_SLASH": L.FRACTION_SLASH, "NOT_OVERLAY": L.NOT_OVERLAY},
        "VERSION": L.__version__,
    }
    js = ("// Automatisch erzeugt von tools/export_tables.py – nicht von Hand ändern.\n"
          "const L2U_TABLES = " + json.dumps(data, ensure_ascii=True, indent=1, sort_keys=True) + ";\n"
          "if (typeof module !== 'undefined') module.exports = L2U_TABLES;\n")
    path = os.path.join(ROOT, "web", "tables.js")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(js)
    print("geschrieben:", path, len(js), "Bytes")


if __name__ == "__main__":
    main()
