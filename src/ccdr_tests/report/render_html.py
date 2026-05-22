"""Minimal HTML report."""

from __future__ import annotations

from html import escape

from .render_markdown import _fmt


_TEMPLATE = """<!doctype html>
<html><head><meta charset="utf-8"><title>CCDR Tier-A Report</title>
<style>
body{{font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;max-width:1100px;margin:2em auto;color:#222}}
table{{border-collapse:collapse;width:100%;font-size:14px}}
th,td{{border:1px solid #ccc;padding:6px 8px;vertical-align:top}}
th{{background:#f0f0f0;text-align:left}}
.supported{{background:#d4edda}}
.retrofit_consistent{{background:#fff3cd}}
.refuted{{background:#f8d7da}}
.inconclusive{{background:#e2e3e5}}
.error{{background:#f5c6cb}}
code{{background:#f7f7f7;padding:1px 4px;border-radius:3px}}
.section{{margin:2em 0}}
</style></head><body>
<h1>CCDR Tier-A Battery</h1>
<p>BH-FDR q-values are computed across all executed tests. SUPPORTED with q&gt;0.10 is demoted to INCONCLUSIVE.</p>
{table}
<h2>Verdict counts</h2>
<ul>{counts}</ul>
<h2>Per-test cards</h2>
{cards}
</body></html>"""


def render_html(results, predictions) -> str:
    rows = sorted(results, key=lambda r: (predictions[r.pid]["domain"], r.pid))
    header = (
        "<tr><th>PID</th><th>Domain</th><th>Verdict</th><th>Observed</th>"
        "<th>Predicted</th><th>p</th><th>q</th><th>Retrofit</th><th>n</th></tr>"
    )
    body = []
    counts: dict[str, int] = {}
    for r in rows:
        pred = predictions[r.pid]
        counts[r.verdict.value] = counts.get(r.verdict.value, 0) + 1
        body.append(
            f'<tr class="{r.verdict.value}">'
            f"<td>{r.pid}</td><td>{escape(pred['domain'])}</td><td><b>{r.verdict.value}</b></td>"
            f"<td>{_fmt(r.effect_observed)}</td><td>{_fmt(r.effect_predicted)}</td>"
            f"<td>{_fmt(r.p_value)}</td><td>{_fmt(r.q_value)}</td>"
            f"<td>{pred['retrofit_risk']}</td><td>{r.n}</td></tr>"
        )
    table = f"<table>{header}{''.join(body)}</table>"

    cards = []
    for r in rows:
        pred = predictions[r.pid]
        caveats_html = "".join(f"<li>{escape(c)}</li>" for c in r.caveats) or "<li>(none)</li>"
        ds_html = "".join(f"<li><code>{escape(s)}</code></li>" for s in r.data_sources_used) or "<li>(none)</li>"
        cards.append(f"""
<div class="section">
<h3>{r.pid} — {escape(pred['one_liner'])}</h3>
<p><b>Sharp form:</b> {escape(pred['sharp_form'])}</p>
<p><b>Null:</b> {escape(pred['null_hypothesis'])}</p>
<p><b>Falsification:</b> {escape(pred['falsification_criterion'])}</p>
<p><b>Decision rule:</b> {escape(pred['decision_rule'])}</p>
<p><b>Verdict:</b> <span class="{r.verdict.value}">{r.verdict.value}</span>
   &nbsp; observed={_fmt(r.effect_observed)} {escape(r.effect_unit)}
   &nbsp; predicted={_fmt(r.effect_predicted)}
   &nbsp; p={_fmt(r.p_value)} q={_fmt(r.q_value)} n={r.n}</p>
<p><b>Methodology.</b> {escape(r.methodology)}</p>
<p><b>Data sources used:</b><ul>{ds_html}</ul></p>
<p><b>Caveats:</b><ul>{caveats_html}</ul></p>
</div>""")

    counts_html = "".join(f"<li><b>{k}</b>: {v}</li>" for k, v in sorted(counts.items()))
    return _TEMPLATE.format(table=table, counts=counts_html, cards="".join(cards))
