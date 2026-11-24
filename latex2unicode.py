#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
latex2unicode – LaTeX-ähnliche Formeln in Unicode-Klartext umwandeln.

Zweck: Formeln in Umgebungen ohne Formelsatz (LinkedIn-Beiträge und
-Kommentare, E-Mail, Chat, Klartextdokumente) so schreiben, dass das
Ergebnis dem LaTeX-Satzbild möglichst nahekommt.

    >>> convert(r"s_t \in S_{phys} \times S_{non-phys}")
    '𝑠ₜ ∈ 𝑆ₚₕᵧₛ × 𝑆ₙₒₙ₋ₚₕᵧₛ'

Grundprinzipien
  * Einzelne lateinische Buchstaben werden – wie in LaTeX – kursiv gesetzt
    (Unicode-Block "Mathematical Alphanumeric Symbols", U+1D400 ff.).
  * Hoch-/Tiefstellungen werden nur dann in Unicode-Hoch-/Tiefzeichen
    umgesetzt, wenn ALLE Zeichen verfügbar sind. Sonst Ersatzschreibweise
    x_(…) bzw. x^(…) plus Hinweis.
  * Abstände um Relationen (=, ∈, ≤ …) und binäre Operatoren (+, ×, …)
    werden nach den TeX-Regeln vereinfacht gesetzt; Leerzeichen in der
    Eingabe sind (wie in LaTeX) bedeutungslos.
  * Alle Sonderzeichen werden über ihre offiziellen Unicode-Namen
    (unicodedata.lookup) erzeugt – ein Tippfehler im Namen führt beim
    Import zu einem Fehler statt zu einem falschen Zeichen.

Nur Standardbibliothek, Python ≥ 3.8.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from functools import lru_cache

__all__ = ["convert", "convert_text"]
__version__ = "1.2.0"

_u = unicodedata.lookup

# Atomklassen (vereinfachte TeX-Klassen)
O, OP, B, R, OPEN, CLOSE, P, SP = "ord", "op", "bin", "rel", "open", "close", "punct", "space"

MINUS = _u("MINUS SIGN")
PRIME = _u("PRIME")
NBSP = _u("NO-BREAK SPACE")
FRACTION_SLASH = _u("FRACTION SLASH")
NOT_OVERLAY = _u("COMBINING LONG SOLIDUS OVERLAY")

# --------------------------------------------------------------------------
# Griechische Buchstaben
# --------------------------------------------------------------------------
_GREEK_SPEC = {
    "alpha": "GREEK SMALL LETTER ALPHA", "beta": "GREEK SMALL LETTER BETA",
    "gamma": "GREEK SMALL LETTER GAMMA", "delta": "GREEK SMALL LETTER DELTA",
    "epsilon": "GREEK LUNATE EPSILON SYMBOL", "varepsilon": "GREEK SMALL LETTER EPSILON",
    "zeta": "GREEK SMALL LETTER ZETA", "eta": "GREEK SMALL LETTER ETA",
    "theta": "GREEK SMALL LETTER THETA", "vartheta": "GREEK THETA SYMBOL",
    "iota": "GREEK SMALL LETTER IOTA", "kappa": "GREEK SMALL LETTER KAPPA",
    "lambda": "GREEK SMALL LETTER LAMDA", "mu": "GREEK SMALL LETTER MU",
    "nu": "GREEK SMALL LETTER NU", "xi": "GREEK SMALL LETTER XI",
    "omicron": "GREEK SMALL LETTER OMICRON", "pi": "GREEK SMALL LETTER PI",
    "varpi": "GREEK PI SYMBOL", "rho": "GREEK SMALL LETTER RHO",
    "varrho": "GREEK RHO SYMBOL", "sigma": "GREEK SMALL LETTER SIGMA",
    "varsigma": "GREEK SMALL LETTER FINAL SIGMA", "tau": "GREEK SMALL LETTER TAU",
    "upsilon": "GREEK SMALL LETTER UPSILON", "phi": "GREEK PHI SYMBOL",
    "varphi": "GREEK SMALL LETTER PHI", "chi": "GREEK SMALL LETTER CHI",
    "psi": "GREEK SMALL LETTER PSI", "omega": "GREEK SMALL LETTER OMEGA",
    "Gamma": "GREEK CAPITAL LETTER GAMMA", "Delta": "GREEK CAPITAL LETTER DELTA",
    "Theta": "GREEK CAPITAL LETTER THETA", "Lambda": "GREEK CAPITAL LETTER LAMDA",
    "Xi": "GREEK CAPITAL LETTER XI", "Pi": "GREEK CAPITAL LETTER PI",
    "Sigma": "GREEK CAPITAL LETTER SIGMA", "Upsilon": "GREEK CAPITAL LETTER UPSILON",
    "Phi": "GREEK CAPITAL LETTER PHI", "Psi": "GREEK CAPITAL LETTER PSI",
    "Omega": "GREEK CAPITAL LETTER OMEGA",
}
GREEK = {k: _u(v) for k, v in _GREEK_SPEC.items()}

