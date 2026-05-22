"""EL1 — 3D NAND throughput scales with area, not volume (transistor count).

PID: EL1
SHARP_FORM: Spearman rho between N_layers and (read bandwidth / total bits) < 0,
            with p < 0.05 (one-sided).
PREDICTED_EFFECT: rho < 0 (bandwidth-per-cell decreases as layers grow).
NULL_HYPOTHESIS: rho >= 0 (per-cell bandwidth flat or rising).
DATA_SOURCE: Published ISSCC/IMW papers and product datasheets for 24L-300L+ NAND.
DECISION_RULE:
  SUPPORTED if Spearman rho < 0 with one-sided p < 0.05.
  REFUTED   if rho > 0 with two-sided p < 0.05.
  INCONCLUSIVE otherwise.
RETROFIT_RISK: LOW.
"""

from __future__ import annotations

import hashlib
from typing import Any

import numpy as np

from ccdr_tests.core.prediction import Prediction, Result, RetrofitRisk, Tier, Verdict
from ccdr_tests.core.stats import spearman

DECISION_RULE = (
    "SUPPORTED if Spearman rho(N_layers, BW_per_bit) < 0 with one-sided p<0.05; "
    "REFUTED if rho > 0 with two-sided p<0.05; INCONCLUSIVE otherwise."
)
DECISION_RULE_HASH = hashlib.sha256(DECISION_RULE.encode()).hexdigest()

PREDICTION = Prediction(
    pid="EL1",
    domain="electronics",
    one_liner="3D NAND throughput scales with area, not volume.",
    sharp_form="Spearman rho(N_layers, BW/bit) < 0 with p<0.05.",
    null_hypothesis="rho >= 0; per-cell bandwidth is layer-agnostic.",
    predicted_effect=-0.5,
    effect_unit="Spearman rho",
    falsification_criterion="rho > 0 with p<0.05.",
    retrofit_risk=RetrofitRisk.LOW,
    tier=Tier.A,
    public_sources=(
        "Samsung ISSCC V-NAND papers (2014-2024)",
        "Micron / SK Hynix product briefs and IMW proceedings",
    ),
    decision_rule=DECISION_RULE,
)


# (vendor_generation, N_layers, die_capacity_Gb, IO_BW_MTps, page_program_us)
# Values from public ISSCC papers and product briefs.
NAND_TABLE = [
    ("Samsung V-NAND Gen1",  24, 128,  333,  1300),
    ("Samsung V-NAND Gen2",  32, 128,  667,  1200),
    ("Samsung V-NAND Gen3",  48, 256, 1000,   700),
    ("Samsung V-NAND Gen4",  64, 512, 1200,   500),
    ("Samsung V-NAND Gen5",  96, 512, 1400,   500),
    ("Samsung V-NAND Gen6", 128, 1024, 1600,   450),
    ("Samsung V-NAND Gen7", 176, 1024, 2000,   350),
    ("Samsung V-NAND Gen8", 236, 1024, 2400,   330),
    ("Micron 176L",         176, 1024, 1600,   400),
    ("Micron 232L",         232, 1024, 2400,   380),
    ("SK Hynix 96L",         96,  512, 1200,   500),
    ("SK Hynix 176L",       176, 1024, 1600,   400),
    ("SK Hynix 238L",       238, 1024, 2400,   330),
    ("YMTC 64L",             64,  256,  667,   600),
    ("YMTC 128L",           128,  512, 1600,   400),
    ("YMTC 232L",           232, 1024, 2400,   330),
]


def run(ctx: Any) -> Result:
    layers = np.array([row[1] for row in NAND_TABLE], dtype=float)
    cap_Gb = np.array([row[2] for row in NAND_TABLE], dtype=float)
    bw_MTps = np.array([row[3] for row in NAND_TABLE], dtype=float)
    # Throughput per cell: I/O bandwidth divided by die capacity.
    bw_per_bit = bw_MTps / cap_Gb
    rho, p_two = spearman(layers, bw_per_bit)
    # One-sided "rho < 0" p-value.
    p_one = p_two / 2 if rho < 0 else 1 - p_two / 2

    if rho < 0 and p_one < 0.05:
        verdict = Verdict.SUPPORTED
    elif rho > 0 and p_two < 0.05:
        verdict = Verdict.REFUTED
    else:
        verdict = Verdict.INCONCLUSIVE

    return Result(
        pid="EL1",
        verdict=verdict,
        effect_observed=rho,
        effect_predicted=-0.5,
        effect_unit="Spearman rho",
        p_value=p_one,
        q_value=None,
        n=len(NAND_TABLE),
        methodology=(
            f"Compiled {len(NAND_TABLE)} 3D-NAND generations (Samsung, Micron, "
            f"SK Hynix, YMTC) from public ISSCC papers and product briefs. "
            f"Computed bandwidth-per-bit = IO_MTps / die_capacity_Gb. "
            f"Spearman rho(N_layers, BW/bit) = {rho:.3f}, two-sided p = {p_two:.3g}."
        ),
        data_sources_used=[row[0] for row in NAND_TABLE],
        caveats=[
            "Architectural choices over a decade confound layer-only inference: "
            "channel-hole shaping, TLC/QLC density, peripheral CMOS-under-array "
            "changes I/O independently of N_layers.",
            "IO_MTps is the interface-bus rate, not internal array bandwidth; "
            "internal bandwidth (read-while-program) is harder to compare across vendors.",
        ],
    )
