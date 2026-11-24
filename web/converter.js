/*
 * latex2unicode – JavaScript-Fassung (gleiche Logik wie latex2unicode.py).
 *
 * convert(latex, opts)      -> { text, warnings }   Unicode-Klartext
 * convertText(text, opts)   -> { text, warnings }   Fließtext mit $…$
 * convert(latex, {rich:true}) liefert eine Zwischendarstellung mit
 * Steuerzeichen (Private Use Area) für den Bild-Export (render.js).
 *
 * Die Zeichentabellen stammen aus tables.js (erzeugt aus Python/unicodedata).
 */
(function (root) {
  "use strict";
  const T = (typeof L2U_TABLES !== "undefined") ? L2U_TABLES : require("./tables.js");

  const O = "ord", OP = "op", B = "bin", R = "rel", OPEN = "open", CLOSE = "close", P = "punct", SP = "space";
  const C = T.CONST;

  // Steuerzeichen für die Bilddarstellung
  const MK = {
    sub: "\uE000", sup: "\uE001", end: "\uE002", frac: "\uE003", mid: "\uE004",
    under: "\uE005", over: "\uE006", sqrt: "\uE007", rootidx: "\uE008", binom: "\uE009",
    delim: "\uE00A", it: "\uE00B",
  };
  const MK_RE = /[\uE000-\uE00F]/;

  const LIMIT_OPS = new Set(["sum", "prod", "coprod", "bigcup", "bigcap", "bigvee", "bigwedge",
    "bigoplus", "bigotimes", "lim", "liminf", "limsup", "max", "min", "sup", "inf", "det", "gcd",
    "Pr", "argmax", "argmin", "underbrace", "overbrace"]);
  const SPREAD = new Set(T.SPREAD_ACCENTS);
  const FRACS = new Set(T.FRACS);
  const BIGS = new Set(T.BIGS);

  const has = (obj, k) => Object.prototype.hasOwnProperty.call(obj, k);
  const cps = (s) => Array.from(s);
  const isSpace = (c) => /^\s$/u.test(c);
  const DIGITS = /^[0-9]+$/;

  function styled(ch, style) {
    if (!style || style === "rm") return ch;
    const m = T.STYLED[style];
    return (m && has(m, ch)) ? m[ch] : ch;
  }

  function isGreek(c) {
    const cp = c.codePointAt(0);
    return (cp >= 0x370 && cp <= 0x3FF && !(cp >= 0x3E2 && cp <= 0x3EF)) ||
      (cp >= 0x1F00 && cp <= 0x1FFF) || (cp >= 0x1D26 && cp <= 0x1D2A) || (cp >= 0x1D66 && cp <= 0x1D6A);
  }
  const isLower = (c) => c === c.toLowerCase() && c !== c.toUpperCase();

  // ------------------------------------------------------------------ Tokenizer
  function tokenize(s) {
    const re = /\\([A-Za-z]+)\*?|\\([\s\S])|(\s+)|([\s\S])/gu;
    const out = [];
    let m;
    while ((m = re.exec(s)) !== null) {
      if (m[1] !== undefined) out.push(["cmd", m[1]]);
      else if (m[2] !== undefined) out.push(["cmd", m[2]]);
      else if (m[3] !== undefined) out.push(["ws", m[3]]);
      else out.push(["chr", m[4]]);
    }
    return out;
  }

  // ------------------------------------------------------------------ Parser
  class Parser {
    constructor(toks, warn) { this.t = toks; this.i = 0; this.warn = warn; }
    peek() { return this.i < this.t.length ? this.t[this.i] : null; }
    take() { const t = this.peek(); this.i++; return t; }
    is(tok, kind, val) { return tok !== null && tok[0] === kind && tok[1] === val; }
    skipWs() { while (this.peek() !== null && this.peek()[0] === "ws") this.i++; }

    seq(closing) {
      const nodes = [];
      for (;;) {
        const tok = this.peek();
        if (tok === null) {
          if (closing) this.warn("Fehlende schließende Klammer '}'.");
          return nodes;
        }
        if (this.is(tok, "chr", "}")) {
          this.i++;
          if (closing) return nodes;
          this.warn("Überzählige Klammer '}' ignoriert.");
          continue;
        }
        if (tok[0] === "chr" && (tok[1] === "^" || tok[1] === "_")) {
          this.i++;
          const arg = this.arg();
          let j = nodes.length - 1;
          while (j >= 0 && nodes[j][0] === "ws") j--;
          let base = j >= 0 ? nodes[j] : null;
          nodes.splice(Math.max(j, 0));
          const slot = tok[1] === "_" ? 2 : 3;
          if (!(base !== null && base[0] === "scripts" && base[slot] === null)) {
            base = ["scripts", base, null, null];
          }
          base[slot] = arg;
          nodes.push(base);
          continue;
        }
        nodes.push(this.node());
      }
    }

    arg() {
      this.skipWs();
      const tok = this.peek();
      if (tok === null) { this.warn("Argument fehlt am Ende der Formel."); return []; }
      if (this.is(tok, "chr", "{")) { this.i++; return this.seq(true); }
      return [this.node()];
    }

    node() {
      const [kind, val] = this.take();
      if (kind === "ws") return ["ws", val];
      if (kind === "chr") {
        if (val === "{") return ["group", this.seq(true)];
        return ["chr", val];
      }
      const name = val;
      if (name === "left" || name === "right" || name === "middle" || BIGS.has(name)) {
        this.skipWs();
        return ["delim", name, this.take()];
      }
      if (name === "not") {
        this.skipWs();
        return ["not", this.peek() !== null ? this.node() : ["chr", ""]];
      }
      let opt = null;
      if (name === "sqrt" || name === "xrightarrow" || name === "xleftarrow") {
        this.skipWs();
        if (this.is(this.peek(), "chr", "[")) {
          this.i++;
          opt = [];
          while (this.peek() !== null && !this.is(this.peek(), "chr", "]")) opt.push(this.node());
          this.i++;
        }
      }
      const n = has(T.ARITY, name) ? T.ARITY[name] : 0;
      const args = [];
      for (let k = 0; k < n; k++) args.push(this.arg());
      return ["cmd", name, args, opt];
    }
  }

  // ------------------------------------------------------------------ Kontext
  function makeCtx(opts) { return { opts, style: null, script: false, text: false, rich: !!opts.rich }; }
  const withCtx = (ctx, kw) => Object.assign({}, ctx, kw);

  // HTML-Ausgabe: Kursivschrift als <i> statt als mathematischer Kursivbuchstabe
  const italicOf = (c, ctx) => (ctx.opts.html ? MK.it + c + MK.end : styled(c, "italic"));
  function letter(c, ctx) {
    if (ctx.style) return styled(c, ctx.style);
    if (ctx.text || (ctx.script && !ctx.rich) || !ctx.opts.italic) return c;
    return italicOf(c, ctx);
  }
  function greek(c, ctx) {
    if (ctx.style) return styled(c, ctx.style);
    if (!ctx.text && (!ctx.script || ctx.rich) && ctx.opts.greekItalic && isLower(c)) return italicOf(c, ctx);
    return c;
  }

  // ------------------------------------------------------------------ Ausgabe
  const WORD_SPACE_HINT = "Leerzeichen zwischen Wörtern werden in Formeln ignoriert (wie in LaTeX). " +
    "Für normalen Text \\text{…} verwenden oder den Text außerhalb von $…$ schreiben.";

  // Hinweis, wenn in einer Formel zwei Wörter (je ≥ 3 Buchstaben) durch ein Leerzeichen getrennt sind
  function checkWordSpaces(nodes, ctx) {
    const seq = [];
    let cur = 0;
    for (const nd of nodes) {
      if (nd[0] === "chr" && /^[A-Za-z]$/.test(nd[1])) { cur++; continue; }
      if (cur) { seq.push(["w", cur]); cur = 0; }
      seq.push(nd[0] === "ws" ? ["ws", 0] : ["x", 0]);
    }
    if (cur) seq.push(["w", cur]);
    for (let i = 0; i + 2 < seq.length; i++) {
      const [a, b, c] = [seq[i], seq[i + 1], seq[i + 2]];
      if (a[0] === "w" && a[1] >= 3 && b[0] === "ws" && c[0] === "w" && c[1] >= 3) {
        ctx.opts.warn(WORD_SPACE_HINT);
        return;
      }
    }
  }

  function render(nodes, ctx) {
    if (!ctx.text && !ctx.script) checkWordSpaces(nodes, ctx);
    const atoms = [];
    for (const nd of nodes) for (const a of renderNode(nd, ctx)) atoms.push(a);
    return atoms;
  }

  function renderNode(nd, ctx) {
    switch (nd[0]) {
      case "ws": return ctx.text ? [[" ", SP]] : [];
      case "chr": return chrAtoms(nd[1], ctx);
      case "group": return [[join(render(nd[1], ctx), ctx), O]];
      case "scripts": return renderScripts(nd, ctx);
      case "delim": return renderDelim(nd, ctx);
      case "not": {
        const atoms = renderNode(nd[1], ctx);
        const t = atoms.length ? atoms[0][0] : "";
        return [[has(T.NEGATE, t) ? T.NEGATE[t] : t + C.NOT_OVERLAY, R]];
      }
      default: return renderCmd(nd, ctx);
    }
  }

  function chrAtoms(c, ctx) {
    if (c === "") return [];
    if (ctx.text) return [[/^\p{L}$/u.test(c) ? letter(c, ctx) : c, O]];
    if (/^[A-Za-z]$/.test(c)) return [[letter(c, ctx), O]];
    if (/^[0-9]$/.test(c)) return [[styled(c, ctx.style), O]];
    if (c === "&") return [];
    if (has(T.CHR_TABLE, c)) return [T.CHR_TABLE[c].slice()];
    if (isGreek(c)) return [[greek(c, ctx), O]];
    return [[c, has(T.CLASS_BY_CHAR, c) ? T.CLASS_BY_CHAR[c] : O]];
  }

  function renderCmd(nd, ctx) {
    const [, name, args, opt] = nd;
    const w = (m) => ctx.opts.warn(m);
    if (has(T.GREEK, name)) return [[greek(T.GREEK[name], ctx), O]];
    if (has(T.SYMBOLS, name)) {
      const [ch, cls] = T.SYMBOLS[name];
      return [LIMIT_OPS.has(name) ? [ch, cls, "limits"] : [ch, cls]];
    }
    if (has(T.SPACES, name)) return [[T.SPACES[name], SP]];
    if (name === "\\") return [["\n", SP]];
    if (has(T.OPNAMES, name)) return [LIMIT_OPS.has(name) ? [T.OPNAMES[name], OP, "limits"] : [T.OPNAMES[name], OP]];
    if (name === "bmod") return [["mod", B]];
    if (name === "pmod") return [[" (mod " + join(render(args[0], ctx), ctx) + ")", O]];
    if (name === "operatorname") return [[join(render(args[0], withCtx(ctx, { style: "rm" })), ctx), OP]];
    if (name === "mathop") return [[join(render(args[0], ctx), ctx), OP]];
    if (has(T.STYLES, name)) return render(args[0], withCtx(ctx, { style: T.STYLES[name] }));
    if (has(T.TEXTS, name)) {
      const tctx = withCtx(ctx, { text: true, style: T.TEXTS[name] });
      return [[render(args[0], tctx).map((a) => a[0]).join(""), O]];
    }
    if (FRACS.has(name)) return [[frac(args, ctx), O]];
    if (name === "sqrt") return [[sqrt(args[0], opt, ctx), O]];
    if (has(T.ACCENTS, name)) return [[accent(name, args[0], ctx), O]];
    if (name === "overset" || name === "stackrel" || name === "underset") {
      let base = render(args[1], ctx);
      if (!base.length) base = [["", O]];
      const kind = name === "underset" ? "sub" : "sup";
      base[base.length - 1][0] += attach(args[0], ctx, ctx.rich ? (kind === "sub" ? "under" : "over") : kind);
      return base;
    }
    if (name === "xrightarrow" || name === "xleftarrow") {
      const arrow = T.SYMBOLS[name === "xrightarrow" ? "rightarrow" : "leftarrow"][0];
      if (opt && !ctx.rich) w("\\" + name + ": Beschriftung unter dem Pfeil wird angehängt.");
      const label = args[0].length ? attach(args[0], ctx, ctx.rich ? "over" : "sup") : "";
      const below = opt ? attach(opt, ctx, ctx.rich ? "under" : "sub") : "";
      return [[arrow + below + label, R]];
    }
    if (name === "underbrace" || name === "overbrace") return [[join(render(args[0], ctx), ctx), O, "limits"]];
    if (name === "binom" || name === "dbinom" || name === "tbinom") {
      const [n, k] = args.map((a) => join(render(a, ctx), ctx));
      if (ctx.rich && !ctx.script) return [[MK.binom + n + MK.mid + k + MK.end, O]];
      w("\\binom ist im Klartext nicht stapelbar – als C(n, k) geschrieben.");
      return [["C(" + n + ", " + k + ")", O]];
    }
    if (name === "boxed") return render(args[0], ctx);
    w("Unbekannter Befehl \\" + name + " – unverändert übernommen.");
    return [["\\" + name, O]];
  }

  function renderScripts(nd, ctx) {
    const [, base, sub, sup] = nd;
    let atoms = base !== null ? renderNode(base, ctx) : [];
    if (!atoms.length) atoms = [["", O]];
    const last = atoms[atoms.length - 1];
    const limits = ctx.rich && !ctx.script && last[2] === "limits";
    let suffix = "";
    if (sub !== null) suffix += attach(sub, ctx, ctx.rich ? (limits ? "under" : "sub") : "sub");
    if (sup !== null) suffix += attach(sup, ctx, ctx.rich ? (limits ? "over" : "sup") : "sup");
    last[0] += suffix;
    return atoms;
  }

  function renderDelim(nd, ctx) {
    const [, name, tok] = nd;
    if (tok === null || tok === undefined || (tok[0] === "chr" && tok[1] === ".")) return [];
    const atoms = tok[0] === "chr" ? chrAtoms(tok[1], ctx) : renderCmd(["cmd", tok[1], [], null], ctx);
    let cls = null;
    if (name === "left" || name.endsWith("l")) cls = OPEN;
    else if (name === "right" || name.endsWith("r")) cls = CLOSE;
    else if (name === "middle") cls = R;
    if (cls) for (const a of atoms) a[1] = cls;
    // Bilddarstellung: Begrenzer an die Höhe des Inhalts anpassen
    if (ctx.rich && !ctx.script) for (const a of atoms) if (a[0]) a[0] = MK.delim + a[0] + MK.end;
    return atoms;
  }

  function mapScript(s, kind, opts) {
    let table = kind === "sup" ? T.SUP : T.SUB;
    if (kind === "sub" && opts.unicode18) table = Object.assign({}, table, T.SUB_UNICODE18);
    let look = kind === "sup" ? T.SUP_LOOKALIKE : T.SUB_LOOKALIKE;
    if (kind === "sub" && opts.lookalike) look = Object.assign({}, look, T.SUB_Y_LOOKALIKE);
    const out = [], missing = [], used = [];
    for (const ch of cps(s)) {
      if (has(table, ch)) out.push(table[ch]);
      else if (!opts.strict && has(look, ch)) {
        out.push(look[ch]);
        if (ch !== "," && ch !== "*") used.push([ch, look[ch]]);
      } else missing.push(ch);
    }
    if (missing.length) return [null, missing, used];
    return [out.join(""), [], used];
  }

  const hex4 = (c) => c.codePointAt(0).toString(16).toUpperCase().padStart(4, "0");
  const sortCp = (arr) => Array.from(new Set(arr)).sort((a, b) => a.codePointAt(0) - b.codePointAt(0));

  function attach(nodes, ctx, kind) {
    const sctx = withCtx(ctx, { script: true });
    const s = join(render(nodes, sctx), sctx);
    if (ctx.rich) return MK[kind] + s + MK.end;
    const [mapped, missing, used] = mapScript(s, kind, ctx.opts);
    const word = kind === "sub" ? "Tiefstellung" : "Hochstellung";
    if (mapped !== null) {
      const u18 = Object.values(T.SUB_UNICODE18);
      if (kind === "sub" && cps(mapped).some((c) => u18.includes(c))) {
        ctx.opts.warn("Tiefstellung nutzt Zeichen aus Unicode 18.0 (" + u18.join(" ") +
          " für w, y, z); viele Schriften und Geräte zeigen sie noch nicht an.");
      }
      for (const [orig, rep] of used) {
        ctx.opts.warn(word + ": '" + orig + "' durch Ersatzzeichen '" + rep + "' (U+" + hex4(rep) + " " +
          T.LOOKALIKE_NAMES[rep] + ") dargestellt.");
      }
      return mapped;
    }
    ctx.opts.warn(word + " von '" + s + "' nicht vollständig in Unicode verfügbar (fehlt: " +
      sortCp(missing).join(" ") + ") – Ersatzschreibweise verwendet.");
    const mark = kind === "sub" ? "_" : "^";
    return mark + (cps(s).length === 1 ? s : "(" + s + ")");
  }

  function simple(atoms) {
    return atoms.length > 0 && atoms.every((a) => a[1] === O) &&
      !atoms.some((a) => cps(a[0]).some(isSpace));
  }

  function frac(args, ctx) {
    const na = render(args[0], ctx), da = render(args[1], ctx);
    const n = join(na, ctx), d = join(da, ctx);
    if (ctx.script) return n + "/" + d;
    if (ctx.rich) return MK.frac + n + MK.mid + d + MK.end;
    if (DIGITS.test(n) && DIGITS.test(d)) {
      const key = n + "/" + d;
      if (has(T.VULGAR, key)) return T.VULGAR[key];
      return cps(n).map((c) => T.SUP[c]).join("") + C.FRACTION_SLASH + cps(d).map((c) => T.SUB[c]).join("");
    }
    return (simple(na) ? n : "(" + n + ")") + "/" + (simple(da) ? d : "(" + d + ")");
  }

  function sqrt(arg, opt, ctx) {
    const atoms = render(arg, ctx);
    let body = join(atoms, ctx);
    if (ctx.rich && !ctx.script) {
      let pre = "";
      if (opt) {
        const sctx = withCtx(ctx, { script: true });
        const idx = join(render(opt, sctx), sctx);
        pre = MK.rootidx + idx + MK.end;
      }
      return pre + MK.sqrt + body + MK.end;
    }
    if (!((atoms.length === 1 && simple(atoms)) || DIGITS.test(body))) body = "(" + body + ")";
    if (!opt) return T.ROOTS["2"] + body;
    const sctx = withCtx(ctx, { script: true });
    const idx = join(render(opt, sctx), sctx);
    if (has(T.ROOTS, idx)) return T.ROOTS[idx] + body;
    const [mapped] = mapScript(idx, "sup", ctx.opts);
    return (mapped !== null ? mapped : "(" + idx + ")") + T.ROOTS["2"] + body;
  }

  function accent(name, arg, ctx) {
    const mark = T.ACCENTS[name];
    const text = join(render(arg, ctx), ctx);
    const clusters = [];
    for (const ch of cps(text)) {
      if (clusters.length && /^\p{M}$/u.test(ch)) clusters[clusters.length - 1] += ch;
      else clusters.push(ch);
    }
    const real = clusters.filter((c) => !MK_RE.test(c));
    if (real.length > 1 && !SPREAD.has(name)) {
      ctx.opts.warn("\\" + name + " über mehrere Zeichen: Akzent auf jedes Zeichen gesetzt.");
    }
    return clusters.map((c) => (isSpace(c) || MK_RE.test(c)) ? c : c + mark).join("");
  }

  function gap(a, b) {
    if ((a === R && b === R) || b === P || a === OPEN || b === CLOSE) return "";
    if (a === B || b === B || a === R || b === R) return " ";
    if (a === P) return " ";
    if (a === OP && (b === O || b === OP)) return " ";
    if (b === OP && (a === O || a === CLOSE || a === OP)) return " ";
    return "";
  }

  function join(atoms, ctx) {
    if (ctx.text) return atoms.map((a) => a[0]).join("");
    if (ctx.script) return atoms.filter((a) => a[1] !== SP).map((a) => a[0]).join("");
    const real = [];
    atoms.forEach((a, k) => { if (a[1] !== SP) real.push(k); });
    const cls = {};
    for (const k of real) cls[k] = atoms[k][1];
    const unary = new Set();
    real.forEach((k, idx) => {
      if (cls[k] === B) {
        const prev = idx > 0 ? cls[real[idx - 1]] : null;
        const nxt = idx + 1 < real.length ? cls[real[idx + 1]] : null;
        if ([null, B, OP, R, OPEN, P].includes(prev) || [null, R, CLOSE, P].includes(nxt)) {
          cls[k] = O;
          unary.add(k); // Vorzeichen: kein Abstand zum Folgenden
        }
      }
    });
    let out = "", prevK = null;
    atoms.forEach((a, k) => {
      const text = a[0], c = a[1];
      if (c === SP) { out += text; prevK = null; return; }
      if (prevK !== null && text) {
        const g = unary.has(prevK) ? "" : gap(cls[prevK], cls[k]);
        const lastCh = out.length ? cps(out).pop() : "";
        if (g && out && !isSpace(lastCh) && !isSpace(cps(text)[0])) out += g;
      }
      out += text;
      if (text) prevK = k;
    });
    return out;
  }

  // ------------------------------------------------------------------ Schnittstelle
  function normOpts(o) {
    o = o || {};
    const warnings = [];
    return {
      italic: o.italic !== false, greekItalic: !!o.greekItalic, strict: !!o.strict,
      lookalike: !!o.lookalike && !o.strict, unicode18: !!o.unicode18,
      rich: !!o.rich || !!o.html, html: !!o.html, warnings,
      warn(m) { if (!warnings.includes(m)) warnings.push(m); },
    };
  }

  function convertWith(latex, opts) {
    const nodes = new Parser(tokenize(latex), opts.warn).seq(false);
    const ctx = makeCtx(opts);
    return join(render(nodes, ctx), ctx).replace(/^ +| +$/g, "");
  }

  function convert(latex, o) {
    const opts = normOpts(o);
    return { text: convertWith(latex, opts), warnings: opts.warnings };
  }

  const MATH_RE = /(?<!\\)\$\$(.+?)(?<!\\)\$\$|\\\[(.+?)\\\]|\\\((.+?)\\\)|(?<![\\$])\$(?![\s$])(.+?)(?<![\s\\])\$(?!\d)/gsu;

  function convertText(text, o) {
    const opts = normOpts(o);
    const out = [];
    let pos = 0, m;
    MATH_RE.lastIndex = 0;
    const segments = [];
    while ((m = MATH_RE.exec(text)) !== null) {
      out.push(text.slice(pos, m.index).replace(/\\\$/g, "$"));
      const inner = m[1] !== undefined ? m[1] : m[2] !== undefined ? m[2] : m[3] !== undefined ? m[3] : m[4];
      out.push(convertWith(inner, opts));
      segments.push(inner);
      pos = m.index + m[0].length;
    }
    out.push(text.slice(pos).replace(/\\\$/g, "$"));
    return { text: out.join(""), warnings: opts.warnings, formulas: segments };
  }

  // ------------------------------------------------------------------ HTML
  // Zwischendarstellung (Option html) -> HTML mit <i>, <sub>, <sup>.
  // Brüche und Wurzeln linear, weil Word, E-Mail-Programme und Editoren
  // gestapelte Formeln aus HTML nicht zuverlässig übernehmen.
  const escHTML = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const stripTags = (h) => h.replace(/<[^>]*>/g, "").replace(/&[a-z]+;/g, "x");
  const simpleHTML = (h) => /^[\p{L}\p{N}\p{M}∂′.]+$/u.test(stripTags(h));
  function richToHTML(str) {
    const ch = cps(str);
    let i = 0;
    function seq() {
      let out = "";
      while (i < ch.length) {
        const c = ch[i];
        if (c === MK.end) { i++; return out; }
        if (c === MK.mid) return out;
        i++;
        if (c === MK.sub || c === MK.under) out += "<sub>" + seq() + "</sub>";
        else if (c === MK.sup || c === MK.over || c === MK.rootidx) out += "<sup>" + seq() + "</sup>";
        else if (c === MK.it) out += "<i>" + seq() + "</i>";
        else if (c === MK.delim) out += seq();
        else if (c === MK.sqrt) { const b = seq(); out += "√" + (simpleHTML(b) ? b : "(" + b + ")"); }
        else if (c === MK.frac || c === MK.binom) {
          const n = seq(); if (ch[i] === MK.mid) i++; const d = seq();
          out += c === MK.frac
            ? (simpleHTML(n) ? n : "(" + n + ")") + "/" + (simpleHTML(d) ? d : "(" + d + ")")
            : "C(" + n + ", " + d + ")";
        } else if (c === "\n") out += "<br>";
        else out += escHTML(c);
      }
      return out;
    }
    let html = "";
    while (i < ch.length) { html += seq(); if (i < ch.length) i++; }
    return html.replace(/<\/i><i>/g, "").replace(/<\/sub><sub>/g, "").replace(/<\/sup><sup>/g, "");
  }

  function toHTML(src, o, textMode) {
    const opts = Object.assign({}, o, { html: true });
    const r = textMode ? convertText(src, opts) : convert(src, opts);
    return richToHTML(r.text);
  }

  const api = { convert, convertText, toHTML, richToHTML, styled, MARKERS: MK, VERSION: T.VERSION };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.L2U = api;
})(typeof window !== "undefined" ? window : globalThis);