# --------------------------------------------------------------------------
# Symbole: LaTeX-Befehl -> (Unicode-Name, Klasse)
# --------------------------------------------------------------------------
_SYM_SPEC = {
    # Relationen
    "in": ("ELEMENT OF", R), "notin": ("NOT AN ELEMENT OF", R), "ni": ("CONTAINS AS MEMBER", R),
    "leq": ("LESS-THAN OR EQUAL TO", R), "le": ("LESS-THAN OR EQUAL TO", R),
    "geq": ("GREATER-THAN OR EQUAL TO", R), "ge": ("GREATER-THAN OR EQUAL TO", R),
    "neq": ("NOT EQUAL TO", R), "ne": ("NOT EQUAL TO", R),
    "approx": ("ALMOST EQUAL TO", R), "equiv": ("IDENTICAL TO", R),
    "sim": ("TILDE OPERATOR", R), "simeq": ("ASYMPTOTICALLY EQUAL TO", R),
    "cong": ("APPROXIMATELY EQUAL TO", R), "propto": ("PROPORTIONAL TO", R),
    "ll": ("MUCH LESS-THAN", R), "gg": ("MUCH GREATER-THAN", R),
    "prec": ("PRECEDES", R), "succ": ("SUCCEEDS", R),
    "subset": ("SUBSET OF", R), "supset": ("SUPERSET OF", R),
    "subseteq": ("SUBSET OF OR EQUAL TO", R), "supseteq": ("SUPERSET OF OR EQUAL TO", R),
    "subsetneq": ("SUBSET OF WITH NOT EQUAL TO", R),
    "to": ("RIGHTWARDS ARROW", R), "rightarrow": ("RIGHTWARDS ARROW", R),
    "gets": ("LEFTWARDS ARROW", R), "leftarrow": ("LEFTWARDS ARROW", R),
    "leftrightarrow": ("LEFT RIGHT ARROW", R),
    "Rightarrow": ("RIGHTWARDS DOUBLE ARROW", R), "Leftarrow": ("LEFTWARDS DOUBLE ARROW", R),
    "Leftrightarrow": ("LEFT RIGHT DOUBLE ARROW", R),
    "implies": ("LONG RIGHTWARDS DOUBLE ARROW", R), "iff": ("LONG LEFT RIGHT DOUBLE ARROW", R),
    "longrightarrow": ("LONG RIGHTWARDS ARROW", R), "mapsto": ("RIGHTWARDS ARROW FROM BAR", R),
    "uparrow": ("UPWARDS ARROW", R), "downarrow": ("DOWNWARDS ARROW", R),
    "mid": ("DIVIDES", R), "parallel": ("PARALLEL TO", R), "perp": ("UP TACK", R),
    "vdash": ("RIGHT TACK", R), "models": ("TRUE", R),
    "coloneqq": ("COLON EQUALS", R), "triangleq": ("DELTA EQUAL TO", R),
    "doteq": ("APPROACHES THE LIMIT", R), "asymp": ("EQUIVALENT TO", R),
    "therefore": ("THEREFORE", R), "because": ("BECAUSE", R),
    "hookrightarrow": ("RIGHTWARDS ARROW WITH HOOK", R),
    "hookleftarrow": ("LEFTWARDS ARROW WITH HOOK", R),
    "twoheadrightarrow": ("RIGHTWARDS TWO HEADED ARROW", R),
    "rightsquigarrow": ("RIGHTWARDS SQUIGGLE ARROW", R), "leadsto": ("RIGHTWARDS SQUIGGLE ARROW", R),
    "longleftarrow": ("LONG LEFTWARDS ARROW", R), "longleftrightarrow": ("LONG LEFT RIGHT ARROW", R),
    "Longrightarrow": ("LONG RIGHTWARDS DOUBLE ARROW", R),
    "Longleftrightarrow": ("LONG LEFT RIGHT DOUBLE ARROW", R),
    "longmapsto": ("LONG RIGHTWARDS ARROW FROM BAR", R),
    # Verneinte Relationen (amssymb)
    "nsim": ("NOT TILDE", R), "ncong": ("NEITHER APPROXIMATELY NOR ACTUALLY EQUAL TO", R),
    "nless": ("NOT LESS-THAN", R), "ngtr": ("NOT GREATER-THAN", R),
    "nleq": ("NEITHER LESS-THAN NOR EQUAL TO", R), "ngeq": ("NEITHER GREATER-THAN NOR EQUAL TO", R),
    "nsubseteq": ("NEITHER A SUBSET OF NOR EQUAL TO", R),
    "nsupseteq": ("NEITHER A SUPERSET OF NOR EQUAL TO", R),
    "nmid": ("DOES NOT DIVIDE", R), "nparallel": ("NOT PARALLEL TO", R),
    "nrightarrow": ("RIGHTWARDS ARROW WITH STROKE", R), "nleftarrow": ("LEFTWARDS ARROW WITH STROKE", R),
    "nleftrightarrow": ("LEFT RIGHT ARROW WITH STROKE", R),
    "nRightarrow": ("RIGHTWARDS DOUBLE ARROW WITH STROKE", R),
    "nLeftarrow": ("LEFTWARDS DOUBLE ARROW WITH STROKE", R),
    "nLeftrightarrow": ("LEFT RIGHT DOUBLE ARROW WITH STROKE", R),
    "nvdash": ("DOES NOT PROVE", R), "nvDash": ("NOT TRUE", R), "nVdash": ("DOES NOT FORCE", R),
    # Binäre Operatoren
    "times": ("MULTIPLICATION SIGN", B), "cdot": ("DOT OPERATOR", B),
    "pm": ("PLUS-MINUS SIGN", B), "mp": ("MINUS-OR-PLUS SIGN", B),
    "div": ("DIVISION SIGN", B), "ast": ("ASTERISK OPERATOR", B),
    "star": ("STAR OPERATOR", B), "circ": ("RING OPERATOR", B),
    "bullet": ("BULLET OPERATOR", B), "cup": ("UNION", B), "cap": ("INTERSECTION", B),
    "setminus": ("SET MINUS", B), "wedge": ("LOGICAL AND", B), "land": ("LOGICAL AND", B),
    "vee": ("LOGICAL OR", B), "lor": ("LOGICAL OR", B),
    "oplus": ("CIRCLED PLUS", B), "otimes": ("CIRCLED TIMES", B),
    "odot": ("CIRCLED DOT OPERATOR", B), "sqcup": ("SQUARE CUP", B), "uplus": ("MULTISET UNION", B),
    # Große Operatoren
    "sum": ("N-ARY SUMMATION", OP), "prod": ("N-ARY PRODUCT", OP),
    "coprod": ("N-ARY COPRODUCT", OP), "int": ("INTEGRAL", OP),
    "iint": ("DOUBLE INTEGRAL", OP), "iiint": ("TRIPLE INTEGRAL", OP),
    "oint": ("CONTOUR INTEGRAL", OP), "bigcup": ("N-ARY UNION", OP),
    "bigcap": ("N-ARY INTERSECTION", OP), "bigvee": ("N-ARY LOGICAL OR", OP),
    "bigwedge": ("N-ARY LOGICAL AND", OP), "bigoplus": ("N-ARY CIRCLED PLUS OPERATOR", OP),
    "bigotimes": ("N-ARY CIRCLED TIMES OPERATOR", OP),
    # Gewöhnliche Symbole
    "infty": ("INFINITY", O), "partial": ("PARTIAL DIFFERENTIAL", O), "nabla": ("NABLA", O),
    "forall": ("FOR ALL", O), "exists": ("THERE EXISTS", O), "nexists": ("THERE DOES NOT EXIST", O),
    "neg": ("NOT SIGN", O), "lnot": ("NOT SIGN", O),
    "emptyset": ("EMPTY SET", O), "varnothing": ("EMPTY SET", O),
    "ell": ("SCRIPT SMALL L", O), "hbar": ("PLANCK CONSTANT OVER TWO PI", O),
    "aleph": ("ALEF SYMBOL", O), "Re": ("BLACK-LETTER CAPITAL R", O),
    "Im": ("BLACK-LETTER CAPITAL I", O), "wp": ("SCRIPT CAPITAL P", O),
    "top": ("DOWN TACK", O), "bot": ("UP TACK", O), "angle": ("ANGLE", O),
    "triangle": ("WHITE UP-POINTING TRIANGLE", O), "prime": ("PRIME", O),
    "degree": ("DEGREE SIGN", O), "ldots": ("HORIZONTAL ELLIPSIS", O),
    "dots": ("HORIZONTAL ELLIPSIS", O), "cdots": ("MIDLINE HORIZONTAL ELLIPSIS", O),
    "vdots": ("VERTICAL ELLIPSIS", O), "ddots": ("DOWN RIGHT DIAGONAL ELLIPSIS", O),
    "Vert": ("DOUBLE VERTICAL LINE", O), "|": ("DOUBLE VERTICAL LINE", O),
    "vert": ("VERTICAL LINE", O), "checkmark": ("CHECK MARK", O), "Box": ("WHITE SQUARE", O),
    "_": ("LOW LINE", O), "%": ("PERCENT SIGN", O), "&": ("AMPERSAND", O),
    "#": ("NUMBER SIGN", O), "$": ("DOLLAR SIGN", O),
    "square": ("WHITE SQUARE", O), "blacksquare": ("BLACK SQUARE", O),
    "qed": ("BLACK SQUARE", O), "complement": ("COMPLEMENT", O),
    "dagger": ("DAGGER", B), "ddagger": ("DOUBLE DAGGER", B),
    # Begrenzer
    "lvert": ("VERTICAL LINE", OPEN), "rvert": ("VERTICAL LINE", CLOSE),
    "lVert": ("DOUBLE VERTICAL LINE", OPEN), "rVert": ("DOUBLE VERTICAL LINE", CLOSE),
    "langle": ("MATHEMATICAL LEFT ANGLE BRACKET", OPEN), "rangle": ("MATHEMATICAL RIGHT ANGLE BRACKET", CLOSE),
    "lceil": ("LEFT CEILING", OPEN), "rceil": ("RIGHT CEILING", CLOSE),
    "lfloor": ("LEFT FLOOR", OPEN), "rfloor": ("RIGHT FLOOR", CLOSE),
    "{": ("LEFT CURLY BRACKET", OPEN), "}": ("RIGHT CURLY BRACKET", CLOSE),
    "lbrace": ("LEFT CURLY BRACKET", OPEN), "rbrace": ("RIGHT CURLY BRACKET", CLOSE),
    # Satzzeichen
    "colon": ("COLON", P),
}
SYMBOLS = {k: (_u(n), c) for k, (n, c) in _SYM_SPEC.items()}

