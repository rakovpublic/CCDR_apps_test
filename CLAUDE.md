# CCDR v7.5 / Synthesis v3.5 — Public-Data Prediction Test Harness

This repository tests the public-data-accessible subset of the **83 predictions** in
`CCDR_Apps_v75_EN.docx` ("CCDR/Synthesis v7.5/v3.5 Engineering"). The goal is to give
each prediction an honest, reproducible pass/fail score against the best public dataset
that bears on it, without overclaiming what such a test proves.

Before writing any code, read this file top to bottom. The triage in §2 determines
what gets built; everything else is implementation detail.

---

## 1. Honest framing — read this first

The CCDR framework is non-mainstream and combines real physics terms (KSS bound,
Kibble–Zurek, holographic codes, skyrmions) in non-standard ways (e.g. dark matter as
"optical phonons" of a cosmic crystal). This program is **not** an endorsement of the
framework. It is a falsification battery: for each prediction we ask only

> *Does the best available public dataset support the predicted effect at the
> predicted magnitude, in a way that could not have been fitted post-hoc?*

Two adversarial pressures must be baked into the harness:

1. **Multiple-testing inflation.** There are 83 predictions. At α = 0.05 we expect
   ≈ 4 spurious "confirmations" by chance. Every per-prediction p-value must be
   reported alongside a Benjamini–Hochberg FDR-adjusted q-value computed across
   the whole executed battery.
2. **Retrofit detection.** Some "predictions" are restatements of known measured
   values (e.g. diamond κ ≈ 3300 W/m/K, Mi et al. 2021 DTC qubit numbers). For
   each test, the spec card below carries a `retrofit_risk` field. A "pass" on a
   retrofitted claim is *not* evidence for the framework — it is evidence the
   author knew the literature. The final report must surface this distinction.

---

## 2. Testability triage (do NOT try to test everything)

The document lists 83 predictions. Triage them into three tiers. **Build tests only
for Tier A.** Tier B goes into the spec library with a `not_implemented` stub
explaining what data would be needed. Tier C is documented and dropped.

### Tier A — implementable now from public data (≈ 14 predictions, the build target)

| ID | One-line claim | Primary public data |
|----|----------------|---------------------|
| QC1 | CDT holographic QEC code distance scales as d ~ N^{1/3} | Simulation only (Stim, PyMatching) |
| QC2 | CDT code outperforms surface code at N > 10⁵ | Simulation only |
| QC3 | CDT threshold p_th ~ 1 % | Simulation only |
| QC4 | CDT superior burst-error protection (RT surface traverses bulk) | Simulation only |
| QC5 | Phononic-crystal-substrate transmon T1 > 1 ms | arXiv / published transmon T1 surveys |
| MAT1 | κ(T) = κ₀(T)·μ(λ/L_grain), μ(x) = x/(1+x)^{1/2}; differs 5–15 % from Casimir | NIST SRD, published low-T κ datasets |
| MAT3 | κ ~ T^{1/2} in nanocrystalline materials at low T (not κ ~ L_grain Casimir) | Same as MAT1 |
| MAT6 | Isotopically pure diamond κ → 3300 W/m/K is the theoretical maximum | Published ¹²C diamond κ measurements (**HIGH RETROFIT RISK**) |
| MAT10 | Kibble–Zurek exponent ν/(1+νz) measurable from grain-size vs cooling-rate scaling | Published EBSD grain-size vs cooling-rate datasets |
| EL1 | 3D-chip throughput scales with inter-layer **area**, not volume (transistor count) | Public 3D NAND datasheets: layer count, die throughput, areal density |
| EN3 | Cosmic-crystal photovoltaic enhancement: ~5–10 % over SQ for Si single-junction, ~15–20 % multi-junction | NREL "Best Research-Cell Efficiency Chart" CSV |
| AE2 | Black-hole ringdown deviation from Kerr ~10⁻³ at first overtone | GWTC-3 (LIGO/Virgo/KAGRA), GWOSC public data |
| AE5 | Pioneer-anomaly-like residuals ~10⁻¹⁰ m/s² from cascade-residue-DM interaction | Pioneer 10/11 historical tracking residuals (Turyshev & Toth 2010), public Cassini tracking |
| FR7 | M_KSS correlates with τ_E across tokamak databases | ITPA H-mode confinement DB (partly public); Wesson tables; published machine-by-machine summaries |

