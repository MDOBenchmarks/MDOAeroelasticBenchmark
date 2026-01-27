"""
==============================================================================
Overall optimisation problem XDSM
==============================================================================
@File    :   OverallXDSM.py
@Date    :   2023/05/15
@Author  :   Alasdair Christison Gray
@Description :
"""

# ==============================================================================
# Standard Python modules
# ==============================================================================

# ==============================================================================
# External Python modules
# ==============================================================================
from pyxdsm.XDSM import (
    XDSM,
    OPT,
    GROUP,
)

# ==============================================================================
# Extension modules
# ==============================================================================

for HighlightedComp in ["opt", "geom", "cruise", "maneuver", "performance", "all"]:
    xdsm = XDSM(optional_latex_packages=["cmbright"], auto_fade={"connections": "connected"})

    # xdsm.add_process(["opt", "geom", "cruise", "performance", "opt"], arrow=True)
    # xdsm.add_process(["opt", "geom", "maneuver", "performance", "opt"], arrow=True)
    # xdsm.add_process(["opt", "geom", "maneuver", "opt"], arrow=True)

    # --- Components ---
    xdsm.add_system("opt", OPT, [r"\text{Optimizer}"], faded=HighlightedComp not in ["opt", "all"])
    xdsm.add_system(
        "cruise", GROUP, [r"\text{Cruise}", r"\text{analysis}"], faded=HighlightedComp not in ["cruise", "all"]
    )
    xdsm.add_system(
        "maneuver1",
        GROUP,
        [r"2.5 g\text{ Maneuver}", r"\text{analysis}"],
        faded=HighlightedComp not in ["maneuver", "all"],
    )
    xdsm.add_system(
        "maneuver2",
        GROUP,
        [r"-1 g\text{ Maneuver}", r"\text{analysis}"],
        faded=HighlightedComp not in ["maneuver", "all"],
    )
    xdsm.add_system(
        "performance",
        GROUP,
        [r"\text{Aircraft}", r"\text{performance}"],
        faded=HighlightedComp not in ["performance", "all"],
    )

    # --- Connections ---
    xdsm.connect(
        "opt",
        "cruise",
        [r"\text{Geometric DVs}", r"\alpha_\text{cruise}, \text{struct DVs}"],
    )
    xdsm.connect(
        "opt",
        "maneuver1",
        [r"\text{Geometric DVs}", r"\alpha_\text{maneuver,1}, \text{struct DVs}"],
    )
    xdsm.connect(
        "opt",
        "maneuver2",
        [r"\text{Geometric DVs}", r"\alpha_\text{maneuver,2}, \text{struct DVs}"],
    )

    # xdsm.connect("geom", "cruise", [r"\text{Aero/struct}", r"\text{coordinates}"])
    # xdsm.connect("geom", "maneuver1", [r"\text{Aero/struct}", r"\text{coordinates}"])
    # xdsm.connect("geom", "maneuver2", [r"\text{Aero/struct}", r"\text{coordinates}"])
    # xdsm.connect("geom", "performance", [r"\text{Wing area,}", r"\text{wingbox volume}"])
    xdsm.connect("cruise", "opt", [r"\text{Geometric}", r"\text{constraints}"])

    xdsm.connect("cruise", "performance", [r"\text{Lift, drag,}", r"\text{wingbox volume,}", r"\text{wing area}"])

    xdsm.connect("maneuver1", "performance", [r"\text{Lift}", r"\text{wingbox mass}"])
    xdsm.connect("maneuver2", "performance", [r"\text{Lift}"])
    xdsm.connect("maneuver1", "opt", [r"\text{Strength}", r"\text{ratios}"])
    xdsm.connect("maneuver2", "opt", [r"\text{Strength}", r"\text{ratios}"])

    xdsm.connect(
        "performance",
        "opt",
        [r"\text{Fuel-burn,}", r"\text{lift errors,}", r"\text{tank usage,}", r"\text{wing loading}"],
    )

    for point in ["cruise", "maneuver1", "maneuver2"]:
        xdsm.add_process(["opt", point, "performance", "opt"], arrow=True)

    # --- inputs ---

    # --- Outputs ---

    # --- Save ---
    xdsm.write(f"Overall-{HighlightedComp}", cleanup=True)