# Klasse direkt eingegebener Unicode-Zeichen (z. B. ∈ statt \in)
_CLASS_BY_CHAR = {ch: c for ch, c in SYMBOLS.values()}
_CLASS_BY_CHAR.update({_u("MIDDLE DOT"): B, MINUS: B, _u("INCREMENT"): O,
                       _u("UP TACK"): O, _u("VERTICAL LINE"): O,
                       _u("DOUBLE VERTICAL LINE"): O})

# Negation mit \not
_NEG_SPEC = [
    ("EQUALS SIGN", "NOT EQUAL TO"), ("ELEMENT OF", "NOT AN ELEMENT OF"),
    ("SUBSET OF", "NOT A SUBSET OF"), ("SUPERSET OF", "NOT A SUPERSET OF"),
    ("SUBSET OF OR EQUAL TO", "NEITHER A SUBSET OF NOR EQUAL TO"),
    ("SUPERSET OF OR EQUAL TO", "NEITHER A SUPERSET OF NOR EQUAL TO"),
    ("IDENTICAL TO", "NOT IDENTICAL TO"), ("THERE EXISTS", "THERE DOES NOT EXIST"),
    ("LESS-THAN SIGN", "NOT LESS-THAN"), ("GREATER-THAN SIGN", "NOT GREATER-THAN"),
    ("LESS-THAN OR EQUAL TO", "NEITHER LESS-THAN NOR EQUAL TO"),
    ("GREATER-THAN OR EQUAL TO", "NEITHER GREATER-THAN NOR EQUAL TO"),
    ("TILDE OPERATOR", "NOT TILDE"), ("ALMOST EQUAL TO", "NOT ALMOST EQUAL TO"),
    ("DIVIDES", "DOES NOT DIVIDE"), ("PARALLEL TO", "NOT PARALLEL TO"),
    ("RIGHT TACK", "DOES NOT PROVE"), ("TRUE", "NOT TRUE"),
    ("APPROXIMATELY EQUAL TO", "NEITHER APPROXIMATELY NOR ACTUALLY EQUAL TO"),
    ("RIGHTWARDS ARROW", "RIGHTWARDS ARROW WITH STROKE"),
    ("LEFTWARDS ARROW", "LEFTWARDS ARROW WITH STROKE"),
    ("LEFT RIGHT ARROW", "LEFT RIGHT ARROW WITH STROKE"),
    ("RIGHTWARDS DOUBLE ARROW", "RIGHTWARDS DOUBLE ARROW WITH STROKE"),
    ("LEFTWARDS DOUBLE ARROW", "LEFTWARDS DOUBLE ARROW WITH STROKE"),
    ("LEFT RIGHT DOUBLE ARROW", "LEFT RIGHT DOUBLE ARROW WITH STROKE"),
]
NEGATE = {_u(a): _u(b) for a, b in _NEG_SPEC}

