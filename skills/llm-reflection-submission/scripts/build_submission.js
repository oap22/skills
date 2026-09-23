#!/usr/bin/env node
// Build a Canvas-ready .docx for an LLM code-reflection assignment from a JSON spec.
// Usage: node build_submission.js spec.json
// See ../SKILL.md and ../spec-example.json. Paths in the spec resolve from the spec's folder.
const fs = require('fs');
const path = require('path');
let docx;
try { docx = require('docx'); } catch (e) {
  console.error('The "docx" npm package is not installed. Run: npm install docx (in a scratch folder, then run this script from there or set NODE_PATH).');
  process.exit(2);
}
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  LevelFormat, BorderStyle, ShadingType, Footer, PageNumber,
  Table, TableRow, TableCell, WidthType, LineRuleType,
} = docx;

const BODY = 'Calibri';
let LIST_INSTANCE = 0;
const LIST_CONFIGS = [];
const MONO = 'Consolas';

// ---------- inline markdown (state machine) ----------
function inline(text, base = {}) {
  const runs = [];
  let st = { bold: false, italics: false, code: false, hl: false, url: false };
  let buf = '';
  const flush = () => {
    if (!buf) return;
    const o = { text: buf, ...base };
    if (st.bold) o.bold = true;
    if (st.italics) o.italics = true;
    if (st.hl) o.highlight = 'yellow';
    if (st.url) o.color = '1F4E79';
    if (st.code) { o.font = MONO; o.size = 20; }
    runs.push(new TextRun(o)); buf = '';
  };
  for (let i = 0; i < text.length; i++) {
    const c = text[i], n = text[i + 1];
    if (c === '`') { flush(); st.code = !st.code; continue; }
    if (st.code) { buf += c; continue; }
    if (c === '*' && n === '*') { flush(); st.bold = !st.bold; i++; continue; }
    if (c === '=' && n === '=') { flush(); st.hl = !st.hl; i++; continue; }
    if (c === '<' && text.startsWith('http', i + 1)) { flush(); st.url = true; continue; }
    if (c === '>' && st.url) { flush(); st.url = false; continue; }
    if (c === '*') {
      // italic toggle only when it looks like emphasis, not math like "x * y"
      const opening = !st.italics && n && n !== ' ';
      const closing = st.italics && text[i - 1] && text[i - 1] !== ' ';
      if (opening || closing) { flush(); st.italics = !st.italics; continue; }
    }
    buf += c;
  }
  flush();
  return runs;
}

// ---------- code block ----------
// One-cell table that cannot split across pages. Long lines wrap with a hanging
// indent so the continuation sits under the code, not at the left margin.
const CODE_SIZE = 15;          // half-points (7.5pt)
const CHAR_TW = 83;            // Consolas 7.5pt advance, in twips
function codeBlock(lines, opts = {}) {
  const numbered = !!opts.lineNumbers;
  const gutter = numbered ? String(lines.length).length + 2 : 0;
  const paras = lines.map((ln, i) => {
    const lead = ln.match(/^ */)[0].length;
    const hang = (gutter + lead + 4) * CHAR_TW;
    const runs = [];
    if (numbered) runs.push(new TextRun({ text: String(i + 1).padStart(gutter - 2, ' ') + '  ', font: MONO, size: CODE_SIZE, color: '9A9A9A' }));
    runs.push(new TextRun({ text: ln.length ? ln : ' ', font: MONO, size: CODE_SIZE }));
    return new Paragraph({
      children: runs,
      spacing: { before: 0, after: 0, line: 176, lineRule: LineRuleType.EXACT },
      indent: { left: hang, hanging: hang },
      keepLines: true,
      ...(i < lines.length - 1 ? { keepNext: true } : {}),
    });
  });
  const border = { style: BorderStyle.SINGLE, size: 4, color: 'C8C8C8' };
  return [
    new Table({
      width: { size: 9360, type: WidthType.DXA },
      columnWidths: [9360],
      borders: { top: border, bottom: border, left: border, right: border,
                 insideHorizontal: { style: BorderStyle.NONE }, insideVertical: { style: BorderStyle.NONE } },
      rows: [new TableRow({ cantSplit: true, children: [new TableCell({
        width: { size: 9360, type: WidthType.DXA },
        shading: { type: ShadingType.CLEAR, color: 'auto', fill: 'F5F5F5' },
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        children: paras,
      })] })],
    }),
    new Paragraph({ children: [], spacing: { before: 0, after: 120 } }),
  ];
}

