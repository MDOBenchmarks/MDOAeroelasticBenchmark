"""
==============================================================================
Balanced Field Length Calculation Model
==============================================================================
@File    :   BFLCalculation.py
@Date    :   2025/06/23
@Author  :   Alasdair Christison Gray
@Description : This file contains a class that wraps a Balanced Field Length
(BFL) calculation performed using OpenMDAO and OpenConcept. The wrapper allows
you to integrate the BFL calculation into your own models without having to
interact directly with the OpenMDAO model yourself.
"""

# ==============================================================================
# Standard Python modules
# ==============================================================================
from pprint import pprint
from difflib import get_close_matches
import os
import copy

# ==============================================================================
# External Python modules
# ==============================================================================
import numpy as np
import openmdao.api as om
import matplotlib.pyplot as plt

# ==============================================================================
# Extension modules
# ==============================================================================
from OMGroups import STWTakeoffAnalysisGroup


class BFLCalculation:
    INPUT_MAP = {
        "togm": "ac|weights|MTOW",
        "wing_area": "ac|geom|wing|S_ref",
        "wing_aspect_ratio": "ac|geom|wing|AR",
        "wing_c4_sweep": "ac|geom|wing|c4sweep",
        "wing_taper": "ac|geom|wing|taper",
        "wing_toverc": "ac|geom|wing|toverc",
    }
    INPUT_UNITS = {
        "togm": "kg",
        "wing_area": "m**2",
        "wing_aspect_ratio": None,  # dimensionless
        "wing_c4_sweep": "deg",
        "wing_taper": None,  # dimensionless
        "wing_toverc": None,  # dimensionless
    }
    OUTPUT_MAP = {
        "balanced_field_length": "bfl.distance_continue",
        "v1": "takeoff|v1",
        "vr": "bfl.takeoff|vr",
    }
    OUTPUT_UNITS = {
        "balanced_field_length": "m",
        "v1": "m/s",
        "vr": "m/s",
    }

    def __init__(
        self,
        num_nodes=11,
    ):
        """Create an instance of the BFLCalculation class.

        Parameters
        ----------
        num_nodes : int, optional
            Number of points used for ODE integration in each of the 4 takeoff phases, by default 11
        """
        self.om_problem = om.Problem()
        self.om_problem.model = STWTakeoffAnalysisGroup(num_nodes=num_nodes)
        self.om_problem.setup()

        # NOTE: It looks like there are some issues with the OpenConcept takeoff model not converting properly between
        # true and equivalent airspeed, which makes the results a bit off if you try to do the takeoff analysis at
        # anything other than sea-level standard atmospheric conditions. So we'll just do the takeoff at standard
        # sea-level conditions for now.

        # self.om_problem.set_val("takeoff|TempIncrement", np.full(numNodes, 15), units="degC")

        # Guesses for takeoff speeds to help with convergence
        self.om_problem.set_val("v0v1.fltcond|Utrue", np.full(num_nodes, 50), units="kn")
        self.om_problem.set_val("v1vr.fltcond|Utrue", np.full(num_nodes, 85), units="kn")
        self.om_problem.set_val("v1v0.fltcond|Utrue", np.full(num_nodes, 85), units="kn")

        # Need these if using ODE transition method
        self.om_problem.set_val("rotate.fltcond|Utrue", np.full(num_nodes, 90), units="kn")
        self.om_problem.set_val("rotate.accel_vert", np.full(num_nodes, 0.1), units="m/s**2")

        self.outputs_up_to_date = False

    def set_inputs(self, inputs):
        """Set the input values for the BFL calculation.

        Parameters
        ----------
        inputs : dict
            Dictionary containing as many of the following values as you want to set:
            - "togm": Takeoff gross mass (kg)
            - "wing_area": Wing area (m^2)
            - "wing_aspect_ratio": Wing aspect ratio
            - "wing_c4_sweep": Wing C4 sweep angle (degrees)
            - "wing_taper": Wing taper ratio
            - "wing_toverc": Wing thickness-to-chord ratio
        """
        for name, om_name in self.INPUT_MAP.items():
            try:
                self.om_problem.set_val(om_name, inputs[name], units=self.INPUT_UNITS[name])
                self.outputs_up_to_date = False
            except KeyError as e:
                # If the input name is not found, try to find a close match
                closest_match = get_close_matches(name, self.INPUT_MAP.keys(), n=1, cutoff=0.0)[0]
                raise KeyError(
                    f"Input '{name}' not found. Did you mean '{closest_match}'? "
                    f"Available inputs are: {list(self.INPUT_MAP.keys())}"
                ) from e

    def get_inputs(self):
        """Get the currently set input values for the BFL calculation."""
        inputs = {}
        for name, om_name in self.INPUT_MAP.items():
            inputs[name] = self.om_problem.get_val(om_name, units=self.INPUT_UNITS[name])[0]
        return inputs

    def get_outputs(self):
        """Get the outputs of the BFL calculation.

        Returns
        -------
        outputs : dict
            Dictionary containing the outputs of the BFL calculation:
            - "balanced_field_length": The balanced field length (m)
            - "v1": The V1 speed (m/s)
            - "vr": The VR speed (m/s)
        """
        outputs = {}
        for name, om_name in self.OUTPUT_MAP.items():
            outputs[name] = self.om_problem.get_val(om_name, units=self.OUTPUT_UNITS[name])[0]
        return outputs

    def run_model(self):
        """Run the BFL analysis with the current inputs and return the outputs.

        Returns
        -------
        outputs : dict
            Dictionary containing the outputs of the BFL calculation:
            - "balanced_field_length": The balanced field length (m)
            - "v1": The V1 speed (m/s)
            - "vr": The VR speed (m/s)
        """
        if not self.outputs_up_to_date:
            self.om_problem.run_model()
            self.outputs_up_to_date = True
        return self.get_outputs()

    def compute_gradients(self):
        """Compute the gradients of the outputs with respect to the inputs.

        The BFL analysis will be run first is the outputs are not up to date.

        Returns
        -------
        dict
            Nested dictionary containing the gradients of each output with respect to each input.
            ``gradients[output][input]`` is the gradient of ``output`` with respect to ``input``.
        """
        if not self.outputs_up_to_date:
            self.run_model()
        om_gradients = self.om_problem.compute_totals(
            of=list(self.OUTPUT_MAP.values()), wrt=list(self.INPUT_MAP.values()), return_format="dict"
        )
        gradients = {output_name: {} for output_name in self.OUTPUT_MAP.keys()}
        for output_name, om_output_name in self.OUTPUT_MAP.items():
            for input_name, om_input_name in self.INPUT_MAP.items():
                gradients[output_name][input_name] = om_gradients[om_output_name][om_input_name]
        return gradients

    def write_n2(self, filename=None):
        """Write the N2 diagram of the OpenMDAO model to a file.

        Parameters
        ----------
        filename : _type_, optional
            Name of file, with or with .html extension, by default None in which case the N2 diagram is written to
            'BFLCalculation_N2.html' in the current working directory.
        """
        if filename is None:
            filename = "BFLCalculation_N2.html"
        else:
            # extract the filename without extension
            filename_no_ext = os.path.splitext(filename)[0]
            filename = f"{filename_no_ext}.html"
        om.n2(self.om_problem, show_browser=False, outfile=filename)

    def plot_trajectory(self):
        """Plot the takeoff trajectory based on the results of the last run of the model.

        Returns
        -------
        matplob figure object
            The figure object containing the plot.
        list of 3 matplotlib axes objects
            The axes for the 3 subplots in the figure.
        """
        takeoff_fig, takeoff_axes = plt.subplots(1, 3, figsize=[12, 5])
        takeoff_axes = takeoff_axes.flatten()  # change 1x3 mtx of axes into 3-element vector

        # Define variables to plot
        takeoff_vars = [
            {"var": "fltcond|h", "name": "Altitude", "units": "ft"},
            {"var": "fltcond|Utrue", "name": "True airspeed", "units": "kn"},
            {"var": "throttle", "name": "Throttle", "units": None},
        ]

        for idx_fig, var in enumerate(takeoff_vars):
            takeoff_axes[idx_fig].set_xlabel("Range (ft)")
            takeoff_axes[idx_fig].set_ylabel(
                f"{var['name']}" if var["units"] is None else f"{var['name']} ({var['units']})"
            )

            # Loop through each flight phase and plot the current variable from each
            for phase in ["v0v1", "v1vr", "rotate", "v1v0"]:
                takeoff_axes[idx_fig].plot(
                    self.om_problem.get_val(f"{phase}.range", units="ft"),
                    self.om_problem.get_val(f"{phase}.{var['var']}", units=var["units"]),
                    "-o",
                    markersize=8.0,
                    clip_on=False,
                )

        takeoff_fig.legend(
            [r"V0 $\rightarrow$ V1", r"V1 $\rightarrow$ Vr", "Rotate", r"V1 $\rightarrow$ V0"],
            loc=(0.067, 0.6),
            fontsize="small",
        )
        takeoff_fig.suptitle("Takeoff phases")
        return takeoff_fig, takeoff_axes


