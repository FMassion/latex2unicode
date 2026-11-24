/*
 * render.js – Bild-Export (SVG/PNG) mit echten Hoch- und Tiefstellungen,
 * gestapelten Brüchen, Wurzelstrich und Grenzen unter/über Operatoren.
 *
 * Eingabe: Zwischendarstellung aus L2U.convert(latex, {rich: true}).text
 * Ausgabe: SVG-Text. Für PNG zeichnet die App das SVG auf ein Canvas.
 *
 * Das Layout ist eine vereinfachte Nachbildung des TeX-Satzes, keine
 * TeX-Engine. Maße in Vielfachen der Schriftgröße.
 */
(function (root) {
  "use strict";
  const MK = {
    sub: "\uE000", sup: "\uE001", end: "\uE002", frac: "\uE003", mid: "\uE004",
    under: "\uE005", over: "\uE006", sqrt: "\uE007", rootidx: "\uE008", binom: "\uE009",
    delim: "\uE00A", it: "\uE00B",
  };
  const OPENERS = {
    [MK.sub]: "sub", [MK.sup]: "sup", [MK.under]: "under", [MK.over]: "over",
    [MK.sqrt]: "sqrt", [MK.rootidx]: "rootidx", [MK.frac]: "frac", [MK.binom]: "binom",
    [MK.delim]: "delim",
  };
  const SCRIPT_KINDS = ["sub", "sup", "under", "over"];
  const DEFAULT_FAMILY = "'STIX Two Math','Cambria Math','Latin Modern Math','STIX Two Text','Times New Roman',serif";

  // ---------------------------------------------------------------- Parser
  function parse(str) {
    const ch = Array.from(str);
    let i = 0;
    function seq() {
      const items = [];
      let buf = "";
      const flush = () => { if (buf) { items.push({ t: "text", s: buf }); buf = ""; } };
      while (i < ch.length) {
        const c = ch[i];
        if (c === MK.end) { i++; flush(); return items; }
        if (c === MK.mid) { flush(); return items; }
        if (OPENERS[c]) {
          i++; flush();
          const kind = OPENERS[c];
          if (kind === "frac" || kind === "binom") {
            const n = seq();
            if (ch[i] === MK.mid) i++;
            const d = seq();
            items.push({ t: kind, n, d });
          } else {
            items.push({ t: kind, c: seq() });
          }
          continue;
        }
        if (c === "\n") { flush(); items.push({ t: "nl" }); i++; continue; }
        buf += c; i++;
      }
      flush();
      return items;
    }
    const all = [];
    while (i < ch.length) {
      for (const it of seq()) all.push(it);
      if (i < ch.length) i++; // verwaistes Steuerzeichen überspringen
    }
    return all;
  }

  // ---------------------------------------------------------------- Layout
  // Box: { w, a (über Grundlinie), d (unter Grundlinie), ops: [...] }, y nach unten positiv
  const place = (box, dx, dy) => box.ops.map((op) => {
    const o = Object.assign({}, op);
    if (o.k === "t") { o.x += dx; o.y += dy; }
    else if (o.k === "p") { o.pts = o.pts.map(([x, y]) => [x + dx, y + dy]); }
    return o;
  });
  const emptyBox = () => ({ w: 0, a: 0, d: 0, ops: [] });

  function hcat(boxes) {
    let x = 0, a = 0, d = 0;
    const ops = [];
    for (const b of boxes) {
      ops.push(...place(b, x, 0));
      x += b.w; a = Math.max(a, b.a); d = Math.max(d, b.d);
    }
    return { w: x, a, d, ops };
  }

  function makeLayout(measure) {
    // Leerzeichen als geschützte Leerzeichen, damit SVG sie nicht zusammenfasst
    const textBox = (s, size) => {
      s = s.replace(/ /g, "\u00A0");
      return { w: measure(s, size), a: 0.72 * size, d: 0.24 * size, ops: [{ k: "t", x: 0, y: 0, s, size }] };
    };

    function seqBox(items, size) {
      const boxes = [];
      for (let k = 0; k < items.length; k++) {
        const it = items[k];
        if (it.t === "text") {
          const next = items[k + 1];
          if (next && (next.t === "under" || next.t === "over")) {
            // Grenzen gehören nur zum letzten Wort (z. B. „∑“ oder „lim“)
            const m = it.s.match(/^([\s\S]*\s)?(\S+)$/u);
            if (m && m[1]) boxes.push(textBox(m[1], size));
            boxes.push(textBox(m ? m[2] : it.s, size));
          } else {
            boxes.push(textBox(it.s, size));
          }
        } else if (it.t === "frac" || it.t === "binom") {
          boxes.push(fracBox(it, size));
        } else if (it.t === "sqrt") {
          boxes.push(sqrtBox(it.c, size));
        } else if (it.t === "rootidx") {
          const ib = seqBox(it.c, size * 0.55);
          const kern = Math.min(ib.w, 0.3 * size);
          boxes.push({ w: ib.w - kern, a: 0.5 * size + ib.a, d: 0, ops: place(ib, 0, -0.5 * size) });
        } else if (SCRIPT_KINDS.includes(it.t)) {
          const sc = {};
          while (k < items.length && SCRIPT_KINDS.includes(items[k].t)) { sc[items[k].t] = items[k].c; k++; }
          k--;
          boxes.push(scriptBox(boxes.pop() || emptyBox(), sc, size));
        } else if (it.t === "delim") {
          const glyph = it.c.map((x) => x.s || "").join("");
          boxes.push({ delim: glyph, w: 0, a: 0, d: 0, ops: [] });
        }
      }
      // Begrenzer (\left, \right) auf die Höhe des übrigen Inhalts skalieren
      let ma = 0.72 * size, md = 0.24 * size;
      for (const b of boxes) if (!b.delim) { ma = Math.max(ma, b.a); md = Math.max(md, b.d); }
      for (let k = 0; k < boxes.length; k++) {
        const b = boxes[k];
        if (!b.delim) continue;
        const S = Math.max(size, (ma + md) * 1.02);
        const y = (md - ma) / 2 + 0.25 * S;
        const tb = textBox(b.delim, S);
        boxes[k] = { w: tb.w, a: Math.max(ma, -y + 0.75 * S), d: Math.max(md, y + 0.25 * S), ops: place(tb, 0, y) };
      }
      return hcat(boxes);
    }

    function scriptBox(base, sc, size) {
      const ss = size * 0.7;
      let box = base;
      if (sc.under || sc.over) {
        const u = sc.under ? seqBox(sc.under, ss) : null;
        const o = sc.over ? seqBox(sc.over, ss) : null;
        const W = Math.max(box.w, u ? u.w : 0, o ? o.w : 0);
        const ops = place(box, (W - box.w) / 2, 0);
        let a = box.a, d = box.d;
        if (u) { const y = box.d + 0.08 * size + u.a; ops.push(...place(u, (W - u.w) / 2, y)); d = y + u.d; }
        if (o) { const y = -(box.a + 0.08 * size + o.d); ops.push(...place(o, (W - o.w) / 2, y)); a = -y + o.a; }
        box = { w: W, a, d, ops };
      }
      if (sc.sub || sc.sup) {
        const sb = sc.sub ? seqBox(sc.sub, ss) : null;
        const sp = sc.sup ? seqBox(sc.sup, ss) : null;
        const x = box.w + 0.04 * size;
        const ops = box.ops.slice();
        let a = box.a, d = box.d, W = box.w;
        if (sp) { const y = -0.42 * size; ops.push(...place(sp, x, y)); a = Math.max(a, -y + sp.a); W = Math.max(W, x + sp.w); }
        if (sb) { const y = sp ? 0.3 * size : 0.24 * size; ops.push(...place(sb, x, y)); d = Math.max(d, y + sb.d); W = Math.max(W, x + sb.w); }
        box = { w: W, a, d, ops };
      }
      return box;
    }

    function fracBox(it, size) {
      const fs = size * 0.85;
      const n = seqBox(it.n, fs), dd = seqBox(it.d, fs);
      const pad = 0.12 * size, axis = 0.26 * size, gap = 0.14 * size, th = Math.max(1, 0.05 * size);
      const inner = Math.max(n.w, dd.w) + 2 * pad;
      const ops = [];
      const yn = -axis - gap - n.d, yd = -axis + gap + dd.a;
      let x0 = 0.06 * size;
      const a = axis + gap + n.d + n.a, d = -axis + gap + dd.a + dd.d;
      if (it.t === "binom") {
        const pw = 0.25 * size;
        ops.push({ k: "p", pts: [[x0 + pw, -a], [x0, (d - a) / 2], [x0 + pw, d]], curve: true, th });
        x0 += pw;
      }
      ops.push(...place(n, x0 + (inner - n.w) / 2, yn));
      ops.push(...place(dd, x0 + (inner - dd.w) / 2, yd));
      if (it.t === "frac") ops.push({ k: "p", pts: [[x0, -axis], [x0 + inner, -axis]], th });
      let w = x0 + inner;
      if (it.t === "binom") {
        const pw = 0.25 * size;
        ops.push({ k: "p", pts: [[w, -a], [w + pw, (d - a) / 2], [w, d]], curve: true, th });
        w += pw;
      }
      return { w: w + 0.06 * size, a: a + 0.04 * size, d: d + 0.04 * size, ops };
    }

    function sqrtBox(items, size) {
      const body = seqBox(items, size);
      const th = Math.max(1, 0.05 * size);
      const top = -(Math.max(body.a, 0.72 * size) + 0.1 * size);
      const bot = Math.max(body.d, 0.2 * size);
      const rw = 0.5 * size;
      const ops = [{ k: "p", pts: [[0, -0.28 * size], [0.1 * size, -0.34 * size], [0.24 * size, bot], [rw, top], [rw + body.w + 0.08 * size, top]], th }];
      ops.push(...place(body, rw + 0.04 * size, 0));
      return { w: rw + body.w + 0.12 * size, a: -top + th, d: bot + th, ops };
    }

    function layout(str, size) {
      const items = parse(str);
      const lines = [[]];
      for (const it of items) { if (it.t === "nl") lines.push([]); else lines[lines.length - 1].push(it); }
      const boxes = lines.map((l) => seqBox(l, size));
      let y = 0, w = 0;
      const ops = [];
      boxes.forEach((b, idx) => {
        y += (idx === 0 ? 0 : 0.35 * size) + Math.max(b.a, 0.72 * size);
        ops.push(...place(b, 0, y));
        y += Math.max(b.d, 0.24 * size);
        w = Math.max(w, b.w);
      });
      return { w, h: y, ops };
    }
    return layout;
  }

  // ---------------------------------------------------------------- SVG
  const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const r2 = (v) => Math.round(v * 100) / 100;

  function browserMeasure(family) {
    const cv = (typeof document !== "undefined") ? document.createElement("canvas") : null;
    const ctx = cv ? cv.getContext("2d") : null;
    return (s, size) => {
      if (!ctx) return Array.from(s).length * size * 0.55;
      ctx.font = size + "px " + family;
      return ctx.measureText(s).width;
    };
  }

  function toSVG(str, o) {
    o = o || {};
    const size = o.size || 48;
    const family = o.family || DEFAULT_FAMILY;
    const color = o.color || "#000";
    const bg = o.background === undefined ? "#fff" : o.background;
    const pad = o.padding === undefined ? 0.4 * size : o.padding;
    const measure = o.measure || browserMeasure(family);
    const L = makeLayout(measure)(str, size);
    const W = Math.ceil(L.w + 2 * pad), H = Math.ceil(L.h + 2 * pad);
    const parts = [];
    parts.push('<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" width="' + W + '" height="' + H +
      '" viewBox="0 0 ' + W + " " + H + '">');
    if (bg) parts.push('<rect width="100%" height="100%" fill="' + bg + '"/>');
    parts.push('<g fill="' + color + '" stroke="' + color + '" font-family="' + esc(family).replace(/"/g, "&quot;") +
      '" style="white-space:pre">');
    for (const op of L.ops) {
      if (op.k === "t") {
        parts.push('<text x="' + r2(op.x + pad) + '" y="' + r2(op.y + pad) + '" font-size="' + r2(op.size) +
          '" stroke="none">' + esc(op.s) + "</text>");
      } else if (op.k === "p") {
        const pts = op.pts.map(([x, y]) => [r2(x + pad), r2(y + pad)]);
        const d = op.curve
          ? "M" + pts[0].join(" ") + " Q" + pts[1].join(" ") + " " + pts[2].join(" ")
          : "M" + pts.map((p) => p.join(" ")).join(" L");
        parts.push('<path d="' + d + '" fill="none" stroke-width="' + r2(op.th) +
          '" stroke-linejoin="round" stroke-linecap="round"/>');
      }
    }
    parts.push("</g></svg>");
    return parts.join("");
  }

  const api = { toSVG, parse, makeLayout, DEFAULT_FAMILY };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.L2URender = api;
})(typeof window !== "undefined" ? window : globalThis);