# Operatornamen (aufrecht)
OPNAMES = {n: n for n in (
    "sin cos tan cot sec csc arcsin arccos arctan sinh cosh tanh coth exp log ln lg "
    "lim liminf limsup max min sup inf det dim ker deg gcd lcm arg Pr hom argmax argmin"
).split()}

# Abstandsbefehle
SPACES = {
    ",": _u("THIN SPACE"), ":": _u("MEDIUM MATHEMATICAL SPACE"),
    ">": _u("MEDIUM MATHEMATICAL SPACE"), ";": _u("THREE-PER-EM SPACE"),
    "!": "", " ": " ", "quad": _u("EM SPACE"), "qquad": _u("EM SPACE") * 2,
    "enspace": _u("EN SPACE"),
}

# Akzente (kombinierende Zeichen)
ACCENTS = {
    "bar": _u("COMBINING MACRON"), "overline": _u("COMBINING OVERLINE"),
    "underline": _u("COMBINING LOW LINE"), "hat": _u("COMBINING CIRCUMFLEX ACCENT"),
    "widehat": _u("COMBINING CIRCUMFLEX ACCENT"), "tilde": _u("COMBINING TILDE"),
    "widetilde": _u("COMBINING TILDE"), "vec": _u("COMBINING RIGHT ARROW ABOVE"),
    "dot": _u("COMBINING DOT ABOVE"), "ddot": _u("COMBINING DIAERESIS"),
    "check": _u("COMBINING CARON"), "acute": _u("COMBINING ACUTE ACCENT"),
    "grave": _u("COMBINING GRAVE ACCENT"), "breve": _u("COMBINING BREVE"),
}
_SPREAD_ACCENTS = {"overline", "underline", "widehat", "widetilde"}

# Schriftstile
STYLES = {
    "mathbf": "bold", "mathbb": "bb", "mathcal": "cal", "mathscr": "cal",
    "mathfrak": "frak", "mathsf": "sf", "mathtt": "tt", "mathit": "italic",
    "mathrm": "rm", "boldsymbol": "bolditalic", "bm": "bolditalic",
}
TEXTS = {
    "text": None, "textrm": None, "textnormal": None, "textup": None, "mbox": None,
    "textbf": "bold", "textit": "italic", "textsf": "sf", "texttt": "tt",
}
FRACS = {"frac", "dfrac", "tfrac", "cfrac"}
BIGS = {"big", "Big", "bigg", "Bigg", "bigl", "bigr", "Bigl", "Bigr",
        "biggl", "biggr", "Biggl", "Biggr"}

ARITY = {name: 1 for name in list(STYLES) + list(TEXTS) + list(ACCENTS)}
ARITY.update({f: 2 for f in FRACS})
ARITY.update({"sqrt": 1, "xrightarrow": 1, "xleftarrow": 1, "underbrace": 1,
              "overbrace": 1, "binom": 2, "dbinom": 2, "tbinom": 2, "overset": 2, "underset": 2, "stackrel": 2,
              "operatorname": 1, "mathop": 1, "pmod": 1, "boxed": 1})

# --------------------------------------------------------------------------
# Hoch- und Tiefzeichen
# --------------------------------------------------------------------------
_DIGIT_NAMES = "ZERO ONE TWO THREE FOUR FIVE SIX SEVEN EIGHT NINE".split()


def _build_scripts():
    sup, sub = {}, {}
    for d, name in zip("0123456789", _DIGIT_NAMES):
        sup[d] = _u("SUPERSCRIPT " + name)
        sub[d] = _u("SUBSCRIPT " + name)
    for key, name in (("+", "PLUS SIGN"), ("-", "MINUS"), (MINUS, "MINUS"),
                      ("=", "EQUALS SIGN"), ("(", "LEFT PARENTHESIS"),
                      (")", "RIGHT PARENTHESIS")):
        sup[key] = _u("SUPERSCRIPT " + name)
        sub[key] = _u("SUBSCRIPT " + name)
    # Hochgestellte Kleinbuchstaben: alle außer q. U+107A5 (q) existiert erst
    # seit Unicode 14 und wird von verbreiteten Schriften kaum unterstützt.
    for c in "abcdefghijklmnoprstuvwxyz":
        for name in ("SUPERSCRIPT LATIN SMALL LETTER ", "MODIFIER LETTER SMALL "):
            try:
                sup[c] = _u(name + c.upper())
                break
            except KeyError:
                pass
    # Hochgestellte Großbuchstaben: nur die seit langem kodierten.
    for c in "ABDEGHIJKLMNOPRTUVW":
        sup[c] = _u("MODIFIER LETTER CAPITAL " + c)
    # Tiefgestellte Kleinbuchstaben: es gibt nur diese 17.
    for c in "aehijklmnoprstuvx":
        sub[c] = _u("LATIN SUBSCRIPT SMALL LETTER " + c.upper())
    for g, name in ((GREEK["alpha"], "MODIFIER LETTER SMALL ALPHA"),
                    (GREEK["beta"], "MODIFIER LETTER SMALL BETA"),
                    (GREEK["gamma"], "MODIFIER LETTER SMALL GREEK GAMMA"),
                    (GREEK["delta"], "MODIFIER LETTER SMALL DELTA"),
                    (GREEK["theta"], "MODIFIER LETTER SMALL THETA"),
                    (GREEK["varphi"], "MODIFIER LETTER SMALL GREEK PHI"),
                    (GREEK["chi"], "MODIFIER LETTER SMALL CHI")):
        sup[g] = _u(name)
    for g, name in (("beta", "BETA"), ("gamma", "GAMMA"), ("rho", "RHO"),
                    ("varphi", "PHI"), ("chi", "CHI")):
        sub[GREEK[g]] = _u("GREEK SUBSCRIPT SMALL LETTER " + name)
    sup[PRIME] = PRIME
    sup[_u("DOUBLE PRIME")] = _u("DOUBLE PRIME")
    return sup, sub


SUP, SUB = _build_scripts()