if __name__ == "__main__":
    model = BFLCalculation()

    # Run model with default values
    outputs = model.run_model()
    model.write_n2("DefaultValues")
    print("With default values:")
    pprint(model.get_inputs())
    pprint(outputs)
    print("\n")

    # Try with values from my SciTech 2025 Case 3 design
    AR = 19.21
    S = 2 * 49.53
    LE_SWEEP = 31.52
    TAPER_RATIO = 0.2
    T_OVER_C = 0.12
    c4_sweep = np.rad2deg(
        np.arctan(np.tan(np.deg2rad(LE_SWEEP)) - 4 * 0.25 * (1 - TAPER_RATIO) / (AR * (1 + TAPER_RATIO)))
    )
    inputs = {
        "togm": 59430.82,
        "wing_area": 2 * 49.53,
        "wing_aspect_ratio": 19.21,
        "wing_c4_sweep": c4_sweep,
        "wing_taper": TAPER_RATIO,
        "wing_toverc": T_OVER_C,
    }
    model.set_inputs(inputs)
    outputs = model.run_model()
    model.write_n2("Case3Values")
    print("\n\nWith SciTech 2025 Case 3 values:")
    pprint(model.get_inputs())
    pprint(outputs)
    print("\n")

    # Plot the trajectory
    model.plot_trajectory()

    # Compute gradients
    gradients = model.compute_gradients()
    print("\n\nGradients:")
    pprint(gradients)

    # Test gradients against finite difference
    fd_gradients = {}
    x0 = model.get_inputs()
    h = 1e-4  # Relative step size for finite difference
    for output_name in model.OUTPUT_MAP.keys():
        fd_gradients[output_name] = {}

    for input_name in model.INPUT_MAP.keys():
        # Perturb the input
        x_pert = copy.deepcopy(x0)
        x_pert[input_name] *= 1 + h
        model.set_inputs(x_pert)
        outputs_pert = model.run_model()
        for output_name in model.OUTPUT_MAP.keys():
            fd_gradients[output_name][input_name] = (outputs_pert[output_name] - outputs[output_name]) / (
                x_pert[input_name] - x0[input_name]
            )

    print("\n\nFinite difference gradients:")
    pprint(fd_gradients)

    # Compare the two sets of gradients
    for output_name in model.OUTPUT_MAP.keys():
        print(f"\nGradients for output '{output_name}', w.r.t:")
        for input_name in model.INPUT_MAP.keys():
            grad = gradients[output_name][input_name][0, 0]
            fd_grad = fd_gradients[output_name][input_name]
            rel_error = np.abs((grad - fd_grad) / fd_grad) if fd_grad != 0 else np.inf
            print(
                f"  {input_name}:\n"
                f"           Analytical: {grad:.6g}\n"
                f"    Finite Difference: {fd_grad:.6g}\n"
                f"       Relative Error: {rel_error:.6g}\n"
            )

    # Show the plot
    plt.show()
