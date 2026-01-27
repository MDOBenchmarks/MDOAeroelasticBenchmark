"""
==============================================================================
Aerostructural analysis block XDSM
==============================================================================
@File    :   PerformanceXDSM.py
@Date    :   2023/05/16
@Author  :   Alasdair Christison Gray
@Description :
"""

# ==============================================================================
# Standard Python modules
# ==============================================================================

# ==============================================================================
# External Python modules
# ==============================================================================
from pyxdsm.XDSM import XDSM, SOLVER, FUNC, IFUNC

# ==============================================================================
# Extension modules
# ==============================================================================

components = {
    "geom": {"label": [r"\text{Geometry}", r"\text{paramterization}"], "compType": FUNC},
    "solver": {"label": [r"\text{NLBGS Solver}"], "compType": SOLVER},
    "aero": {"label": [r"\text{CFD}"], "compType": IFUNC},
    "loads": {"label": [r"\text{Load}", r"\text{transfer}"], "compType": FUNC},
    "struct": {"label": [r"\text{FEM}"], "compType": IFUNC},
    "disps": {"label": [r"\text{Displacement}", r"\text{transfer}"], "compType": FUNC},
}

systemOrder = list(components.keys())
highlightOrder = ["geom", "aero", "struct", "loads", "disps", "solver"]

for ii in range(len(highlightOrder)):
    HighlightedComps = highlightOrder[: (ii + 1)]
    xdsm = XDSM(
        optional_latex_packages=["cmbright"],
        auto_fade={"connections": "connected", "inputs": "connected", "outputs": "connected"},
    )
    xdsm.add_process(["geom", "solver", "aero", "loads", "struct", "disps", "solver"])

    # --- Components ---
    for key, val in components.items():
        xdsm.add_system(key, val["compType"], val["label"], faded=key not in HighlightedComps)

    # --- Connections ---
    xdsm.connect("geom", "aero", [r"\text{Aero surface}", r"\text{mesh coordinates}"])
    xdsm.connect("geom", "struct", [r"\text{Struct mesh}", r"\text{coordinates}"])
    xdsm.connect("geom", "loads", [r"\text{Aero surface +}", r"\text{struct mesh coordinates}"])
    xdsm.connect("geom", "disps", [r"\text{Aero surface +}", r"\text{struct mesh coordinates}"])

    xdsm.connect("aero", "loads", [r"\text{Aerodynamic}", r"\text{loads}"])

    xdsm.connect("loads", "struct", [r"\text{Structural}", r"\text{loads}"])

    xdsm.connect("struct", "disps", [r"\text{Structural}", r"\text{displacements}"])
    xdsm.connect("struct", "loads", [r"\text{Structural}", r"\text{displacements}"])

    xdsm.connect("disps", "aero", [r"\text{Aerodynamic}", r"\text{displacements}"])

    # --- inputs ---
    xdsm.add_input("geom", [r"\text{Geometric DVs}"])
    xdsm.add_input("aero", [r"\alpha"])
    xdsm.add_input("struct", [r"\text{Struct DVs}"])

    # --- Outputs ---
    xdsm.add_output("aero", [r"\text{Lift,}", r"\text{drag}"], side="right")
    xdsm.add_output("struct", [r"\text{wingbox mass,}", r"\text{strength ratios}"], side="right")
    xdsm.add_output("geom", [r"\text{Geometric}", r"\text{constraints}"], side="right")

    # --- Save ---
    xdsm.write(f"AeroStruct-{highlightOrder[ii]}", cleanup=True)