Notes on the simulation tests (QC1–QC4): the document itself calls these
"achievable by a single researcher in weeks with free software." They are
**not** tests against observed data — they are math/code claims about the CDT
holographic code. The harness should treat them as theoretical-consistency
checks, clearly labelled.

### Tier B — would need real but plausibly accessible data (do not implement; document only)

FR3 (ELM energy scaling — JET/DIII-D access usually requires login),
FR4 (η/s vs collisionality — same), FR6 (ELM frequency vs H_mag — same),
FR8 (stellarator vs tokamak M_KSS — W7-X/LHD publication scraping),
FR10 (multi-machine confinement residuals — ITPA), MAT4 (ZT vs grain
misorientation — feasible via Materials Project + literature, but no clean
benchmark dataset), MAT5 (Kibble–Zurek cooling profile — would require new
DSC/EBSD data), MAT8 (skyrmion lifetime — published but heterogeneous),
AE1 (cosmic-ray cross-section anomaly at >1 TeV — AMS-02 / CALET public data,
but the predicted ~10⁻⁶ enhancement is far below current statistical
sensitivity).

For each Tier-B entry write a one-page spec under `specs/tier_b/` documenting
the data source, the test design, and the obstacle to current implementation.

### Tier C — not testable on any current public data; document and drop

All ν_bulk predictions at the ~10⁻¹⁵ level (FR9, FR11, FR12, QC11–QC14,
EN5–EN8, SE1–SE10, BI8, AE3, AE6–AE8), all next-gen-instrument predictions
(LISA, LiteBIRD, CMB-S4, AION-100, 100-km optical-clock baselines), and the
biotechnology predictions (BI1–BI7) that need wet-lab work.

Create `specs/tier_c_log.md` with one bullet per prediction stating the
unmet instrumental requirement. Do not attempt to test these.

---

## 3. Repository layout

```
ccdr_test_harness/
├── CLAUDE.md                    # this file
├── README.md                    # human-facing overview
├── pyproject.toml               # uv / pip-compatible
├── src/ccdr_tests/
│   ├── __init__.py
│   ├── core/
│   │   ├── prediction.py        # Prediction dataclass + Result dataclass
│   │   ├── registry.py          # central registry of all tests
│   │   ├── runner.py            # orchestration, parallelism, caching
│   │   ├── stats.py             # BH-FDR correction, bootstrap CIs, effect sizes
│   │   └── data_cache.py        # HTTP fetch with on-disk caching + checksum
│   ├── tests/
│   │   ├── qc01_cdt_code_distance.py
│   │   ├── qc02_cdt_vs_surface.py
│   │   ├── qc03_cdt_threshold.py
│   │   ├── qc04_cdt_burst_errors.py
│   │   ├── qc05_transmon_t1_floor.py
│   │   ├── mat01_grain_boundary_kappa.py
│   │   ├── mat03_kappa_t_half.py
│   │   ├── mat06_diamond_kappa_ceiling.py
│   │   ├── mat10_kibble_zurek_exponent.py
│   │   ├── el01_3dnand_area_scaling.py
│   │   ├── en03_pv_sq_excess.py
│   │   ├── ae02_ringdown_kerr_deviation.py
│   │   ├── ae05_pioneer_residual.py
│   │   └── fr07_mkss_tau_e.py
│   └── report/
│       ├── render_markdown.py
│       └── render_html.py
├── specs/
│   ├── tier_a/                  # one .md per Tier-A test (sharp spec)
│   ├── tier_b/                  # one .md per Tier-B test (deferred)
│   └── tier_c_log.md            # bullet log of dropped predictions
├── data_cache/                  # gitignored; raw downloads land here
├── reports/                     # generated; final summary lives here
└── tests/                       # pytest tests of the harness itself
```

**Style choice for the Java maintainer reading this:** every test module
exposes exactly two top-level objects — the `Prediction` constant (an
immutable dataclass, analogous to a Java `record`) and a `run(ctx) ->
Result` function. No globals, no side effects at import time, no
test-time network calls outside the cached fetcher. Treat each test
module like a Java class implementing a `PredictionTest` interface.

---

## 4. Core types (build these first)