# Ersatzzeichen (nur ohne --strict): optisch ähnlich, aber anderes Zeichen.
SUB_LOOKALIKE = {",": ","}
# Unicode 18.0 (September 2026): tiefgestelltes w, y, z (U+209D–U+209F).
# Feste Codepunkte, weil unicodedata in Python 3.8–3.14 diese Version noch nicht kennt.
# Quelle: https://www.unicode.org/Public/UCD/latest/charts/nameslist/2070/
SUB_UNICODE18 = {"w": "\u209D", "y": "\u209E", "z": "\u209F"}
# Nur auf ausdrücklichen Wunsch (lookalike=True): sieht anders aus als ein y.
SUB_Y_LOOKALIKE = {"y": _u("GREEK SUBSCRIPT SMALL LETTER GAMMA")}
SUP_LOOKALIKE = {_u("ASTERISK OPERATOR"): "*", "*": "*",
                 _u("DOWN TACK"): _u("MODIFIER LETTER CAPITAL T"), ",": ","}

ROOTS = {"2": _u("SQUARE ROOT"), "3": _u("CUBE ROOT"), "4": _u("FOURTH ROOT")}


def _build_vulgar():
    out = {}
    for cp in list(range(0xBC, 0xBF)) + list(range(0x2150, 0x215F)):
        dec = unicodedata.decomposition(chr(cp))
        if dec.startswith("<fraction>"):
            chars = "".join(chr(int(h, 16)) for h in dec.split()[1:])
            num, den = chars.split(FRACTION_SLASH)
            out[(num, den)] = chr(cp)
    return out


VULGAR = _build_vulgar()

# --------------------------------------------------------------------------
# Mathematische Alphabete
# --------------------------------------------------------------------------
_STYLE_PREFIX = {
    "italic": "ITALIC", "bold": "BOLD", "bolditalic": "BOLD ITALIC",
    "bb": "DOUBLE-STRUCK", "cal": "SCRIPT", "frak": "FRAKTUR",
    "sf": "SANS-SERIF", "tt": "MONOSPACE",
}
# Buchstaben, die im Block "Letterlike Symbols" vorab kodiert sind (Lücken)
_HOLE_PREFIX = {"bb": "DOUBLE-STRUCK", "cal": "SCRIPT", "frak": "BLACK-LETTER"}


@lru_cache(maxsize=None)
def styled(ch: str, style) -> str:
    """Zeichen im gewünschten mathematischen Alphabet; sonst unverändert."""
    if not style or style == "rm":
        return ch
    p = _STYLE_PREFIX[style]
    if ch.isascii() and ch.isalpha():
        case = "CAPITAL" if ch.isupper() else "SMALL"
        names = ["MATHEMATICAL %s %s %s" % (p, case, ch.upper())]
        if style in _HOLE_PREFIX:
            names.append("%s %s %s" % (_HOLE_PREFIX[style], case, ch.upper()))
        if style == "italic" and ch == "h":
            names.append("PLANCK CONSTANT")
        for n in names:
            try:
                return _u(n)
            except KeyError:
                pass
        return ch
    if ch.isascii() and ch.isdigit():
        try:
            return _u("MATHEMATICAL %s DIGIT %s" % (p, _DIGIT_NAMES[int(ch)]))
        except KeyError:
            return ch
    name = unicodedata.name(ch, "")
    if name.startswith("GREEK "):
        rest = name[len("GREEK "):]
        rest = rest.replace("SMALL LETTER ", "SMALL ").replace("CAPITAL LETTER ", "CAPITAL ")
        rest = rest.replace("LUNATE EPSILON SYMBOL", "EPSILON SYMBOL")
        try:
            return _u("MATHEMATICAL %s %s" % (p, rest))
        except KeyError:
            return ch
    return ch


# --------------------------------------------------------------------------
# Tokenizer und Parser
# --------------------------------------------------------------------------
_TOK = re.compile(r"\\([A-Za-z]+)\*?|\\(.)|(\s+)|(.)", re.S)


def _tokenize(s):
    out = []
    for m in _TOK.finditer(s):
        if m.group(1) is not None:
            out.append(("cmd", m.group(1)))
        elif m.group(2) is not None:
            out.append(("cmd", m.group(2)))
        elif m.group(3) is not None:
            out.append(("ws", m.group(3)))
        else:
            out.append(("chr", m.group(4)))
    return out


class _Parser:
    def __init__(self, toks, warn):
        self.t, self.i, self.warn = toks, 0, warn

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else None

    def take(self):
        tok = self.peek()
        self.i += 1
        return tok

    def skip_ws(self):
        while self.peek() is not None and self.peek()[0] == "ws":
            self.i += 1

    def seq(self, closing=False):
        nodes = []
        while True:
            tok = self.peek()
            if tok is None:
                if closing:
                    self.warn("Fehlende schließende Klammer '}'.")
                return nodes
            if tok == ("chr", "}"):
                self.i += 1
                if closing:
                    return nodes
                self.warn("Überzählige Klammer '}' ignoriert.")
                continue
            if tok[0] == "chr" and tok[1] in "^_":
                self.i += 1
                arg = self.arg()
                j = len(nodes) - 1
                while j >= 0 and nodes[j][0] == "ws":
                    j -= 1
                base = nodes[j] if j >= 0 else None
                del nodes[max(j, 0):]
                slot = 2 if tok[1] == "_" else 3
                if not (base is not None and base[0] == "scripts" and base[slot] is None):
                    base = ["scripts", base, None, None]
                base[slot] = arg
                nodes.append(base)
                continue
            nodes.append(self.node())

    def arg(self):
        self.skip_ws()
        tok = self.peek()
        if tok is None:
            self.warn("Argument fehlt am Ende der Formel.")
            return []
        if tok == ("chr", "{"):
            self.i += 1
            return self.seq(closing=True)
        return [self.node()]

    def node(self):
        kind, val = self.take()
        if kind == "ws":
            return ("ws", val)
        if kind == "chr":
            if val == "{":
                return ("group", self.seq(closing=True))
            return ("chr", val)
        name = val
        if name in ("left", "right", "middle") or name in BIGS:
            self.skip_ws()
            return ("delim", name, self.take())
        if name == "not":
            self.skip_ws()
            return ("not", self.node() if self.peek() is not None else ("chr", ""))
        opt = None
        if name in ("sqrt", "xrightarrow", "xleftarrow"):
            self.skip_ws()
            if self.peek() == ("chr", "["):
                self.i += 1
                opt = []
                while self.peek() is not None and self.peek() != ("chr", "]"):
                    opt.append(self.node())
                self.i += 1
        args = [self.arg() for _ in range(ARITY.get(name, 0))]
        return ("cmd", name, args, opt)


