import matplotlib.pyplot as plt
import numpy as np
import openmdao.api as om
from semiempirical_buffet_model import (
    BuffetGeometryParameters,
    SemiEmpiricalBuffetModel,
    compute_sweep_max_thickness_from_sweep_quarter_chord,
    get_reference_data,
)


class BuffetOnsetConstraint(om.ExplicitComponent):
    """
    The OpenMDAO component wraps the semiempirical buffet model into the constraint definition,
    a 30% margin for the cruise lift coffiecnt and the predicted buffet onset lift coefficient:
    1.3 CL_cruise < CL_buffet_onset

    The semi-empirical model is based on the ESDU reference data. The model is used to predict
    a buffet onset boundary based on a range of reference aircraft Mach numbers. The model outputs
    are then a set of (Mach, CL_buffet) values for the new aircraft which is then linearly
    interpolated to the cruise Mach number of the Benchmark case: 0.77.
    """

    def initialize(self):
        self.options.declare("mach_cruise", default=0.77, desc="cruise Mach number")
        self.options.declare("plot_buffet_boundary", default=False)
        self.call_counter = 0

    def setup(self):
        self.add_input("aspect_ratio", desc="The aspect ratio of the wing")
        self.add_input("taper_ratio", desc="The taper ratio of the wing")

        # values at the wing tip
        self.add_input("sweep_quarter_chord", desc="The sweep angle at the quart chord", units="deg")
        self.add_input("tc_ratio", desc="The thickness to chord ratio at the wing tip")
        self.add_input("camber", desc="The camber at the wing tip")
        self.add_input(
            "xc_max_thickness", desc="The chordwise position of the maximum thickness at the tip. Normalized by chord"
        )

        self.add_input("cl_cruise", desc="the cruise lift coefficient")

        self.add_output(
            "buffet_constraint",
            desc="The violation of the buffet constraint. Inequality constraint, i.e. should be < 0",
        )
        self.declare_partials("*", "*", method="cs")

    def compute(self, inputs, outputs):
        geom = BuffetGeometryParameters(
            sweep_max_thickness=-1,
            aspect_ratio=inputs["aspect_ratio"],
            taper_ratio=inputs["taper_ratio"],
            thickness_to_chord_ratio=inputs["tc_ratio"],
            camber=inputs["camber"],
            chord_position_of_max_thickness=inputs["xc_max_thickness"],
        )
        compute_sweep_max_thickness_from_sweep_quarter_chord(geom, sweep_quarter_chord=inputs["sweep_quarter_chord"])

        # Compute a semiempirical buffet boundary
        num = 16
        ref_machs = np.zeros(num)
        ref_cl_buffet = np.zeros(num)

        machs = np.zeros(num)
        cl_buffet = np.zeros(num)
        for i, mach in enumerate(np.linspace(0.4, 0.9, num=num)):
            ref_data = get_reference_data(mach)
            ref_machs[i] = ref_data.mach
            ref_cl_buffet[i] = ref_data.cl

            self.buffet_model = SemiEmpiricalBuffetModel()
            machs[i], cl_buffet[i] = self.buffet_model.compute_buffet_lift_coefficient(geom, ref_data)

        # linearly interpolate the semi-empirical buffet model to get the buffet CL at the cruise Mach number
        mach_cruise = self.options["mach_cruise"]
        for i in range(machs.size - 1):
            if machs[i] <= mach_cruise < machs[i + 1]:
                break
        else:
            raise ValueError("mach_cruise is outside of the bounds of the semiempirical buffet model evaluation range")

        cl_buffet_at_cruise_mach = cl_buffet[i] + (cl_buffet[i + 1] - cl_buffet[i]) * (mach_cruise - machs[i]) / (
            machs[i + 1] - machs[i]
        )

        outputs["buffet_constraint"] = inputs["cl_cruise"] * 1.3 - cl_buffet_at_cruise_mach

        if self.options["plot_buffet_boundary"] and self.comm.rank == 0:
            plt.figure()
            plt.plot(ref_machs, ref_cl_buffet, "s", label="Reference buffet boundary")
            plt.plot(machs, cl_buffet, "x", label="Computed buffet boundary")
            plt.legend()
            plt.xlabel("Mach")
            plt.ylabel("CL")
            plt.savefig(f"buffet_boundary_iteration{self.call_counter}.png")
            plt.close()
            self.call_counter += 1
