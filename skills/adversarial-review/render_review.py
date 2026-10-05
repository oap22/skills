#!/usr/bin/env python3
"""Render a review record (JSON) as one self-contained HTML page with severity-coloured findings.

Usage: python3 render_review.py review.json --out review.html

Input fields (only `title` and `findings` are required):
  title         page heading
  scope         what was reviewed; out_of_scope: list of strings
  tests         list of {command, result: green|red|not-run, excerpt}
  findings      list of {severity, claim, location, lens, scenario, status, converged}
                severity: critical | high | medium | low | suggestion
                status:   open | fixed | discarded | out-of-scope (default open)
  sections      list of {heading, items: [str]} for extra blocks (spec fidelity, progress)
  notes         free text shown last
Standard library only. Every string is HTML-escaped.
"""
import argparse
import html
import json
from pathlib import Path
import sys

SEVERITIES = ('critical', 'high', 'medium', 'low', 'suggestion')
STATUSES = ('open', 'fixed', 'discarded', 'out-of-scope')
RESULTS = ('green', 'red', 'not-run')

CSS = """
:root{--bg:#fff;--fg:#1d1d1f;--muted:#5f6368;--card:#f6f7f9;--line:#d9dce1;
--critical:#c62828;--high:#e65100;--medium:#b58100;--low:#1565c0;--suggestion:#546e7a;--green:#2e7d32;--red:#c62828}
@media (prefers-color-scheme:dark){:root{--bg:#141517;--fg:#e8eaed;--muted:#9aa0a6;--card:#1f2124;--line:#34373c;
--critical:#ef5350;--high:#ff8a3d;--medium:#e0b000;--low:#64b5f6;--suggestion:#90a4ae;--green:#66bb6a;--red:#ef5350}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 -apple-system,system-ui,sans-serif}
main{max-width:980px;margin:0 auto;padding:24px 16px}h1{font-size:22px;margin:0 0 4px}h2{font-size:17px;margin:28px 0 8px}
.muted{color:var(--muted)}.counts{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}
.chip{display:inline-block;padding:2px 10px;border-radius:999px;color:#fff;font-size:12px;font-weight:600;text-transform:uppercase}
.finding{background:var(--card);border:1px solid var(--line);border-left:6px solid var(--sev);border-radius:8px;padding:12px 14px;margin:10px 0}
.finding.closed{opacity:.6}.meta{display:flex;flex-wrap:wrap;gap:8px;align-items:center;font-size:13px}
.claim{margin:6px 0 0;font-weight:600}.scenario{margin:6px 0 0}code,pre{font:13px/1.4 ui-monospace,Menlo,monospace}
pre{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px;overflow-x:auto;white-space:pre-wrap}
ul{padding-left:20px}
"""


def fail(message):
    print(f'render_review: {message}', file=sys.stderr)
    raise SystemExit(2)


def esc(value):
    return html.escape(str(value), quote=True)


def validate(data):
    if not isinstance(data, dict) or not str(data.get('title', '')).strip():
        fail('input needs a nonempty "title"')
    findings = data.get('findings')
    if not isinstance(findings, list):
        fail('"findings" must be a list (use [] when nothing survived)')
    for i, f in enumerate(findings):
        if f.get('severity') not in SEVERITIES:
            fail(f'finding {i}: severity must be one of {", ".join(SEVERITIES)}')
        if not str(f.get('claim', '')).strip():
            fail(f'finding {i}: "claim" is required')
        if f.get('status', 'open') not in STATUSES:
            fail(f'finding {i}: status must be one of {", ".join(STATUSES)}')
    for i, t in enumerate(data.get('tests', [])):
        if t.get('result') not in RESULTS:
            fail(f'test {i}: result must be one of {", ".join(RESULTS)}')


def chip(label, colour_var):
    return f'<span class="chip" style="background:var(--{colour_var})">{esc(label)}</span>'


def render(data):
    validate(data)
    findings = sorted(data['findings'], key=lambda f: SEVERITIES.index(f['severity']))
    out = ['<!doctype html><html lang="en"><head><meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width,initial-scale=1">',
           f'<title>{esc(data["title"])}</title><style>{CSS}</style></head><body><main>',
           f'<h1>{esc(data["title"])}</h1>']
    if data.get('scope'):
        out.append(f'<p class="muted">Scope: {esc(data["scope"])}</p>')
    open_counts = {s: sum(1 for f in findings if f['severity'] == s and f.get('status', 'open') == 'open') for s in SEVERITIES}
    out.append('<div class="counts">' + ''.join(chip(f'{n} {s}', s) for s, n in open_counts.items() if n) +
               ('' if any(open_counts.values()) else chip('no open findings', 'green')) + '</div>')
    if data.get('tests'):
        out.append('<h2>Tests</h2>')
        for t in data['tests']:
            colour = {'green': 'green', 'red': 'red'}.get(t['result'], 'suggestion')
            out.append(f'<div class="meta">{chip(t["result"], colour)} <code>{esc(t.get("command", ""))}</code></div>')
            if t.get('excerpt'):
                out.append(f'<pre>{esc(t["excerpt"])}</pre>')
    out.append('<h2>Findings</h2>')
    if not findings:
        out.append('<p class="muted">Nothing survived the failure-scenario bar.</p>')
    for f in findings:
        status = f.get('status', 'open')
        meta = [chip(f['severity'], f['severity']), f'<span>{esc(status)}</span>']
        if f.get('location'):
            meta.append(f'<code>{esc(f["location"])}</code>')
        if f.get('lens'):
            meta.append(f'<span class="muted">lens: {esc(f["lens"])}</span>')
        if f.get('converged'):
            meta.append('<span class="muted">converged</span>')
        closed = ' closed' if status != 'open' else ''
        out.append(f'<div class="finding{closed}" style="--sev:var(--{f["severity"]})"><div class="meta">{" ".join(meta)}</div>'
                   f'<p class="claim">{esc(f["claim"])}</p>' +
                   (f'<p class="scenario">{esc(f["scenario"])}</p>' if f.get('scenario') else '') + '</div>')
    if data.get('out_of_scope'):
        out.append('<h2>Out of scope</h2><ul>' + ''.join(f'<li>{esc(x)}</li>' for x in data['out_of_scope']) + '</ul>')
    for section in data.get('sections', []):
        out.append(f'<h2>{esc(section.get("heading", ""))}</h2><ul>' +
                   ''.join(f'<li>{esc(x)}</li>' for x in section.get('items', [])) + '</ul>')
    if data.get('notes'):
        out.append(f'<h2>Notes</h2><p>{esc(data["notes"])}</p>')
    out.append('</main></body></html>\n')
    return '\n'.join(out)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('record', type=Path, help='review record JSON')
    parser.add_argument('--out', type=Path, required=True, help='HTML file to write')
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.record.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f'cannot read {args.record}: {exc}')
    page = render(data)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(page, encoding='utf-8')
    print(args.out)


if __name__ == '__main__':
    main()