```python
# src/ccdr_tests/core/prediction.py
from dataclasses import dataclass
from enum import Enum
from typing import Literal

class Tier(Enum):
    A = "implementable_now"
    B = "deferred_needs_data"
    C = "not_testable_today"

class Verdict(Enum):
    SUPPORTED = "supported"           # observed effect matches prediction
    REFUTED = "refuted"               # data contradicts prediction
    INCONCLUSIVE = "inconclusive"     # data too noisy / sparse to decide
    RETROFIT = "retrofit_consistent"  # consistent but post-hoc, not a real test

@dataclass(frozen=True)
class Prediction:
    pid: str                          # e.g. "QC1", "MAT6"
    domain: str                       # "quantum_computing", "materials", ...
    one_liner: str
    sharp_form: str                   # mathematical statement, one sentence
    falsification_criterion: str      # what observation would refute it
    retrofit_risk: Literal["low", "medium", "high"]
    tier: Tier
    public_sources: list[str]         # URLs / identifiers

@dataclass
class Result:
    pid: str
    verdict: Verdict
    effect_observed: float | None
    effect_predicted: float | tuple[float, float]   # point or (lo, hi) range
    effect_unit: str
    p_value: float | None             # raw, uncorrected
    q_value: float | None             # BH-FDR adjusted (filled by runner)
    n: int                            # sample size / DoF
    methodology: str                  # 2–3 sentences
    data_sources_used: list[str]
    caveats: list[str]
    timestamp_utc: str
```

The runner fills `q_value` after all Tier-A tests have produced raw p-values.

---

## 5. Per-test specifications

For each Tier-A test, the implementing module **must** at the top hold a
docstring containing the eight-field card below. Do not deviate from this
schema — the report generator reads it.

```
PID: <id>
SHARP_FORM: <one-line falsifiable math statement>
PREDICTED_EFFECT: <number with units, or range>
NULL_HYPOTHESIS: <what we'd expect absent the framework>
DATA_SOURCE: <URL(s)>
TEST_STATISTIC: <e.g. weighted χ², KS distance, slope of log-log fit>
DECISION_RULE: <pass/fail threshold, including significance level>
RETROFIT_RISK: low | medium | high — and why
```

The full per-test plans follow. Implement them in the order listed; the
ordering reflects feasibility, not priority.

### 5.1 QC1–QC4 — CDT holographic QEC code (simulation suite)

**What's being tested:** the document claims a CDT-derived tensor-network
code has distance d ~ N^{1/3}, beats surface code at N > 10⁵, has threshold
p_th ~ 1 %, and superior burst-error protection. These are mathematical
claims about a code construction; the "test" is reproducing the
construction and measuring its properties.

