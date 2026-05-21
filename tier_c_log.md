# Tier C — predictions not testable on current public data

Each entry lists why no public-data test is possible *as of May 2026*. These
are not failures of the framework; they are honest statements of where the
needed instruments don't exist yet or where the data isn't public.

## Bulk-vacuum (ν_bulk) noise-floor predictions at ~10⁻¹⁵

- **FR9** — bulk-vacuum noise floor δn/n ~ 10⁻⁸ in tokamak edge electrostatic
  fluctuations. Requires ITER edge diagnostics or DIII-D / JT-60SA fluctuation
  campaigns with integration >0.1 s and resolution <1 cm. No public dataset
  at this sensitivity.
- **FR11** — ν_bulk-coupled drift-wave growth-rate ~1 % correction. Requires
  Alcator C-Mod or DIII-D gyrokinetic-vs-experiment comparison data not
  in any public archive.
- **FR12** — Stage-4 cold-atom 2D→1D analogue. No deployed instrument.
- **QC11** — T2-cap at ~1 s for transmons from bulk-vacuum coupling.
  Current best T2 ≪ 1 s; cap will not be hit for years.
- **QC12** — bulk-Weyl-anomaly qubit. No synthetic-dimension ion-trap
  experiment at the required size has reported data.
- **QC13** — ν cross-domain triangulation via atom-interferometer noise
  floors. Sensitivity is ~10⁻¹³ today vs required ~10⁻¹⁵.
- **QC14** — Stage-4 QRNG from χ→1 saturation. No instrument.
- **MAT13** — ν_bulk projection in laboratory crystal zero-point energy via
  <1 mK torsion balance. No such measurement is public.
- **EL9** — sub-Landauer computing floor at ~10⁻⁵⁵ J/op. 34 orders of
  magnitude below current technology.
- **EL10** — synthetic-dimension memory architecture. No instrument.
- **EN5–EN8** — bulk-vacuum energy flux, sub-Landauer computing, bulk-Weyl
  energy harvesting, KK-Casimir deviation. All require sensitivity at least
  1–5 orders of magnitude below current public-data state of the art.
- **SE1–SE10** — entire sensors-and-metrology chapter is forward-looking:
  AION-100, LISA, next-gen Casimir, 100-km optical-clock baselines, all
  unbuilt or not yet returning public data.
- **BI8** — bulk-vacuum projection in biological systems via molecular
  spectroscopy at <1 K. No matching public dataset.
- **AE3** — spacecraft chronometric ν_bulk drift over decade missions.
  Requires deep-space optical clocks not yet flown.
- **AE6** — bulk-Weyl small-N propulsion via Stage-4 simulator. No instrument.
- **AE7** — higher-dimensional trajectory optimisation. Explicitly noted in
  the document as >50 year horizon.
- **AE8** — cosmic-crystal frequency reference for deep-space missions.
  No instrument.

## Biotechnology predictions requiring wet-lab work

- **BI1** — directed evolution of high-symmetry synthetic proteins.
- **BI2** — voltage-sensitive-dye microscopy on cultured neuron arrays for
  ~1 % action-potential anisotropy.
- **BI3** — nanofabricated chromophore arrays for synthetic photosystem
  efficiency >70 %.
- **BI4** — controlled mineralisation experiments with Kibble–Zurek profile.
- **BI5** — ultrafast spectroscopy on isolated microtubules at 37 °C.
- **BI6** — phonon spectroscopy on stretched DNA fibres.
- **BI7** — 3D-printed gradient scaffolds with load-bearing assay.

None of these have public databases of the kind the harness can ingest;
each would need a dedicated experiment.

## Cosmological core (out of scope by design)

The Synthesis v3.5 cross-link triangulation (CL1–CL5) and the P39 / P40
predictions require DESI DR3, LiteBIRD, Euclid Q1+, and CMB-S4 pipelines.
These are mentioned in the document but explicitly framed as
not-yet-implementable; they live in companion CCDR cosmology manuscripts
and are out of scope for this engineering-applications harness.

---

**Action for any future user of this harness:** when a Tier-C item becomes
testable (new instrument flies, dataset is released), move its entry to
`specs/tier_b/<pid>.md`, write the test design, and only then promote to
Tier A by writing a full test module.
