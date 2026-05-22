"""Markdown summary table."""

from __future__ import annotations


def _fmt(v) -> str:
    if v is None:
        return "—"
    if isinstance(v, (list, tuple)):
        return "[" + ", ".join(_fmt(x) for x in v) + "]"
    if isinstance(v, float):
        if v == 0:
            return "0"
        if abs(v) < 1e-3 or abs(v) >= 1e4:
            return f"{v:.2e}"
        return f"{v:.4g}"
    return str(v)


def render_summary(results, predictions) -> str:
    rows = sorted(results, key=lambda r: (predictions[r.pid]["domain"], r.pid))
    lines = [
        "# CCDR Tier-A Battery — Summary",
        "",
        "BH-FDR q-values are computed across the executed battery; verdicts of",
        "SUPPORTED with q > 0.10 are downgraded to INCONCLUSIVE.",
        "",
        "| PID | Domain | Verdict | Observed | Predicted | p | q | Retrofit | Notes |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    counts: dict[str, int] = {}
    for r in rows:
        pred = predictions[r.pid]
        counts[r.verdict.value] = counts.get(r.verdict.value, 0) + 1
        notes = "; ".join(r.caveats)[:200]
        lines.append(
            "| {pid} | {domain} | {verdict} | {obs} | {pred} | {p} | {q} | {risk} | {notes} |".format(
                pid=r.pid,
                domain=pred["domain"],
                verdict=r.verdict.value,
                obs=_fmt(r.effect_observed),
                pred=_fmt(r.effect_predicted),
                p=_fmt(r.p_value),
                q=_fmt(r.q_value),
                risk=pred["retrofit_risk"],
                notes=notes,
            )
        )
    lines += ["", "## Verdict counts", ""]
    for v in ("supported", "retrofit_consistent", "refuted", "inconclusive", "error"):
        lines.append(f"- **{v}**: {counts.get(v, 0)}")
    lines.append("")
    lines.append("## Per-test methodology")
    lines.append("")
    for r in rows:
        lines.append(f"### {r.pid} — {predictions[r.pid]['one_liner']}")
        lines.append("")
        lines.append(r.methodology)
        if r.data_sources_used:
            lines.append("")
            lines.append("**Data sources used:** " + ", ".join(r.data_sources_used))
        if r.caveats:
            lines.append("")
            lines.append("**Caveats:**")
            for c in r.caveats:
                lines.append(f"- {c}")
        lines.append("")
    return "\n".join(lines)
