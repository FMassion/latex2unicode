# -*- coding: utf-8 -*-
"""Tests der Python-Fassung. Aufruf im Repository-Verzeichnis:
    python3 -m unittest discover -s tests -v
"""
import json
import os
import sys
import unicodedata
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from latex2unicode import SUB, SUB_UNICODE18, SUP, convert, convert_text, styled  # noqa: E402

OPT_MAP = {"greekItalic": "greek_italic"}


class Testfaelle(unittest.TestCase):
    """Gemeinsame Testfälle (tests/cases.json), dieselben wie für JavaScript."""

    def test_cases(self):
        with open(os.path.join(HERE, "cases.json"), encoding="utf-8") as fh:
            cases = json.load(fh)
        for case in cases:
            kw = {OPT_MAP.get(k, k): v for k, v in case.get("opts", {}).items()}
            warns = []
            if "text" in case:
                out = convert_text(case["text"], warnings=warns, **kw)
                src = case["text"]
            else:
                out = convert(case["in"], warnings=warns, **kw)
                src = case["in"]
            with self.subTest(src=src, opts=kw):
                self.assertEqual(out, case["out"])
                if "warn" in case:
                    self.assertEqual(bool(warns), case["warn"], warns)


class Zeichentabellen(unittest.TestCase):
    """Prüft die erzeugten Zeichen gegen die Unicode-Datenbank."""

    def test_hochzeichen(self):
        for k, v in SUP.items():
            if k in "′″":
                continue
            n = unicodedata.name(v)
            self.assertTrue("SUPERSCRIPT" in n or "MODIFIER LETTER" in n, (k, n))

    def test_tiefzeichen(self):
        for k, v in SUB.items():
            self.assertIn("SUBSCRIPT", unicodedata.name(v), k)

    def test_kein_tiefgestelltes_y(self):
        self.assertNotIn("y", SUB)

    def test_unicode18(self):
        # U+209D–U+209F: in Unicode 18.0 zugewiesen; ältere unicodedata-Versionen kennen sie nicht
        self.assertEqual([ord(c) for c in SUB_UNICODE18.values()], [0x209D, 0x209E, 0x209F])
        try:
            self.assertEqual(unicodedata.name("\u209E"), "LATIN SUBSCRIPT SMALL LETTER Y")
        except ValueError:
            pass  # Python-Version mit Unicode < 18.0

    def test_luecken(self):
        self.assertEqual(styled("h", "italic"), "ℎ")   # PLANCK CONSTANT
        self.assertEqual(styled("C", "bb"), "ℂ")       # DOUBLE-STRUCK CAPITAL C
        self.assertEqual(styled("B", "cal"), "ℬ")      # SCRIPT CAPITAL B
        self.assertEqual(styled("R", "frak"), "ℜ")     # BLACK-LETTER CAPITAL R
        self.assertEqual(styled("s", "italic"), "\U0001D460")


if __name__ == "__main__":
    unittest.main()
