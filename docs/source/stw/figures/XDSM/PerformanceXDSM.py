"""
==============================================================================
Aircraft performance block XDSM
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
from pyxdsm.XDSM import XDSM, FUNC

# ==============================================================================
# Extension modules
# ==============================================================================

components = {
    "WingMass": [r"\text{Wing mass}", r"\text{regression}"],
    "MassSum": [r"\text{Airframe mass}", r"\text{summation}"],
    "DragSum": [r"\text{Drag}", r"\text{correction}"],
    "Cruise": [r"\text{Cruise}", r"\text{fuel-burn}"],
    "Climb": [r"\text{Climb}", r"\text{fuel-burn}"],
    "FuelBurn": [r"\text{Total}", r"\text{fuel-burn}"],
    "CruiseLift": [r"\text{Cruise}", r"\text{lift error}"],
    "ManLift": [r"\text{Maneuver}", r"\text{lift error}"],
    "FuelVol": [r"\text{Fuel tank}", r"\text{usage}"],
    "WingLoading": [r"\text{Wing loading}", r"\text{calculation}"],
}

for HighlightedComp in list(components.keys()) + ["all"]:
    xdsm = XDSM(
        optional_latex_packages=["cmbright"],
        auto_fade={"connections": "connected", "inputs": "connected", "outputs": "connected"},
    )

    # --- Components ---
    for key, val in components.items():
        xdsm.add_system(key, FUNC, val, faded=HighlightedComp not in [key, "all"])

    # --- Connections ---
    xdsm.connect("WingMass", "MassSum", r"\text{Wing mass}")

    for target in ["Cruise", "FuelBurn", "CruiseLift", "ManLift"]:
        xdsm.connect("MassSum", target, r"\text{LGM}")

    xdsm.connect("DragSum", "Cruise", r"\text{Drag}")
    xdsm.connect("DragSum", "Climb", r"\text{Drag}")

    xdsm.connect("Cruise", "Climb", r"M_\text{cruise,start}")
    xdsm.connect("Cruise", "CruiseLift", r"M_\text{cruise,start}")

    xdsm.connect("Climb", "FuelBurn", r"\text{TOGM}")
    xdsm.connect("Climb", "WingLoading", r"\text{TOGM}")

    xdsm.connect("FuelBurn", "FuelVol", [r"\text{Fuel-}", r"\text{burn}"])

    # --- inputs ---
    xdsm.add_input("WingMass", [r"\text{Wingbox}", r"\text{mass}"])

    xdsm.add_input("DragSum", [r"\text{Cruise}", r"\text{drag}"])

    for comp in ["Cruise", "Climb", "CruiseLift"]:
        xdsm.add_input(comp, [r"\text{Cruise}", r"\text{lift}"])

    xdsm.add_input("ManLift", [r"\text{Maneuver}", r"\text{lift}"])

    xdsm.add_input("FuelVol", [r"\text{Wingbox}", r"\text{volume}"])

    xdsm.add_input("WingLoading", [r"\text{Wing}", r"\text{area}"])

    # --- Outputs ---
    xdsm.add_output("FuelBurn", [r"\text{Fuel-}", r"\text{burn}"])

    xdsm.add_output("WingLoading", [r"\text{Wing}", r"\text{loading}"])

    xdsm.add_output("FuelVol", [r"\text{Tank}", r"\text{usage}"])

    for comp in ["CruiseLift", "ManLift"]:
        xdsm.add_output(comp, [r"\text{Lift}", r"\text{error}"])

    # --- Save ---
    xdsm.write(f"Performance-{HighlightedComp}", cleanup=True)
