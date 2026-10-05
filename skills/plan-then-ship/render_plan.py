#!/usr/bin/env python3
"""Render a plan record (JSON) as one self-contained HTML page with the approaches side by side.

Usage: python3 render_plan.py plan.json --out plan.html

Input fields (only `title` and `approaches` are required):
  title         page heading
  goal          one or two sentences
  approaches    list of {name, summary, pros: [str], cons: [str], cost, chosen: bool}
                zero or one may be chosen; zero means the choice is still Owen's
  decisions     list of str: routine calls the planner made itself (Owen can veto)
  assumptions   list of str: consequential assumptions awaiting approval
  acceptance    list of str: acceptance criteria copied from the spec
  spec_path     path to SPEC.md, shown as the source of truth
Standard library only. Every string is HTML-escaped. SPEC.md stays the implementer's contract.
"""
import argparse
import html
import json
from pathlib import Path
import sys

CSS = """
:root{--bg:#fff;--fg:#1d1d1f;--muted:#5f6368;--card:#f6f7f9;--line:#d9dce1;--accent:#2e7d32;--pro:#2e7d32;--con:#c62828}
@media (prefers-color-scheme:dark){:root{--bg:#141517;--fg:#e8eaed;--muted:#9aa0a6;--card:#1f2124;--line:#34373c;--accent:#66bb6a;--pro:#66bb6a;--con:#ef5350}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 -apple-system,system-ui,sans-serif}
main{max-width:1180px;margin:0 auto;padding:24px 16px}h1{font-size:22px;margin:0 0 4px}h2{font-size:17px;margin:28px 0 8px}
.muted{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px}
.card.chosen{border:2px solid var(--accent)}.badge{float:right;font-size:12px;font-weight:700;color:var(--accent);text-transform:uppercase}
.card h3{margin:0 0 6px;font-size:16px}.pros li::marker{content:"+ ";color:var(--pro)}.cons li::marker{content:"− ";color:var(--con)}
ul{padding-left:20px;margin:6px 0}code{font:13px/1.4 ui-monospace,Menlo,monospace}
"""


def fail(message):
    print(f'render_plan: {message}', file=sys.stderr)
    raise SystemExit(2)


def esc(value):
    return html.escape(str(value), quote=True)


def validate(data):
    if not isinstance(data, dict) or not str(data.get('title', '')).strip():
        fail('input needs a nonempty "title"')
    approaches = data.get('approaches')
    if not isinstance(approaches, list) or not approaches:
        fail('"approaches" must list at least one approach')
    for i, a in enumerate(approaches):
        if not isinstance(a, dict) or not str(a.get('name', '')).strip():
            fail(f'approach {i}: needs an object with a "name"')
        for key in ('pros', 'cons'):
            if not isinstance(a.get(key, []), list):
                fail(f'approach {i}: "{key}" must be a list')
    for key in ('decisions', 'assumptions', 'acceptance'):
        if not isinstance(data.get(key, []), list):
            fail(f'"{key}" must be a list')
    if sum(1 for a in approaches if a.get('chosen')) > 1:
        fail('at most one approach may be chosen')


def bullets(items, cls=''):
    if not items:
        return ''
    return f'<ul class="{cls}">' + ''.join(f'<li>{esc(x)}</li>' for x in items) + '</ul>'


def render(data):
    validate(data)
    chosen = next((a['name'] for a in data['approaches'] if a.get('chosen')), None)
    out = ['<!doctype html><html lang="en"><head><meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width,initial-scale=1">',
           f'<title>{esc(data["title"])}</title><style>{CSS}</style></head><body><main>',
           f'<h1>{esc(data["title"])}</h1>']
    if data.get('goal'):
        out.append(f'<p>{esc(data["goal"])}</p>')
    if data.get('spec_path'):
        out.append(f'<p class="muted">Contract: <code>{esc(data["spec_path"])}</code>. This page is a view of it; the spec wins on any difference.</p>')
    out.append('<h2>Approaches</h2>')
    out.append(f'<p class="muted">{"Chosen: " + esc(chosen) if chosen else "No approach chosen yet: this choice is waiting on Owen."}</p>')
    out.append('<div class="grid">')
    for a in data['approaches']:
        cls = ' chosen' if a.get('chosen') else ''
        badge = '<span class="badge">chosen</span>' if a.get('chosen') else ''
        out.append(f'<section class="card{cls}">{badge}<h3>{esc(a["name"])}</h3>' +
                   (f'<p>{esc(a["summary"])}</p>' if a.get('summary') else '') +
                   bullets(a.get('pros', []), 'pros') + bullets(a.get('cons', []), 'cons') +
                   (f'<p class="muted">Cost: {esc(a["cost"])}</p>' if a.get('cost') else '') + '</section>')
    out.append('</div>')
    for key, heading in (('assumptions', 'Assumptions awaiting approval'),
                         ('decisions', 'Decided without asking (veto any)'),
                         ('acceptance', 'Acceptance criteria')):
        if data.get(key):
            out.append(f'<h2>{heading}</h2>' + bullets(data[key]))
    out.append('</main></body></html>\n')
    return '\n'.join(out)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('record', type=Path, help='plan record JSON')
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
