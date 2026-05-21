# CCDR v7.5 Prediction Test Harness

A reproducible test battery for the public-data-accessible subset of the 83
engineering predictions in *"CCDR/Synthesis v7.5/v3.5 Engineering: Practical
Applications of Spacetime Crystal Physics across Eight Domains"* (April 2026).

## What this is

A Python harness that fetches public datasets (NREL PV efficiency tables,
GWTC-3 gravitational-wave catalogue, NIST thermal-conductivity tabulations,
NAND industry datasheets, Pioneer tracking residuals, etc.), runs a fixed
pre-registered statistical test per prediction, and emits an HTML / Markdown
/ JSON report.

## What this is not

- Not an endorsement of the CCDR framework. The harness is adversarial — it
  applies BH-FDR multiple-testing correction across all 83 predictions and
  flags retrofitted "predictions" (e.g. quoting the known diamond κ
  number as if it were forward inference).
- Not a complete test of the framework. Only ~14 of 83 predictions can be
  tested against current public data; the cosmological core (P39, P40,
  MOND-sequence) needs DESI/LiteBIRD/Euclid pipelines outside scope.

## Quick start

```bash
# Requires Python 3.11+
pip install -e .

# Run the full battery (downloads ~2 GB into data_cache/ on first run)
python -m ccdr_tests run

# Run a single prediction test
python -m ccdr_tests run --pid AE2

# Render report only (no recompute)
python -m ccdr_tests report
```

## Reading the output

`reports/summary.md` has one row per prediction with a verdict:

| Verdict       | Meaning                                            |
|---------------|----------------------------------------------------|
| `SUPPORTED`   | Effect observed at predicted magnitude, p<0.05, q<0.10 |
| `REFUTED`     | Data contradicts prediction at 95 % CL              |
| `INCONCLUSIVE`| Effect direction unclear, or sensitivity too low    |
| `RETROFIT`    | Consistent with data, but data predates / informed prediction |

A `SUPPORTED` verdict on 1–2 out of ~14 tests is expected from chance alone
(α = 0.05). The BH-FDR `q`-column is the load-bearing significance measure.

## Layout

See `CLAUDE.md` for the full architecture spec and per-test methodology.
That file is also the build instructions for Claude Code.

## License

MIT. Underlying datasets retain their original licences; see each test's
result card for citation requirements.