# --------------------------------------------------------------------------
# Ausgabe
# --------------------------------------------------------------------------
class _Opts:
    def __init__(self, italic, greek_italic, strict, warnings, lookalike=False, unicode18=False):
        self.italic, self.greek_italic, self.strict = italic, greek_italic, strict
        self.lookalike = lookalike and not strict
        self.unicode18 = unicode18
        self.warnings = warnings if warnings is not None else []

    def warn(self, msg):
        if msg not in self.warnings:
            self.warnings.append(msg)


class _Ctx:
    __slots__ = ("style", "script", "text", "opts")

    def __init__(self, opts, style=None, script=False, text=False):
        self.opts, self.style, self.script, self.text = opts, style, script, text

    def with_(self, **kw):
        c = _Ctx(self.opts, self.style, self.script, self.text)
        for k, v in kw.items():
            setattr(c, k, v)
        return c


_CHR_TABLE = {
    "+": ("+", B), "-": (MINUS, B), "*": (_u("ASTERISK OPERATOR"), B),
    "=": ("=", R), "<": ("<", R), ">": (">", R), ":": (":", R),
    ",": (",", P), ";": (";", P),
    "(": ("(", OPEN), "[": ("[", OPEN), ")": (")", CLOSE), "]": ("]", CLOSE),
    "!": ("!", CLOSE), "?": ("?", CLOSE),
    "'": (PRIME, O), "~": (NBSP, SP), "|": ("|", O), "/": ("/", O), ".": (".", O),
}


def _letter(c, ctx):
    if ctx.style:
        return styled(c, ctx.style)
    if ctx.text or ctx.script or not ctx.opts.italic:
        return c
    return styled(c, "italic")


def _greek(c, ctx):
    if ctx.style:
        return styled(c, ctx.style)
    if not (ctx.text or ctx.script) and ctx.opts.greek_italic and c.islower():
        return styled(c, "italic")
    return c


def _is_greek(c):
    return unicodedata.name(c, "").startswith("GREEK ")


def _render(nodes, ctx):
    atoms = []
    for nd in nodes:
        atoms.extend(_render_node(nd, ctx))
    return atoms


def _render_node(nd, ctx):
    k = nd[0]
    if k == "ws":
        return [[" ", SP]] if ctx.text else []
    if k == "chr":
        return _chr_atoms(nd[1], ctx)
    if k == "group":
        return [[_join(_render(nd[1], ctx), ctx), O]]
    if k == "scripts":
        return _render_scripts(nd, ctx)
    if k == "delim":
        return _render_delim(nd, ctx)
    if k == "not":
        atoms = _render_node(nd[1], ctx)
        t = atoms[0][0] if atoms else ""
        return [[NEGATE.get(t, t + NOT_OVERLAY), R]]
    return _render_cmd(nd, ctx)


def _chr_atoms(c, ctx):
    if c == "":
        return []
    if ctx.text:
        return [[_letter(c, ctx) if c.isalpha() else c, O]]
    if c.isascii() and c.isalpha():
        return [[_letter(c, ctx), O]]
    if c.isascii() and c.isdigit():
        return [[styled(c, ctx.style), O]]
    if c == "&":
        return []
    if c in _CHR_TABLE:
        return [list(_CHR_TABLE[c])]
    if _is_greek(c):
        return [[_greek(c, ctx), O]]
    return [[c, _CLASS_BY_CHAR.get(c, O)]]


def _render_cmd(nd, ctx):
    _, name, args, opt = nd
    if name in GREEK:
        return [[_greek(GREEK[name], ctx), O]]
    if name in SYMBOLS:
        ch, cls = SYMBOLS[name]
        return [[ch, cls]]
    if name in SPACES:
        return [[SPACES[name], SP]]
    if name == "\\":
        return [["\n", SP]]
    if name in OPNAMES:
        return [[OPNAMES[name], OP]]
    if name == "bmod":
        return [["mod", B]]
    if name == "pmod":
        return [[" (mod " + _join(_render(args[0], ctx), ctx) + ")", O]]
    if name == "operatorname":
        return [[_join(_render(args[0], ctx.with_(style="rm")), ctx), OP]]
    if name == "mathop":
        return [[_join(_render(args[0], ctx), ctx), OP]]
    if name in STYLES:
        return _render(args[0], ctx.with_(style=STYLES[name]))
    if name in TEXTS:
        tctx = ctx.with_(text=True, style=TEXTS[name])
        return [["".join(a[0] for a in _render(args[0], tctx)), O]]
    if name in FRACS:
        return [[_frac(args, ctx), O]]
    if name == "sqrt":
        return [[_sqrt(args[0], opt, ctx), O]]
    if name in ACCENTS:
        return [[_accent(name, args[0], ctx), O]]
    if name in ("overset", "stackrel", "underset"):
        base = _render(args[1], ctx) or [["", O]]
        base[-1][0] += _attach(args[0], ctx, "sub" if name == "underset" else "sup")
        return base
    if name in ("xrightarrow", "xleftarrow"):
        arrow = SYMBOLS["rightarrow" if name == "xrightarrow" else "leftarrow"][0]
        if opt:
            ctx.opts.warn("\\%s: Beschriftung unter dem Pfeil wird angehängt." % name)
        label = _attach(args[0], ctx, "sup") if args[0] else ""
        below = _attach(opt, ctx, "sub") if opt else ""
        return [[arrow + below + label, R]]
    if name in ("underbrace", "overbrace"):
        return [[_join(_render(args[0], ctx), ctx), O]]
    if name in ("binom", "dbinom", "tbinom"):
        ctx.opts.warn("\\binom ist im Klartext nicht stapelbar – als C(n, k) geschrieben.")
        n, k = (_join(_render(a, ctx), ctx) for a in args)
        return [["C(" + n + ", " + k + ")", O]]
    if name == "boxed":
        return _render(args[0], ctx)
    ctx.opts.warn("Unbekannter Befehl \\%s – unverändert übernommen." % name)
    return [["\\" + name, O]]


