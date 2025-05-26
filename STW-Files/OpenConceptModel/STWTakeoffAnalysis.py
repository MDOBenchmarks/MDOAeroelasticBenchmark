"""
==============================================================================
STW Takeoff analysis using OpenConcept
==============================================================================
@File    :   STWTakeoffAnalysis.py
@Date    :   2025/05/25
@Author  :   Alasdair Christison Gray
@Description :
"""

# ==============================================================================
# Standard Python modules
# ==============================================================================
import os
import sys

# ==============================================================================
# External Python modules
# ==============================================================================
import openmdao.api as om
from openconcept.aerodynamics import CleanCLmax, FlapCLmax
from openconcept.utilities import DictIndepVarComp

# ==============================================================================
# Extension modules
# ==============================================================================
from TakeOffMission import TakeoffAnalysis
from STWAircraftModel import STWAircraftModel

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../AircraftSpecs"))
from STWSpecs import aircraftSpecs  # noqa: E402

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../geometry"))
from wingGeometry import wingGeometry  # noqa: E402

# create an OpenConcept aircraft data dictionary from the contents of STWSpecs and WingGeometry
STWData = {
    "ac": {
        "aero": {
            "polar": {
                "e": {"value": 0.9},
            },  # total guess
            "airfoil_Cl_max": {"value": 1.00},  # total guess
            "takeoff_flap_deg": {"value": aircraftSpecs["takeoffFlapSetting"], "units": "deg"},
        },
        "propulsion": {
            "engine": {
                "rating": {"value": aircraftSpecs["maxThrustPerEngine"], "units": "N"},
            },
            "num_engines": {
                "value": 2,
            },
        },
        "geom": {
            "wing": {
                "S_ref": {"value": 2 * wingGeometry["wing"]["planformArea"], "units": "m**2"},
                "AR": {"value": wingGeometry["wing"]["aspectRatio"]},
                "taper": {"value": wingGeometry["wing"]["taperRatio"]},
                "toverc": {"value": 0.12},
                "c4sweep": {"value": wingGeometry["wing"]["quarterChordSweep"], "units": "deg"},
            },
            "fuselage": {
                "S_wet": {"value": wingGeometry["fuselage"]["area"], "units": "m**2"},
                "length": {"value": wingGeometry["fuselage"]["length"], "units": "m"},
                "height": {"value": wingGeometry["fuselage"]["width"], "units": "m"},
            },
            "hstab": {
                "S_ref": {"value": 2 * wingGeometry["hTail"]["planformArea"], "units": "m**2"},
                "AR": {"value": wingGeometry["hTail"]["aspectRatio"]},
                "taper": {"value": wingGeometry["hTail"]["taperRatio"]},
                "toverc": {"value": wingGeometry["hTail"]["toverc"]},
            },
            "vstab": {
                "S_ref": {"value": wingGeometry["vTail"]["planformArea"], "units": "m**2"},
                "AR": {"value": wingGeometry["vTail"]["aspectRatio"]},
                "taper": {"value": wingGeometry["vTail"]["taperRatio"]},
                "toverc": {"value": wingGeometry["vTail"]["toverc"]},
            },
            "nacelle": {
                "S_wet": {"value": wingGeometry["nacelle"]["area"], "units": "m**2"},
                "length": {"value": wingGeometry["nacelle"]["length"], "units": "m"},
            },
        },
        "weights": {"MTOW": {"value": aircraftSpecs["refMTOW"], "units": "kg"}},
    }
}


class STWTakeoffAnalysisGroup(om.Group):
    def initialize(self):
        self.options.declare("num_nodes", default=11)

    def setup(self):
        nn = self.options["num_nodes"]

        # ==============================================================================
        # Create variables from aircraft data dictionary
        # ==============================================================================
        dv = self.add_subsystem("ac_vars", DictIndepVarComp(STWData), promotes_outputs=["*"])
        dv_outputs = [
            # -------------- Aero --------------
            "ac|aero|polar|e",
            "ac|aero|airfoil_Cl_max",
            "ac|aero|takeoff_flap_deg",
            # -------------- Propulsion --------------
            "ac|propulsion|engine|rating",
            "ac|propulsion|num_engines",
            # -------------- Geometry --------------
            # Wing
            "ac|geom|wing|S_ref",  # To be passed in as design variable
            "ac|geom|wing|AR",  # To be passed in as design variable
            "ac|geom|wing|c4sweep",  # To be passed in as design variable
            "ac|geom|wing|taper",  # To be passed in as design variable
            "ac|geom|wing|toverc",  # To be passed in as design variable
            # Horizontal stabilizer
            "ac|geom|hstab|AR",
            "ac|geom|hstab|taper",
            "ac|geom|hstab|toverc",
            "ac|geom|hstab|S_ref",
            # Vertical stabilizer
            "ac|geom|vstab|AR",
            "ac|geom|vstab|taper",
            "ac|geom|vstab|toverc",
            "ac|geom|vstab|S_ref",
            # Fuselage
            "ac|geom|fuselage|length",
            "ac|geom|fuselage|height",
            "ac|geom|fuselage|S_wet",
            # Nacelle
            "ac|geom|nacelle|length",
            "ac|geom|nacelle|S_wet",
            # -------------- Weights --------------
            "ac|weights|MTOW",  # To be passed in as design variable
        ]
        for output_name in dv_outputs:
            dv.add_output_from_dict(output_name)

        # CLmax Estimation
        self.add_subsystem(
            "clean_cl_max",
            CleanCLmax(),
            promotes_inputs=["ac|*"],
            promotes_outputs=[("CL_max_clean", "ac|aero|CLmax_clean")],
        )

        self.add_subsystem(
            "flap_cl_max",
            FlapCLmax(),
            promotes_inputs=[
                "ac|*",
                ("flap_extension", "ac|aero|takeoff_flap_deg"),
                ("CL_max_clean", "ac|aero|CLmax_clean"),
            ],
            promotes_outputs=[("CL_max_flap", "ac|aero|CLmax_TO")],
        )

        self.add_subsystem(
            "analysis",
            TakeoffAnalysis(num_nodes=nn, aircraft_model=STWAircraftModel, transition_method="simplified"),
            promotes_inputs=["*"],
            promotes_outputs=["*"],
        )