// ---------- block markdown ----------
function md(src, headingShift = 0) {
  const out = [];
  const lines = src.replace(/\r/g, '').split('\n');
  let i = 0;
  const hl = [HeadingLevel.HEADING_1, HeadingLevel.HEADING_2, HeadingLevel.HEADING_3, HeadingLevel.HEADING_4];
  while (i < lines.length) {
    let line = lines[i];
    if (!line.trim()) { i++; continue; }
    // fenced code
    if (line.trim().startsWith('```')) {
      const buf = []; i++;
      while (i < lines.length && !lines[i].trim().startsWith('```')) { buf.push(lines[i]); i++; }
      i++;
      out.push(...codeBlock(buf));
      continue;
    }
    // heading
    let h = line.match(/^(#{1,4})\s+(.*)$/);
    if (h) {
      const lvl = Math.min(h[1].length - 1 + headingShift, 3);
      out.push(new Paragraph({ heading: hl[lvl], children: inline(h[2]) }));
      i++; continue;
    }
    // list
    let li = line.match(/^(\s*)([-*]|\d+\.)\s+(.*)$/);
    if (li) {
      const listInst = ++LIST_INSTANCE;
      const ref = 'list' + listInst;
      const topNumbered = /\d+\./.test(li[2]);
      LIST_CONFIGS.push({ reference: ref, levels: [0, 1, 2].map((l) => ({
        level: l,
        format: (l === 0 && topNumbered) ? LevelFormat.DECIMAL : LevelFormat.BULLET,
        text: (l === 0 && topNumbered) ? '%1.' : ['\u2022', '\u25E6', '\u25AA'][l],
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720 + 360 * l, hanging: 360 } } } })) });
      while (i < lines.length) {
        const m = lines[i].match(/^(\s*)([-*]|\d+\.)\s+(.*)$/);
        if (!m) break;
        const level = Math.min(Math.floor(m[1].length / 2), 2);
        let text = m[3]; i++;
        while (i < lines.length && lines[i].trim() && !lines[i].match(/^(\s*)([-*]|\d+\.)\s+/) && /^\s+/.test(lines[i])) {
          text += ' ' + lines[i].trim(); i++;
        }
        out.push(new Paragraph({
          numbering: { reference: ref, level },
          children: inline(text), spacing: { after: 80 },
        }));
        // allow blank lines between numbered items
        if (i < lines.length && !lines[i].trim() && i + 1 < lines.length && lines[i + 1].match(/^(\s*)([-*]|\d+\.)\s+/) && topNumbered) i++;
      }
      continue;
    }
    // paragraph
    let text = line.trim(); i++;
    while (i < lines.length && lines[i].trim() && !lines[i].trim().startsWith('```') &&
           !lines[i].match(/^#{1,4}\s/) && !lines[i].match(/^(\s*)([-*]|\d+\.)\s+/)) {
      text += ' ' + lines[i].trim(); i++;
    }
    let j = i; while (j < lines.length && !lines[j].trim()) j++;
    const beforeCode = (j < lines.length && lines[j].trim().startsWith('```')) || /^\*\*[^*]+\*\*$/.test(text) || /:$/.test(text);
    const pseudoHead = /^\*\*[^*]+\*\*$/.test(text);
    out.push(new Paragraph({ children: inline(text), spacing: { before: pseudoHead ? 180 : 0, after: pseudoHead ? 80 : 140 }, ...(beforeCode ? { keepNext: true } : {}) }));
  }
  return out;
}


// ---------- spec ----------
const specPath = process.argv[2];
if (!specPath) { console.error('Usage: node build_submission.js spec.json'); process.exit(2); }
const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));
const base = path.dirname(path.resolve(specPath));
const resolve = (f) => path.resolve(base, f);
const read = (f) => {
  const p = resolve(f);
  if (!fs.existsSync(p)) { console.error(`Missing file: ${p}`); process.exit(1); }
  return fs.readFileSync(p, 'utf8');
};
const codeLines = (f) => read(f).replace(/\n$/, '').split('\n');
for (const k of ['title', 'author', 'output', 'sections']) {
  if (!spec[k]) { console.error(`Spec is missing "${k}"`); process.exit(1); }
}