def _render_scripts(nd, ctx):
    _, base, sub, sup = nd
    atoms = _render_node(base, ctx) if base is not None else []
    if not atoms:
        atoms = [["", O]]
    suffix = ""
    if sub is not None:
        suffix += _attach(sub, ctx, "sub")
    if sup is not None:
        suffix += _attach(sup, ctx, "sup")
    atoms[-1][0] += suffix
    return atoms


def _render_delim(nd, ctx):
    _, name, tok = nd
    if tok is None or tok == ("chr", "."):
        return []
    kind, val = tok
    atoms = _chr_atoms(val, ctx) if kind == "chr" else _render_cmd(("cmd", val, [], None), ctx)
    if name == "left" or name.endswith("l"):
        cls = OPEN
    elif name == "right" or name.endswith("r"):
        cls = CLOSE
    elif name == "middle":
        cls = R
    else:
        cls = None
    if cls:
        for a in atoms:
            a[1] = cls
    return atoms


def _map_script(s, kind, opts):
    """Gibt (Ergebnis oder None, fehlende Zeichen, verwendete Ersatzzeichen) zurück."""
    table = SUP if kind == "sup" else SUB
    if kind == "sub" and opts.unicode18:
        table = dict(SUB, **SUB_UNICODE18)
    look = SUP_LOOKALIKE if kind == "sup" else SUB_LOOKALIKE
    if kind == "sub" and opts.lookalike:
        look = dict(look, **SUB_Y_LOOKALIKE)
    out, missing, used = [], [], []
    for ch in s:
        if ch in table:
            out.append(table[ch])
        elif not opts.strict and ch in look:
            out.append(look[ch])
            if ch not in ",*":
                used.append((ch, look[ch]))
        else:
            missing.append(ch)
    if missing:
        return None, missing, used
    return "".join(out), [], used


def _attach(nodes, ctx, kind):
    sctx = ctx.with_(script=True)
    s = _join(_render(nodes, sctx), sctx)
    mapped, missing, used = _map_script(s, kind, ctx.opts)
    word = "Tiefstellung" if kind == "sub" else "Hochstellung"
    if mapped is not None:
        if kind == "sub" and any(c in SUB_UNICODE18.values() for c in mapped):
            ctx.opts.warn("Tiefstellung nutzt Zeichen aus Unicode 18.0 (₝ ₞ ₟ für w, y, z); "
                          "viele Schriften und Geräte zeigen sie noch nicht an.")
        for orig, rep in used:
            ctx.opts.warn("%s: '%s' durch Ersatzzeichen '%s' (U+%04X %s) dargestellt."
                          % (word, orig, rep, ord(rep), unicodedata.name(rep)))
        return mapped
    ctx.opts.warn("%s von '%s' nicht vollständig in Unicode verfügbar (fehlt: %s) – "
                  "Ersatzschreibweise verwendet."
                  % (word, s, " ".join(sorted(set(missing)))))
    mark = "_" if kind == "sub" else "^"
    return mark + (s if len(s) == 1 else "(" + s + ")")


def _simple(atoms):
    return bool(atoms) and all(c == O for _, c in atoms) and \
        not any(ch.isspace() for t, _ in atoms for ch in t)


_DIGITS = re.compile(r"[0-9]+\Z")


def _frac(args, ctx):
    na, da = _render(args[0], ctx), _render(args[1], ctx)
    n, d = _join(na, ctx), _join(da, ctx)
    if ctx.script:
        return n + "/" + d
    if _DIGITS.match(n) and _DIGITS.match(d):
        if (n, d) in VULGAR:
            return VULGAR[(n, d)]
        return "".join(SUP[c] for c in n) + FRACTION_SLASH + "".join(SUB[c] for c in d)
    nn = n if _simple(na) else "(" + n + ")"
    dd = d if _simple(da) else "(" + d + ")"
    return nn + "/" + dd


def _sqrt(arg, opt, ctx):
    atoms = _render(arg, ctx)
    body = _join(atoms, ctx)
    if not ((len(atoms) == 1 and _simple(atoms)) or _DIGITS.match(body)):
        body = "(" + body + ")"
    if not opt:
        return ROOTS["2"] + body
    sctx = ctx.with_(script=True)
    idx = _join(_render(opt, sctx), sctx)
    if idx in ROOTS:
        return ROOTS[idx] + body
    mapped, _, _ = _map_script(idx, "sup", ctx.opts)
    return (mapped if mapped is not None else "(" + idx + ")") + ROOTS["2"] + body


def _accent(name, arg, ctx):
    mark = ACCENTS[name]
    text = _join(_render(arg, ctx), ctx)
    clusters = []
    for ch in text:
        if clusters and unicodedata.combining(ch):
            clusters[-1] += ch
        else:
            clusters.append(ch)
    if len(clusters) > 1 and name not in _SPREAD_ACCENTS:
        ctx.opts.warn("\\%s über mehrere Zeichen: Akzent auf jedes Zeichen gesetzt." % name)
    return "".join(c if c.isspace() else c + mark for c in clusters)


def _gap(a, b):
    if (a == R and b == R) or b == P or a == OPEN or b == CLOSE:
        return ""
    if B in (a, b) or R in (a, b):
        return " "
    if a == P:
        return " "
    if a == OP and b in (O, OP):
        return " "
    if b == OP and a in (O, CLOSE, OP):
        return " "
    return ""


def _join(atoms, ctx):
    if ctx.text:
        return "".join(a[0] for a in atoms)
    if ctx.script:  # explizite Abstände in Indizes entfallen
        return "".join(a[0] for a in atoms if a[1] != SP)
    real = [k for k, a in enumerate(atoms) if a[1] != SP]
    cls = {k: atoms[k][1] for k in real}
    unary = set()
    for idx, k in enumerate(real):
        if cls[k] == B:
            prev = cls[real[idx - 1]] if idx > 0 else None
            nxt = cls[real[idx + 1]] if idx + 1 < len(real) else None
            if prev in (None, B, OP, R, OPEN, P) or nxt in (None, R, CLOSE, P):
                cls[k] = O
                unary.add(k)  # Vorzeichen: kein Abstand zum Folgenden
    out, prev_k = "", None
    for k, (text, c) in enumerate(atoms):
        if c == SP:
            out += text
            prev_k = None
            continue
        if prev_k is not None and text:
            g = "" if prev_k in unary else _gap(cls[prev_k], cls[k])
            if g and out and not out[-1].isspace() and not text[0].isspace():
                out += g
        out += text
        if text:
            prev_k = k
    return out


