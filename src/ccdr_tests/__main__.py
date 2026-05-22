"""CLI entry point: `python -m ccdr_tests run [--pid PID] [--report-only]`."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from .core.data_cache import DataCache
from .core.registry import load_all
from .core.runner import Context, run_battery, write_lock_files
from .report.render_markdown import render_summary
from .report.render_html import render_html


def main(argv: list | None = None) -> int:
    p = argparse.ArgumentParser("ccdr-tests")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="run the full Tier-A battery")
    p_run.add_argument("--pid", action="append", help="restrict to one or more PIDs")
    p_run.add_argument("--reports-dir", default="reports")
    p_run.add_argument("-v", "--verbose", action="store_true")

    p_lock = sub.add_parser("lock", help="(re)write decision-rule lock files")

    p_list = sub.add_parser("list", help="list all registered tests")

    args = p.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if getattr(args, "verbose", False) else logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    if args.cmd == "list":
        for pid, (pred, _) in load_all().items():
            print(f"{pid:6s} [{pred.tier.value}] {pred.one_liner}")
        return 0

    if args.cmd == "lock":
        write_lock_files(Path(__file__).resolve().parents[2] / "specs" / "tier_a")
        print("wrote lock files")
        return 0

    if args.cmd == "run":
        ctx = Context(cache=DataCache(), logger=logging.getLogger("ccdr"))
        results = run_battery(args.pid, ctx)
        reports_dir = Path(args.reports_dir)
        reports_dir.mkdir(parents=True, exist_ok=True)

        # JSON
        registry = load_all()
        predictions = {pid: pred.to_dict() for pid, (pred, _) in registry.items()}
        machine = {
            "predictions": predictions,
            "results": [r.to_dict() for r in results],
        }
        (reports_dir / "machine_readable.json").write_text(json.dumps(machine, indent=2, default=str))
        (reports_dir / "summary.md").write_text(render_summary(results, predictions))
        (reports_dir / "full_report.html").write_text(render_html(results, predictions))
        print(f"wrote {reports_dir}/summary.md, full_report.html, machine_readable.json")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