const labelBox = (t) => {
  const bd = { style: BorderStyle.SINGLE, size: 8, color: '7F7F7F' };
  return [new Table({
    width: { size: 9360, type: WidthType.DXA }, columnWidths: [9360],
    borders: { top: bd, bottom: bd, left: bd, right: bd, insideHorizontal: { style: BorderStyle.NONE }, insideVertical: { style: BorderStyle.NONE } },
    rows: [new TableRow({ cantSplit: true, children: [new TableCell({
      width: { size: 9360, type: WidthType.DXA },
      shading: { type: ShadingType.CLEAR, color: 'auto', fill: 'EDEDED' },
      margins: { top: 100, bottom: 100, left: 160, right: 160 },
      children: [new Paragraph({ children: [new TextRun({ text: t, bold: true })] })] })] })],
  }), new Paragraph({ children: [], spacing: { after: 120 } })];
};
const h1 = (t, pageBreakBefore) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(t)], ...(pageBreakBefore ? { pageBreakBefore: true } : {}) });

const children = [
  new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun(spec.title)] }),
  new Paragraph({ children: [new TextRun({ text: spec.author, bold: true })], spacing: { after: 40 } }),
  ...(spec.meta || []).map((m) => new Paragraph({ children: [new TextRun(m)], spacing: { after: 40 } })),
  ...(spec.llm ? [new Paragraph({ children: [new TextRun({ text: 'LLM used: ', bold: true }), new TextRun(spec.llm)], spacing: { after: 40 } })] : []),
  ...(spec.note ? [new Paragraph({ children: [new TextRun({ text: spec.note, italics: true, color: '595959' })], spacing: { after: 40 } })] : []),
  new Paragraph({ children: [], spacing: { after: 200 } }),
];

for (const sec of spec.sections) {
  children.push(h1(sec.heading, sec.pageBreakBefore));
  if (sec.type === 'code') {
    children.push(...codeBlock(codeLines(sec.file), { lineNumbers: sec.lineNumbers !== false }));
  } else if (sec.type === 'markdown') {
    children.push(...md(read(sec.file), sec.headingShift || 0));
  } else if (sec.type === 'llm-output') {
    const who = sec.llm || spec.llm || 'the LLM';
    children.push(...labelBox(sec.startLabel || `Written entirely by ${who}. Everything between this box and the "End of LLM output" line is the LLM's exact output, copied and pasted without edits. None of it is my writing.`));
    children.push(...md(read(sec.file), sec.headingShift || 0));
    children.push(...labelBox(sec.endLabel || 'End of LLM output.'));
  } else {
    console.error(`Unknown section type "${sec.type}" (use code, markdown, or llm-output)`); process.exit(1);
  }
}

const doc = new Document({
  creator: spec.author,
  title: spec.title,
  styles: {
    default: { document: { run: { font: BODY, size: 22 } } },
    paragraphStyles: [
      { id: 'Title', name: 'Title', basedOn: 'Normal', next: 'Normal',
        run: { font: BODY, size: 40, bold: true }, paragraph: { spacing: { after: 160 } } },
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: BODY, size: 32, bold: true, color: '1F1F1F' }, paragraph: { spacing: { before: 360, after: 120 }, outlineLevel: 0, keepNext: true, border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: 'BFBFBF', space: 2 } } } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: BODY, size: 26, bold: true, color: '1F1F1F' }, paragraph: { spacing: { before: 280, after: 120 }, outlineLevel: 1, keepNext: true } },
      { id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: BODY, size: 23, bold: true, color: '404040' }, paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 2, keepNext: true } },
      { id: 'Heading4', name: 'Heading 4', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: BODY, size: 22, bold: true, italics: true }, paragraph: { spacing: { before: 160, after: 80 }, outlineLevel: 3, keepNext: true } },
    ],
  },
  numbering: { config: LIST_CONFIGS.length ? LIST_CONFIGS : [{ reference: 'unused', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT }] }] },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1152, bottom: 1152, left: 1440, right: 1440 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
      children: [new TextRun({ text: `${spec.author} · ${spec.footer || spec.title} · `, size: 18, color: '808080' }),
                 new TextRun({ children: [PageNumber.CURRENT], size: 18, color: '808080' })] })] }) },
    children,
  }],
});

const out = resolve(spec.output);
Packer.toBuffer(doc)
  .then((b) => { fs.writeFileSync(out, b); console.log(`Wrote ${out}`); })
  .catch((e) => { console.error(`Failed to write ${out}: ${e && e.stack ? e.stack : e}`); process.exitCode = 1; });