# --------------------------------------------------------------------------
# Öffentliche Schnittstelle
# --------------------------------------------------------------------------
def convert(latex: str, *, italic: bool = True, greek_italic: bool = False,
            strict: bool = False, lookalike: bool = False, unicode18: bool = False,
            warnings: list | None = None) -> str:
    r"""Eine Formel (ohne $-Begrenzer) in Unicode-Text umwandeln.

    italic        Lateinische Einzelbuchstaben kursiv (wie LaTeX). False = ASCII.
    greek_italic  Griechische Kleinbuchstaben kursiv (𝛼 statt α).
    strict        Keine Ersatzzeichen (auch nicht * und ᵀ in Hochstellungen).
    lookalike     Tiefgestelltes y als griechisches ᵧ (U+1D67) darstellen.
    unicode18     Tiefgestelltes w, y, z aus Unicode 18.0 (U+209D–U+209F) verwenden.
    warnings      Liste, an die Hinweise angehängt werden.
    """
    opts = _Opts(italic, greek_italic, strict, warnings, lookalike, unicode18)
    nodes = _Parser(_tokenize(latex), opts.warn).seq()
    ctx = _Ctx(opts)
    return _join(_render(nodes, ctx), ctx).strip(" ")


_MATH = re.compile(
    r"(?<!\\)\$\$(.+?)(?<!\\)\$\$"            # $$ … $$
    r"|\\\[(.+?)\\\]"                          # \[ … \]
    r"|\\\((.+?)\\\)"                          # \( … \)
    r"|(?<![\\$])\$(?![\s$])(.+?)(?<![\s\\])\$(?!\d)",  # $ … $
    re.S)


def convert_text(text: str, **kw) -> str:
    r"""Fließtext mit Formeln in $…$, $$…$$, \(…\) oder \[…\] umwandeln.
    Text außerhalb bleibt unverändert; \$ ergibt ein Dollarzeichen."""
    out, pos = [], 0
    for m in _MATH.finditer(text):
        out.append(text[pos:m.start()].replace(r"\$", "$"))
        out.append(convert(next(g for g in m.groups() if g is not None), **kw))
        pos = m.end()
    out.append(text[pos:].replace(r"\$", "$"))
    return "".join(out)


# --------------------------------------------------------------------------
# Kommandozeile
# --------------------------------------------------------------------------
def copy_to_clipboard(text: str) -> bool:
    env = dict(os.environ)
    env.setdefault("LC_CTYPE", "UTF-8")  # pbcopy liest sonst ggf. nicht als UTF-8
    for cmd in (["pbcopy"], ["wl-copy"], ["xclip", "-selection", "clipboard"], ["clip.exe"]):
        if shutil.which(cmd[0]):
            subprocess.run(cmd, input=text.encode("utf-8"), check=True, env=env)
            return True
    return False


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="latex2unicode",
        description="LaTeX-ähnliche Formeln in Unicode-Klartext umwandeln "
                    "(z. B. für LinkedIn).")
    ap.add_argument("formel", nargs="*", help="Formel ohne $…$ (in einfache Anführungszeichen setzen)")
    ap.add_argument("-f", "--file", help="Textdatei mit Formeln in $…$ ('-' = Standardeingabe)")
    ap.add_argument("-m", "--math", action="store_true",
                    help="Datei/Standardeingabe vollständig als eine Formel behandeln")
    ap.add_argument("-o", "--output", help="Ergebnis in Datei schreiben")
    ap.add_argument("-c", "--copy", action="store_true", help="Ergebnis in die Zwischenablage kopieren")
    ap.add_argument("--strict", action="store_true", help="Keine Ersatzzeichen verwenden")
    ap.add_argument("--unicode18", action="store_true",
                    help="Tiefgestelltes w, y, z aus Unicode 18.0 (₝ ₞ ₟); noch wenig Schriftunterstützung")
    ap.add_argument("--ersatz-y", action="store_true",
                    help="Tiefgestelltes y als griechisches ᵧ darstellen (sieht anders aus)")
    ap.add_argument("--upright", action="store_true",
                    help="Variablen nicht kursiv (ASCII; besser durchsuchbar)")
    ap.add_argument("--greek-italic", action="store_true", help="Griechische Kleinbuchstaben kursiv")
    ap.add_argument("-q", "--quiet", action="store_true", help="Keine Hinweise ausgeben")
    ap.add_argument("--version", action="version", version=__version__)
    a = ap.parse_args(argv)

    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    kw = dict(italic=not a.upright, greek_italic=a.greek_italic, strict=a.strict,
              lookalike=a.ersatz_y, unicode18=a.unicode18)

    def run(src, math):
        warns = []
        res = convert(src, warnings=warns, **kw) if math else convert_text(src, warnings=warns, **kw)
        if not a.quiet:
            for w in warns:
                print("Hinweis: " + w, file=sys.stderr)
        return res

    if a.formel:
        result = run(" ".join(a.formel), True)
    elif a.file or not sys.stdin.isatty():
        if a.file and a.file != "-":
            with open(a.file, encoding="utf-8") as fh:
                src = fh.read()
        else:
            src = sys.stdin.read()
        result = run(src, a.math)
    else:
        print("Formel eingeben (Strg-D beendet):", file=sys.stderr)
        while True:
            try:
                line = input("LaTeX> ")
            except EOFError:
                print(file=sys.stderr)
                return 0
            if line.strip():
                res = run(line, "$" not in line)
                print(res)
                if a.copy and copy_to_clipboard(res):
                    print("(in Zwischenablage kopiert)", file=sys.stderr)

    if a.output:
        with open(a.output, "w", encoding="utf-8") as fh:
            fh.write(result)
    else:
        print(result, end="" if result.endswith("\n") else "\n")
    if a.copy:
        if copy_to_clipboard(result):
            if not a.quiet:
                print("(in Zwischenablage kopiert)", file=sys.stderr)
        else:
            print("Hinweis: kein Zwischenablage-Programm gefunden.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
