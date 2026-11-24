# latex2unicode

Wandelt LaTeX-Formeln in Unicode-Text um, den man in LinkedIn-Beiträge, Kommentare, E-Mails oder Chats einfügen kann. Diese Umgebungen haben keinen Formelsatz. Für Formeln, die Unicode nicht darstellen kann, erzeugt die App zusätzlich ein Bild (PNG/SVG).

```
Eingabe:   \sum_{i=1}^{n} x_i^2 \leq \lVert x \rVert_2^2
Ergebnis:  ∑ᵢ₌₁ⁿ 𝑥ᵢ² ≤ ‖𝑥‖₂²
```

Es gibt zwei Fassungen mit derselben Logik:

| Fassung | Datei | Zweck |
|---|---|---|
| Web-App | `docs/index.html` | Bedienung im Browser, Bild-Export, offline nutzbar |
| Python | `latex2unicode.py` | Kommandozeile und Modul (nur Standardbibliothek, Python ≥ 3.8) |

## Web-App

Online: https://fmassion.github.io/latex2unicode/ (GitHub Pages)

Lokal: `docs/index.html` im Browser öffnen. Die Datei ist in sich geschlossen, braucht keine Internetverbindung und überträgt keine Daten. Über GitHub Pages (Quelle: Ordner `/docs`) lässt sie sich auch online bereitstellen.

Funktionen:

- Formel oder ganzen Beitragstext mit `$…$` eingeben; das Ergebnis erscheint sofort
- Text kopieren
- Hinweise, wenn Unicode ein Zeichen nicht darstellen kann
- HTML mit `<i>`, `<sub>` und `<sup>` für Word, Pages, E-Mail und Webseiten; formatiert oder als Quelltext kopieren
- Bild mit echten Hoch- und Tiefstellungen, gestapelten Brüchen, Wurzelstrich, Grenzen unter Summen und Limes und mitwachsenden Klammern; als PNG kopieren oder speichern, als SVG speichern
- Kurzreferenz, deren Ergebnisse live berechnet werden

## Kommandozeile

```bash
python3 latex2unicode.py 'E = mc^2'                  # 𝐸 = 𝑚𝑐²
python3 latex2unicode.py -c '\sum_{i=1}^{n} x_i'     # zusätzlich in die Zwischenablage
python3 latex2unicode.py -f beitrag.txt -o beitrag_linkedin.txt   # nur $…$ wird ersetzt
python3 latex2unicode.py                              # interaktiv, Strg-D beendet
```

| Option | Wirkung |
|---|---|
| `-c`, `--copy` | Ergebnis in die Zwischenablage (macOS: pbcopy) |
| `-f DATEI` | Text mit Formeln in `$…$`, `$$…$$`, `\(…\)`, `\[…\]` |
| `-m`, `--math` | Datei bzw. Standardeingabe als eine Formel behandeln |
| `-o DATEI` | Ergebnis in eine Datei schreiben |
| `--upright` | Variablen nicht kursiv (normale ASCII-Buchstaben) |
| `--greek-italic` | Griechische Kleinbuchstaben kursiv (𝛼 statt α) |
| `--unicode18` | Tiefgestelltes w, y, z aus Unicode 18.0 (₝ ₞ ₟); viele Schriften zeigen sie noch nicht an |
| `--ersatz-y` | Tiefgestelltes y als griechisches ᵧ (sieht anders aus als y) |
| `--strict` | Keine Ersatzzeichen, auch nicht ᵀ für ⊤ und * für ∗ |
| `-q` | Hinweise unterdrücken |

Als Modul:

```python
from latex2unicode import convert, convert_text
convert(r"\alpha \leq \beta")              # 'α ≤ β'
convert_text(r"Sei $x \in \mathbb{R}$.")   # 'Sei 𝑥 ∈ ℝ.'
```

## Grenzen von Unicode