**Approach:**
- Use [Stim](https://github.com/quantumlib/Stim) for stabiliser simulation
  and [PyMatching](https://github.com/oscarhiggott/PyMatching) for decoding.
- Build the surface-code baseline first (it ships with Stim).
- For the "CDT" code: the document does not give an unambiguous
  construction. Implement the nearest well-defined proxy — a random
  triangulation of a 3-ball with stabilisers placed on boundary edges of
  the dual graph, following the Pastawski–Yoshida–Harlow holographic-code
  recipe (arXiv:1503.06237). Document this choice prominently as a
  **construction ambiguity** in the result card.
- Sweep N ∈ {10², 10³, 10⁴, 10⁵, 10⁶}. Fit log d vs log N. Pass if slope
  ∈ [0.30, 0.36] with 95 % bootstrap CI excluding 0.5 (the surface-code value).
- For QC3, sweep depolarising noise p ∈ [0.001, 0.05] and find the
  threshold by the standard finite-size-scaling crossing of logical error
  curves. Pass if 0.005 ≤ p_th ≤ 0.02.
- For QC4, inject correlated bursts of n_burst ∈ {3,5,10} adjacent errors;
  compare logical error rate to a surface code of identical N. Pass if
  CDT-proxy logical error is lower at p = 0.7 × p_th with p < 0.05.

**Retrofit risk: HIGH** — the construction is not uniquely specified in
the document, so we are choosing a code that may or may not match what
the authors had in mind. Report verdicts as `RETROFIT` not `SUPPORTED`
even on a positive result, and surface this choice prominently.

### 5.2 QC5 — phononic-crystal-substrate transmon T1 > 1 ms

**Data source:** the SQuADDS database (https://sqdlab.github.io/SQuADDS/)
and a curated list of phononic-crystal-substrate qubit papers from
arXiv (Painter group preprints, search arXiv API for
`abs:"phononic crystal" AND abs:transmon AND abs:T1`).

**Test:** scrape reported T1 values for (a) standard transmons on Si/Al₂O₃,
(b) transmons on phononic-crystal substrates. Compute the maximum reported
T1 in group (b). Pass if max(T1_b) > 1 ms with at least one independent
replication. **Note** the current state of the art as of the document's
April 2026 date is ~300 μs (Caltech Painter group). So this test is
likely INCONCLUSIVE — the threshold of 1 ms has not been crossed yet,
which is consistent with the prediction being for future hardware.

**Decision:** if no published T1 ≥ 1 ms exists by execution time, verdict
is INCONCLUSIVE, not REFUTED. The prediction is forward-looking.

### 5.3 MAT1, MAT3 — grain-boundary thermal conductivity

**Data source:** the NIST ThermoData Engine has parts; a more useful
source is the published tabulations in Cahill et al. 2014 (Appl. Phys.
Rev. 1, 011305 — listed as ref [11] in the doc itself). Also the
Materials Project API (https://api.materialsproject.org/) for
phonon-mode data on candidate materials.

**Test (MAT1):** for each material with κ(T) data over T ∈ [1 K, 50 K]
and an independently measured grain size L_grain, fit the data to:
1. Casimir baseline: κ(T) = α·T³·L_grain·(1−β·exp(−T_D/T))
2. CCDR form: κ(T) = κ₀(T) × μ(λ(T)/L_grain), μ(x) = x/(1+x)^{1/2}, where
   λ(T) is the bulk mean-free-path estimated from κ_bulk(T).

Compare AIC of the two fits. Pass for CCDR if ΔAIC > 4 in favour of the
CCDR form across at least 5 materials (one-sided sign test, n ≥ 5).

**Test (MAT3):** in the T → 0 limit (T < 5 K), fit log κ vs log T. The
Casimir model gives slope 3. The CCDR claim is slope 1/2. Pass for CCDR
if pooled slope (Fisher-combined) falls in [0.3, 0.7]; refute if it
falls in [2.5, 3.5].

**Retrofit risk: medium** — published κ(T) data is exactly the data the
framework was constructed against (the doc cites Cahill).

### 5.4 MAT6 — diamond κ ≤ 3300 W/m/K theoretical maximum

**HIGH RETROFIT RISK** — the value 3300 W/m/K is the measured number from
Wei et al. 1993 (Phys. Rev. Lett. 70, 3764) and subsequent ¹²C-enriched
diamond work. The "prediction" is post-hoc explanation, not forward
inference.

**Test:** scan recent literature (2020–2026) on Inoue et al.-style
ultra-pure CVD diamond for any report of κ ≥ 3500 W/m/K at 300 K. If
found, REFUTED. If max reported κ stays in [3300, 3500] W/m/K, the
verdict is `RETROFIT` (consistent but not a forward prediction).

### 5.5 MAT10 — Kibble–Zurek exponent from grain-size vs cooling-rate scaling

**Data source:** published EBSD studies of solidification grain size in
metals and ceramics with measured cooling rates dT/dt. A curated
starting list:
- Al alloys: published rapid-solidification studies (Jones 1973 onward)
- Ni superalloys: laser-powder-bed-fusion grain size vs scan speed
- Si: float-zone grain-size data at varying pull rates

**Test:** for each material/dataset, fit log(grain size) vs log(quench
time τ_Q) and extract the exponent. The CCDR prediction is
ν/(1+νz) ≈ 0.63/(1+0.63·2.02) ≈ 0.277 for 3D Ising universality. Pass
if pooled exponent ∈ [0.20, 0.35] with bootstrap CI; refute if pooled
exponent < 0.10 or > 0.50.

**Important caveat:** Kibble–Zurek scaling in solidification has *standard*
explanations from nucleation theory that give very similar exponents.
A confirmation here is **not** specific to CCDR — flag this in the
caveats list.

### 5.6 EL1 — 3D NAND areal vs volumetric scaling

**Data source:** public datasheets and ISSCC papers for 3D NAND
generations: Samsung V-NAND (24L→32L→48L→64L→96L→128L→176L→236L),
Micron, SK Hynix. Compile a CSV of (layer count, die area, total bits,
read bandwidth, write bandwidth).

**Test:** fit two competing models for read bandwidth and bit density:
1. Volume: bandwidth ∝ N_layers × area
2. Area: bandwidth ∝ √(N_layers) × area  (effective surface scaling)

Compute the ratio BW / (N_layers × area) across generations. The CCDR
claim is that this ratio should **decrease** with N_layers (bandwidth
bottlenecks at the inter-layer interface). The conventional view is
that it stays roughly flat. Test by Spearman ρ between (N_layers) and
(BW_per_transistor). Pass for CCDR if ρ < 0 with p < 0.05 (one-sided).

**Caveat:** confounded by deliberate architectural choices over the
2014–2026 NAND evolution — channel-hole-shaped scaling, charge-trap vs
floating-gate transitions, etc. Document these confounders in the
result.

### 5.7 EN3 — photovoltaic efficiency exceeding Shockley–Queisser

**Data source:** NREL "Best Research-Cell Efficiency Chart" — the
chart's underlying data is available from NREL as a CSV. Plus per-cell
literature references for the highest-efficiency points.

**Test:** the Shockley–Queisser limit for Si under AM1.5G is ~32.9 %.
The CCDR prediction is real Si cells should exceed SQ by 5–10 %, i.e.
reach 34.5–36.2 %. Current Si record is ~27 % (well below SQ — Si is
SQ-limited but does not reach it).

Therefore EN3 is most usefully tested **against the prediction in its
own terms**: among single-junction Si cells (heterojunction, IBC,
HIT, TOPCon), is any reported efficiency above SQ? Pass if yes;
refute if no published Si single-junction cell exceeds the
single-junction SQ limit by April 2026. As of present knowledge,
verdict will be REFUTED for the strong reading. For multi-junction
the SQ limit is much higher (~46 %) and current record is ~47 %, so
the *multi-junction* reading is RETROFIT-consistent.

Be precise: a single-junction Si cell at 27 % efficiency does not
"exceed SQ" because SQ for Si is ~33 %; the cell is just close to
the limit.

### 5.8 AE2 — black-hole ringdown deviation from Kerr

**Data source:** GWTC-3 catalogue (https://www.gw-openscience.org/eventapi/)
and the LIGO/Virgo ringdown analyses (Isi & Farr 2021; LVC ringdown
papers). Use the `gwosc` Python client to fetch posterior samples.

**Test:** for high-SNR ringdown events (GW150914, GW200129, etc.),
extract the posterior on the first-overtone frequency deviation δf_22/f_22
from the Kerr prediction. The CCDR claim is ~10⁻³. Current LIGO/Virgo
posteriors have width ~10⁻¹ on the mean for individual events. Pool
across events using a hierarchical Bayesian model (PyMC) to estimate
the population-level deviation.

Pass for CCDR if the pooled posterior on |δf/f| has 90 % credible interval
containing 10⁻³ AND excluding zero. Refute if 90 % CI is fully below
3×10⁻⁴ (well below the predicted value) or fully above 3×10⁻³.

Most likely verdict: INCONCLUSIVE — current sensitivity does not reach
10⁻³ on ringdown deviations even for the loudest events.

### 5.9 AE5 — Pioneer-anomaly-like cascade-residue residuals

**Data source:** Turyshev & Toth 2010 published Pioneer 10/11 tracking
residuals (arXiv:1001.3686). Note that the Pioneer anomaly has been
conclusively explained by anisotropic thermal radiation pressure (Turyshev
et al. 2012, Phys. Rev. Lett. 108, 241101). There is no residual unexplained
acceleration at the 10⁻¹⁰ m/s² level remaining.

**Test:** check whether the published residuals *after* the thermal
recoil model are consistent with the CCDR claim of additional
~10⁻¹⁰ m/s² cascade-residue acceleration. The published post-thermal
residuals are at the level of ~10⁻¹¹ m/s² (i.e. an order of magnitude
below the CCDR claim). Therefore the strong CCDR claim is REFUTED by
existing public Pioneer data.

Be careful in the report: document the thermal recoil resolution
prominently. A reader unaware of Turyshev 2012 would expect Pioneer
data to be supportive; the public-data testing must reflect the
*current* state of analysis, not the 2008 state.

### 5.10 FR7 — M_KSS / energy-confinement-time correlation

**Data source:** ITPA H-mode confinement database (the public subset is
small); secondary, the IPB98(y,2) scaling-law fitting datasets cited
in Wesson "Tokamaks" and Doyle et al. 2007 (Nucl. Fusion 47, S18). Some
shot-level data is accessible via tokamak-specific archives (DIII-D,
EAST) under registration; for a public-only test, restrict to the
published machine-by-machine aggregated tables.

**Test:** the CCDR claim is that M_KSS = η_edge / η_KSS should correlate
with τ_E across machines. The challenge: η_edge is not in standard
confinement databases — it has to be inferred from edge ν*, T_e, n_e
via Braginskii expressions. Implement that inference; flag the
inference as a major systematic.

Compute Spearman ρ(M_KSS, τ_E) across the machine-aggregated table.
Pass if ρ < −0.5 with p < 0.05 (lower M_KSS = higher τ_E). Caveats:
small N (machines), heavy systematic in η_edge derivation. Expect
INCONCLUSIVE unless effect is very strong.

---

## 6. Cross-cutting requirements

### 6.1 Reproducibility

Every test must:
- Pin all data source URLs and checksum the cached data.
- Pin all Python dependency versions in `pyproject.toml`.
- Set deterministic random seeds (default 0xCCDR) for simulation tests.
- Write the exact dataset version / accession date into the result card.

### 6.2 Multiple-testing correction

After all Tier-A tests have run, the runner computes Benjamini–Hochberg
q-values across the full battery and adjusts verdicts:
- A test with raw p < 0.05 but q > 0.10 is downgraded from SUPPORTED to
  INCONCLUSIVE in the summary table, with a note.
- The HTML report shows both raw and adjusted in side-by-side columns.

### 6.3 Pre-registration discipline

Each test's decision rule (in the docstring card) is **fixed before**
the data is fetched. Implementations that adjust thresholds after seeing
the data are bugs. Add a `pytest` test that hashes the decision-rule
string at test-module import time and asserts it matches a recorded
hash in `specs/tier_a/<pid>.lock`.

### 6.4 Honest verdicts

The runner refuses to emit a SUPPORTED verdict when:
- `retrofit_risk == "high"` — output is RETROFIT instead.
- The dataset used was published before the document's April 2026 date
  AND the prediction's numerical value falls within ±20 % of the
  dataset's known central value (heuristic retrofit smell-check).

### 6.5 Output

Generate three artefacts in `reports/`:
1. `summary.md` — one-line verdict per prediction in a table, plus
   tier counts.
2. `full_report.html` — per-prediction full result card with plots.
3. `machine_readable.json` — array of `Result` dicts, for downstream use.

The summary table is the headline. It must include:
| PID | Domain | Verdict | Observed | Predicted | p / q | Retrofit risk | Notes |

Sort by domain, then PID.

---

## 7. Implementation order (suggested)

1. Core types + runner skeleton + BH-FDR statistics (1 day)
2. Data-cache layer with checksumming (½ day)
3. Three "easy" tests to validate harness end-to-end: EL1, EN3, MAT6 (1 day)
4. The CDT simulation suite QC1–QC4 (2–3 days; this is the bulkiest piece)
5. Materials tests MAT1, MAT3, MAT10 (1–2 days)
6. AE2 ringdown (1 day; depends on gwpy)
7. AE5 Pioneer (½ day)
8. QC5 transmon survey, FR7 tokamak — last because both are dominated by
   data-availability frustration (1 day combined, expect INCONCLUSIVE)
9. Report renderer + final QA pass (1 day)
10. Tier-B and Tier-C documentation files (½ day)

Total: ~9–11 days of focused work.

---

## 8. What this harness does NOT do

- It does not test the cosmological core of CCDR/Synthesis. P39 secular
  Λ-drift, P40 bulk-Weyl B-mode, MOND-sequence ν_joint, void-wall
  kurtosis — these need DESI / LiteBIRD / Euclid / CMB-S4 data that
  either is not public yet or requires custom large-scale-structure
  analysis pipelines beyond this harness's scope.
- It does not adjudicate the theoretical framework. A clean sweep of
  Tier-A SUPPORTED verdicts would still be only ~14/83 predictions, with
  several flagged as retrofit. The framework's real test is in the
  cosmological predictions, not the engineering applications.
- It does not produce policy or funding recommendations.

---

## 9. For Claude Code: start here

1. Read this file again.
2. Read `specs/tier_a/QC1.md` through `specs/tier_a/FR7.md` (write them
   first if they're missing — they expand the sketches in §5 above into
   full spec cards).
3. Implement §4's core types.
4. Implement the runner with a dummy test to validate the framework.
5. Implement tests in the §7 order. After each test, run the harness
   end-to-end and check that the report renders.
6. When stuck on data access, write a Tier-B spec card and move on.
   Do not block on private datasets.
7. Before merging anything, run `pytest tests/` — every test module
   has a corresponding harness-level test that checks its card schema
   and decision-rule lock hash.

Remember: the goal is not to make CCDR look good or bad. The goal is
to produce a defensible, reproducible, honest assessment of which
of its engineering predictions hold up against public data **today**,
with all the caveats made loud.