if __name__ == "__main__":
    import numpy as np
    import niceplots
    import matplotlib.pyplot as plt

    plt.style.use(niceplots.get_style())

    numNodes = 21  # Number of nodes for the analysis

    # Example usage
    prob = om.Problem()
    prob.model = STWTakeoffAnalysisGroup(num_nodes=numNodes)
    prob.model.nonlinear_solver = om.NewtonSolver(iprint=2, solve_subsystems=True, maxiter=20)
    prob.model.linear_solver = om.DirectSolver()

    prob.driver = om.ScipyOptimizeDriver()
    prob.driver.options["optimizer"] = "SLSQP"

    # Solve and optimization problem to find the flap setting that minimizes the balanced field length
    prob.model.add_design_var("ac|aero|takeoff_flap_deg", lower=0, upper=20, units="deg")
    prob.model.add_objective("bfl.distance_continue", scaler=1e-3, units="ft")  # Minimize balanced field length

    prob.setup()

    # Do the takeoff at +15 deg C conditions
    # NOTE: It looks like there are some issues with the OpenConcept takeoff model not converting properly between true
    # and equivalent airspeed, which makes the results a bit off, we'll just do the takepoff at standard sea-level
    # conditions for now.
    # prob.set_val("takeoff|TempIncrement", np.full(numNodes, 15), units="degC")

    # Guesses for takeoff speeds to help with convergence
    prob.set_val("v0v1.fltcond|Utrue", np.full(numNodes, 50), units="kn")
    prob.set_val("v1vr.fltcond|Utrue", np.full(numNodes, 85), units="kn")
    prob.set_val("v1v0.fltcond|Utrue", np.full(numNodes, 85), units="kn")
    # Need these if using ODE transition method
    # prob.set_val("rotate.fltcond|Utrue", np.full(numNodes, 90), units="kn")
    # prob.set_val("rotate.accel_vert", np.full(numNodes, 0.1), units="m/s**2")

    prob.run_driver()

    prob.run_model()
    om.n2(prob, show_browser=False, outfile="takeoff_analysis_n2.html")

    # =============== Print some useful outputs ================
    print_vars = [
        {"var": "ac|weights|MTOW", "name": "MTOW", "units": "kg"},
        {"var": "bfl.distance_continue", "name": "Balanced field length", "units": "ft"},
        {"var": "takeoff|v1", "name": "V1 speed", "units": "kn"},
        {"var": "bfl.takeoff|vr", "name": "Rotation speed", "units": "kn"},
        {"var": "ac|aero|takeoff_flap_deg", "name": "Optimal flap setting", "units": "deg"},
    ]
    print("\n=======================================================================\n")
    for var in print_vars:
        print(f"{var['name']}: {prob.get_val(var['var'], units=var['units']).item()} {var['units']}")

    takeoff_fig, takeoff_axs = plt.subplots(1, 3, figsize=[12, 5])
    takeoff_axs = takeoff_axs.flatten()  # change 1x3 mtx of axes into 4-element vector

    # Define variables to plot
    takeoff_vars = [
        {"var": "fltcond|h", "name": "Altitude", "units": "ft"},
        {"var": "fltcond|Utrue", "name": "True airspeed", "units": "kn"},
        {"var": "throttle", "name": "Throttle", "units": None},
    ]

    for idx_fig, var in enumerate(takeoff_vars):
        takeoff_axs[idx_fig].set_xlabel("Range (ft)")
        takeoff_axs[idx_fig].set_ylabel(f"{var['name']}" if var["units"] is None else f"{var['name']} ({var['units']})")

        # Loop through each flight phase and plot the current variable from each
        for phase in ["v0v1", "v1vr", "rotate", "v1v0"]:
            takeoff_axs[idx_fig].plot(
                prob.get_val(f"{phase}.range", units="ft"),
                prob.get_val(f"{phase}.{var['var']}", units=var["units"]),
                "-o",
                markersize=8.0,
                clip_on=False,
            )
            niceplots.adjust_spines(takeoff_axs[idx_fig])

    takeoff_fig.legend(
        [r"V0 $\rightarrow$ V1", r"V1 $\rightarrow$ Vr", "Rotate", r"V1 $\rightarrow$ V0"],
        loc=(0.067, 0.6),
        fontsize="small",
    )
    takeoff_fig.suptitle("Takeoff phases")
    niceplots.save_figs(takeoff_fig, "takeoff_phases", ["png", "pdf"])
    plt.show()