1. **Tiefgestellte Buchstaben:** Vorhanden sind nur a e h i j k l m n o p r s t u v x sowie β γ ρ φ χ. Es fehlen b c d f g q w y z, alle Großbuchstaben und die übrigen griechischen Buchstaben (z. B. θ). Ist ein Index nicht vollständig darstellbar, steht im Text `x_(…)`. Beispiel: `S_{phys}` wird zu `𝑆_(phys)`, denn ein tiefgestelltes y gibt es nicht. Im Bild und in der HTML-Ausgabe ist die Tiefstellung korrekt.
   Unicode 18.0 (September 2026) hat tiefgestelltes w, y, z ergänzt (U+209D–U+209F). Mit der Option `--unicode18` bzw. „Unicode 18“ in der App ergibt `S_{phys}` dann `𝑆ₚₕ₞ₛ`. Viele Schriften und Betriebssysteme können diese Zeichen noch nicht darstellen, und Leser sehen dann ein leeres Kästchen. Deshalb ist die Option standardmäßig aus.
2. **Hochgestellte Buchstaben:** Es fehlen q sowie C F Q S X Y Z.
3. **Brüche, Binomialkoeffizienten, Grenzen unter Operatoren:** Im Text werden sie linear geschrieben, also `(𝑎 + 𝑏)/2`, `C(𝑛, 𝑘)` und `lim_(x→0)`. Im Bild erscheinen sie gestapelt.
4. **Barrierefreiheit und Suche:** Kursive Mathematikbuchstaben (𝑥) sind eigene Unicode-Zeichen. Screenreader und Suchfunktionen behandeln sie nicht wie normale Buchstaben. Für Fließtext ist das Werkzeug deshalb nicht gedacht.
5. **Darstellung:** Wie die Zeichen aussehen, hängt von den Schriften des Lesegeräts ab.

## Welcher Weg für welches Ziel

| Ziel | Weg |
|---|---|
| LinkedIn-Beitrag, Kommentar, Chat (reiner Text) | Unicode-Text; nicht darstellbare Formeln als Bild anhängen |
| Word, Pages, Outlook, Apple Mail | HTML „formatiert kopieren“ |
| Webseite, Blog | HTML-Quelltext |
| Fachartikel, Markdown mit Formelrenderer (Obsidian, Jupyter, GitHub) | LaTeX direkt, z. B. `$s_t \in S_{\mathrm{phys}}$` |

## Abdeckung

`ABDECKUNG.md` enthält das Ergebnis für 410 Formeln und Befehle aus einem Spickzettel mathematischer Notation. Diesen Bericht erzeugt `python3 tools/abdeckung.py DATEI.md` für jede beliebige Markdown-Datei.

## Aufbau und Entwicklung

```
latex2unicode.py        Referenzimplementierung (Python)
web/tables.js           Zeichentabellen, erzeugt aus Python (nicht von Hand ändern)
web/converter.js        Umwandlung (JavaScript, gleiche Logik wie Python)
web/render.js           Bild-Export (SVG-Layout)
web/app.html            Oberfläche (lädt die drei Skripte)
docs/index.html         gebaute App, eine einzige Datei
tools/export_tables.py  web/tables.js erzeugen
tools/build_app.py      Tabellen exportieren und docs/index.html bauen
tools/abdeckung.py      Abdeckungsbericht und Referenzdaten für den Gleichlauftest
tests/cases.json        gemeinsame Testfälle für beide Fassungen
tests/parity.json       Python-Ergebnisse als Referenz für JavaScript
```

Alle Sonderzeichen werden in Python über ihre offiziellen Unicode-Namen erzeugt (`unicodedata.lookup`). Die JavaScript-Fassung übernimmt die exportierten Tabellen. Ein falscher Zeichenname führt deshalb zu einem Fehler statt zu einem falschen Zeichen.

```bash
python3 tools/build_app.py                      # nach Änderungen an Python oder web/
python3 -m unittest discover -s tests -v         # Python-Tests
node tests/test_js.mjs                           # JavaScript-Tests inkl. Gleichlauf mit Python
```

## Lizenz

MIT-Lizenz, siehe `LICENSE`. Nutzung, Änderung, Weitergabe und kommerzielle Verwendung sind erlaubt; der Copyright- und Lizenzhinweis muss erhalten bleiben.
