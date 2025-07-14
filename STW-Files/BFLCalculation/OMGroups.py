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
from difflib import get_close_matches

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
            "airfoil_Cl_max": {"value": 1.25},  # total guess
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


def add_aircraft_data(group, excluded_inputs=None):
    dv = group.add_subsystem("ac_vars", DictIndepVarComp(STWData), promotes_outputs=["*"])
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
        "ac|geom|wing|S_ref",  # Varies during optimization
        "ac|geom|wing|AR",  # Varies during optimization
        "ac|geom|wing|c4sweep",  # Varies during optimization
        "ac|geom|wing|taper",  # Varies during optimization
        "ac|geom|wing|toverc",  # Varies during optimization
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
        "ac|weights|MTOW",  # Varies during optimization
    ]

    # Remove any excluded indepvarcomp outputs
    if excluded_inputs is not None:
        for ivc_exclude in excluded_inputs:
            try:
                dv_outputs.remove(ivc_exclude)
            except ValueError:
                closest_match = get_close_matches(ivc_exclude, list(dv_outputs.keys()), n=1, cutoff=0.0)
                Warning(f"Variable {ivc_exclude} not found in indepvarcomp outputs. Did you mean {closest_match}?")

    for output_name in dv_outputs:
        dv.add_output_from_dict(output_name)

    # Set default values for the excluded indepvarcomp outputs using the aircraft specs
    if excluded_inputs is not None:
        for ivc_exclude in excluded_inputs:
            split_names = ivc_exclude.split("|")
            data_dict_tmp = STWData
            for sub_name in split_names:
                try:
                    data_dict_tmp = data_dict_tmp[sub_name]
                except KeyError:
                    raise KeyError('"%s" does not exist in the data dictionary' % ivc_exclude)
            try:
                val = data_dict_tmp["value"]
            except KeyError:
                raise KeyError('Data dict entry "%s" must have a "value" key' % ivc_exclude)
            units = data_dict_tmp.get("units", None)
            group.set_input_defaults(ivc_exclude, val, units=units)


class STWTakeoffAnalysisGroup(om.Group):
    def initialize(self):
        self.options.declare("num_nodes", default=11)
        self.options.declare(
            "ivc_excludes",
            default=None,
            allow_none=True,
            desc="List of variables to exclude from the indepvarcomp. Use this for variables that will instead come from the outputs of other components.",
        )

    def setup(self):
        nn = self.options["num_nodes"]

        # Create variables from aircraft data dictionary
        add_aircraft_data(self, excluded_inputs=self.options["ivc_excludes"])

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
            TakeoffAnalysis(num_nodes=nn, aircraft_model=STWAircraftModel, transition_method="ode"),
            promotes_inputs=["*"],
            promotes_outputs=["*"],
        )

        # Set nonlinear and linear solvers for the group
        self.nonlinear_solver = om.NewtonSolver(iprint=2, solve_subsystems=True, maxiter=20)
        self.linear_solver = om.DirectSolver()


if __name__ == "__main__":
    # ==============================================================================
    # Example OpenMDAO group use
    # ==============================================================================
    # This is a simple demonstration of using the STWTakeoffAnalysisGroup in an OpenMDAO problem.
    # It runs a basic optimization to find the flap setting that minimizes the balanced field length.
    import numpy as np
    import niceplots
    import matplotlib.pyplot as plt

    plt.style.use(niceplots.get_style())

    numNodes = 11  # Number of nodes for each ODE phase

    prob = om.Problem()

    # By default, all the "variables" we expect to change during optimization will be included in an IndepVarComp within the group. If you are using this takeoff analysis group as part of a larger OpenMDAO model, where you want these values to instead come from the outputs of other components, you can exclude them from the indepvarcomp by passing a list of variable names to the ivc_excludes argument. These variables are:
    # - "ac|geom|wing|S_ref"
    # - "ac|geom|wing|AR"
    # - "ac|geom|wing|c4sweep"
    # - "ac|geom|wing|taper"
    # - "ac|geom|wing|toverc"
    # - "ac|weights|MTOW"
    prob.model = STWTakeoffAnalysisGroup(num_nodes=numNodes, ivc_excludes=["ac|weights|MTOW"])

    prob.driver = om.ScipyOptimizeDriver()
    prob.driver.options["optimizer"] = "SLSQP"

    # Solve and optimization problem to find the flap setting that minimizes the balanced field length
    prob.model.add_design_var("ac|aero|takeoff_flap_deg", lower=0, upper=20, units="deg")
    prob.model.add_objective("bfl.distance_continue", scaler=1e-3, units="ft")  # Minimize balanced field length

    prob.setup()

    # NOTE: It looks like there are some issues with the OpenConcept takeoff model not converting properly between true
    # and equivalent airspeed, which makes the results a bit off if you try to do the takeoff analysis at anything other
    # than sea-level standard atmospheric conditions. So we'll just do the takeoff at standard sea-level conditions for now.

    # prob.set_val("takeoff|TempIncrement", np.full(numNodes, 15), units="degC")

    # Initial guesses for takeoff speeds to help with convergence
    prob.set_val("v0v1.fltcond|Utrue", np.full(numNodes, 50), units="kn")
    prob.set_val("v1vr.fltcond|Utrue", np.full(numNodes, 85), units="kn")
    prob.set_val("v1v0.fltcond|Utrue", np.full(numNodes, 85), units="kn")

    # Need these if using ODE transition method
    prob.set_val("rotate.fltcond|Utrue", np.full(numNodes, 90), units="kn")
    prob.set_val("rotate.accel_vert", np.full(numNodes, 0.1), units="m/s**2")

    # Set an initial guess for the takeoff flap setting away from te upper bound
    prob.set_val("ac|aero|takeoff_flap_deg", 10.0, units="deg")

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
    takeoff_axs = takeoff_axs.flatten()  # change 1x3 mtx of axes into 3-element vector

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
                "-",
                clip_on=False,
            )
            niceplots.adjust_spines(takeoff_axs[idx_fig])

    # Label the start, decision and end points on the x axis
    xTicks = [0]
    for phase in ["v0v1", "rotate"]:
        xTicks.append(prob.get_val(f"{phase}.range", units="ft")[-1])
    for ax in takeoff_axs:
        ax.set_xticks(xTicks)

    takeoff_fig.legend(
        [r"V0 $\rightarrow$ V1", r"V1 $\rightarrow$ Vr", "Rotate", r"V1 $\rightarrow$ V0"],
        loc=(0.067, 0.6),
        fontsize="small",
    )
    takeoff_fig.suptitle("Takeoff phases")
    niceplots.save_figs(takeoff_fig, "takeoff_phases", ["png", "pdf"])
    plt.show()
