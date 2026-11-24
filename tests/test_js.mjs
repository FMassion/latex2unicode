// Tests der JavaScript-Fassung. Aufruf: node tests/test_js.mjs
import { createRequire } from "module";
import { readFileSync } from "fs";
import { dirname, join } from "path";
import { fileURLToPath } from "url";

const require = createRequire(import.meta.url);
const here = dirname(fileURLToPath(import.meta.url));
const L2U = require("../web/converter.js");
const R = require("../web/render.js");

let fail = 0, n = 0;
function check(name, got, want) {
  n++;
  if (got !== want) { fail++; console.log("FEHLER", name, "\n  erwartet:", JSON.stringify(want), "\n  erhalten:", JSON.stringify(got)); }
}

// 1. Gemeinsame Testfälle
const cases = JSON.parse(readFileSync(join(here, "cases.json"), "utf8"));
for (const c of cases) {
  const r = c.text !== undefined ? L2U.convertText(c.text, c.opts) : L2U.convert(c.in, c.opts);
  check(c.text || c.in, r.text, c.out);
  if (c.warn !== undefined) check("Hinweis " + (c.text || c.in), r.warnings.length > 0, c.warn);
}

// 2. Gleichlauf mit Python über alle Formeln des Spickzettels
const parity = JSON.parse(readFileSync(join(here, "parity.json"), "utf8"));
for (const p of parity) {
  const r = L2U.convert(p.in);
  check("Gleichlauf " + p.in, r.text, p.out);
  check("Gleichlauf Hinweise " + p.in, JSON.stringify(r.warnings), JSON.stringify(p.warnings));
}

// 3. Bilddarstellung: Struktur und Layout (Breitenmessung vereinfacht)
const M = L2U.MARKERS;
check("rich Tiefstellung", L2U.convert("S_{phys}", { rich: true }).text, "𝑆" + M.sub + "𝑝ℎ𝑦𝑠" + M.end);
check("rich Grenzen", L2U.convert("\\sum_{i=1}^n", { rich: true }).text, "∑" + M.under + "𝑖=1" + M.end + M.over + "𝑛" + M.end);
check("rich Bruch", L2U.convert("\\frac{a}{b}", { rich: true }).text, M.frac + "𝑎" + M.mid + "𝑏" + M.end);
const measure = (s, size) => Array.from(s).length * size * 0.5;
const svg = R.toSVG(L2U.convert("s_t \\in S_{phys} \\times \\frac{a+b}{\\sqrt{2}}", { rich: true }).text, { measure, size: 40 });
check("SVG beginnt mit <svg", svg.startsWith("<svg"), true);
check("SVG enthält Tiefstellung phys", svg.includes(">𝑝ℎ𝑦𝑠<"), true);
check("SVG enthält keine Steuerzeichen", /[\uE000-\uE00F]/.test(svg), false);

// 4. Bild-Export für alle Formeln des Spickzettels: läuft durch, ohne Ersatzschreibweise
for (const p of parity) {
  const rich = L2U.convert(p.in, { rich: true }).text;
  let out = "";
  try { out = R.toSVG(rich, { measure, size: 40 }); } catch (e) { out = "FEHLER " + e.message; }
  check("SVG " + p.in, out.startsWith("<svg") && !/_\(|\^\(|[\uE000-\uE00F]/.test(out), true);
}

// 5. HTML-Ausgabe
check("HTML Nutzerformel", L2U.toHTML("s_t \\in S_{phys} \\times S_{\\text{non-phys}}", {}),
  "<i>s</i><sub><i>t</i></sub> ∈ <i>S</i><sub><i>phys</i></sub> × <i>S</i><sub>non-phys</sub>");
check("HTML Summe", L2U.toHTML("\\sum_{i=1}^{n} x_i^2", {}),
  "∑<sub><i>i</i>=1</sub><sup><i>n</i></sup> <i>x</i><sub><i>i</i></sub><sup>2</sup>");
check("HTML Bruch", L2U.toHTML("\\frac{a+b}{2}", {}), "(<i>a</i> + <i>b</i>)/2");
check("HTML Escape", L2U.toHTML("a < b", {}), "<i>a</i> &lt; <i>b</i>");
check("HTML Text", L2U.toHTML("Sei $x_i$ gross", {}, true), "Sei <i>x</i><sub><i>i</i></sub> gross");

console.log(`${n - fail}/${n} Prüfungen bestanden`);
process.exit(fail ? 1 : 0);
