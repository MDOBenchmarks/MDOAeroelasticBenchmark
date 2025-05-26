import openmdao.api as om

# import numpy as np # Not strictly needed for this setup

# It is assumed that when this model is used, the necessary data from
# STWSpecs.py and wingGeometry.py will be loaded and passed as inputs
# to this STWAircraftModel group, for example, via prob.model.set_input_defaults(...)
# or by connecting them from an IndepVarComp holding these spec values.
# e.g.:
# from AircraftSpecs.STWSpecs import aircraftSpecs
# from geometry.wingGeometry import wingGeometry

# Import OpenConcept components
from openconcept.aerodynamics.drag_jet_transport import ParasiteDragCoefficient_JetTransport
from openconcept.aerodynamics import PolarDrag  # Corrected import and combined PolarDrag
from openconcept.utilities import AddSubtractComp, ElementMultiplyDivideComp, Integrator


class SuperBasicTurboFan(om.ExplicitComponent):
    """This is the most basic engine model possible, it simply scales a thrust rating by a throttle and density values,
    then computes fuel flow based on a constant TSFC"""

    def initialize(self):
        self.options.declare("num_nodes", default=1, types=int, desc="Number of analysis points")
        self.options.declare(
            "rated_rho", default=1.22494, types=float, desc="Air density corresponding to rated thrust (kg/m^3)"
        )
        self.options.declare("tsfc", types=float, default=18.1e-6, desc="Thrust-specific fuel consumption (kg/N/s)")

    def setup(self):
        nn = self.options["num_nodes"]

        # Inputs
        self.add_input("throttle", shape=(nn,), desc="Engine throttle (0 to 1)", units=None)
        self.add_input("ac|propulsion|engine|rating", shape=(), desc="Rated thrust of the engine (N)", units="N")
        self.add_input("fltcond|rho", shape=(nn,), desc="Air density at flight condition (kg/m^3)", units="kg/m**3")

        # Outputs
        self.add_output("thrust", shape=(nn,), desc="Thrust produced by the engine (N)", units="N")
        self.add_output("fuel_flow", shape=(nn,), desc="Fuel flow rate (kg/s)", units="kg/s")

        # Partial derivatives
        # These partials are a diagonal matrix
        self.declare_partials(of="*", wrt=["throttle", "fltcond|rho"], rows=range(nn), cols=range(nn))
        # These partials are vectors
        self.declare_partials(of="*", wrt=["ac|propulsion|engine|rating"])

    def compute(self, inputs, outputs):
        throttle = inputs["throttle"]
        rated_thrust = inputs["ac|propulsion|engine|rating"]
        rho = inputs["fltcond|rho"]
        tsfc = self.options["tsfc"]
        rated_rho = self.options["rated_rho"]

        # Compute thrust
        outputs["thrust"] = throttle * rated_thrust * (rho / rated_rho)

        # Compute fuel flow
        outputs["fuel_flow"] = outputs["thrust"] * tsfc

    def compute_partials(self, inputs, partials):
        throttle = inputs["throttle"]
        rated_thrust = inputs["ac|propulsion|engine|rating"]
        rho = inputs["fltcond|rho"]
        tsfc = self.options["tsfc"]
        rated_rho = self.options["rated_rho"]

        # Partial derivatives for thrust
        partials["thrust", "throttle"] = rated_thrust * (rho / rated_rho)
        partials["thrust", "fltcond|rho"] = throttle * rated_thrust / rated_rho
        partials["thrust", "ac|propulsion|engine|rating"] = throttle * (rho / rated_rho)

        # Partial derivatives for fuel flow
        for inp in ["throttle", "fltcond|rho", "ac|propulsion|engine|rating"]:
            partials["fuel_flow", inp] = partials["thrust", inp] * tsfc


class STWAircraftModel(om.Group):
    """
    STWAircraftModel is an OpenConcept-compatible aircraft model for the STW benchmark.

    It features:
    - Simple thrust model: rated_thrust * throttle
    - Drag model: ParasiteDragCoefficient_JetTransport for CD0 + calculated induced drag
    - CLmax model: CleanCLmax and FlapCLmax
    - Weight model: Takes MTOW (or similar) as a direct input (DV)
    - No fuel burn integration within this model
    """

    def initialize(self):
        self.options.declare("num_nodes", default=1, types=int, desc="Number of analysis points")
        self.options.declare(
            "flight_phase", default=None, types=str, desc="Current flight phase (e.g., 'cruise', 'takeoff')"
        )

    def setup(self):
        nn = self.options["num_nodes"]
        flight_phase = self.options["flight_phase"]

        # --- Propulsion ---
        self.add_subsystem(
            "BasicTurboFan",
            SuperBasicTurboFan(num_nodes=nn),
            promotes_inputs=["throttle", "fltcond|rho", "ac|propulsion|engine|rating"],
        )

        # -------------- Multiply fuel flow and thrust by the number of active engines --------------
        # propulsor_active is 0 if failed engine and 1 otherwise, so
        # num active engines = num engines - 1 + propulsor_active
        self.add_subsystem(
            "num_engine_calc",
            AddSubtractComp(
                output_name="num_active_engines",
                input_names=["num_engines", "propulsor_active", "one"],
                vec_size=[1, nn, 1],
                scaling_factors=[1, 1, -1],
            ),
            promotes_inputs=[("num_engines", "ac|propulsion|num_engines"), "propulsor_active"],
        )
        self.set_input_defaults("num_engine_calc.one", 1.0)

        prop_mult = self.add_subsystem(
            "propulsion_multiplier", ElementMultiplyDivideComp(), promotes_outputs=["thrust"]
        )
        prop_mult.add_equation(
            output_name="thrust",
            input_names=["thrust_per_engine", "num_active_engines_1"],
            vec_size=nn,
            input_units=["lbf", None],
        )
        prop_mult.add_equation(
            output_name="fuel_flow",
            input_names=["fuel_flow_per_engine", "num_active_engines_2"],
            vec_size=nn,
            input_units=["kg/s", None],
        )
        self.connect("BasicTurboFan.fuel_flow", "propulsion_multiplier.fuel_flow_per_engine")
        self.connect("BasicTurboFan.thrust", "propulsion_multiplier.thrust_per_engine")

        # This hacky thing is necessary to enable two equations to pull from the same input
        self.connect(
            "num_engine_calc.num_active_engines",
            ["propulsion_multiplier.num_active_engines_1", "propulsion_multiplier.num_active_engines_2"],
        )

        # ==============================================================================
        # Weight
        # ==============================================================================
        # -------------- Integrate fuel burn --------------
        integ = self.add_subsystem(
            "fuel_burn_integ", Integrator(num_nodes=nn, diff_units="s", method="simpson", time_setup="duration")
        )
        integ.add_integrand(
            "fuel_burn",
            rate_name="fuel_flow",
            rate_units="kg/s",
            lower=0.0,
            upper=1e6,
        )
        self.connect("propulsion_multiplier.fuel_flow", "fuel_burn_integ.fuel_flow")

        # -------------- Subtract fuel burn from takeoff weight --------------
        self.add_subsystem(
            "weight_calc",
            AddSubtractComp(
                output_name="weight",
                input_names=["ac|weights|MTOW", "fuel_burn"],
                scaling_factors=[1, -1],
                vec_size=[1, nn],
                units="kg",
            ),
            promotes_inputs=["ac|weights|MTOW"],
            promotes_outputs=["weight"],
        )
        self.connect("fuel_burn_integ.fuel_burn", "weight_calc.fuel_burn")

        # --- Aerodynamics ---
        # Determine aerodynamic configuration based on flight_phase
        # Common phases for takeoff configuration: "v0v1", "v1v0", "v1vr", "rotate"
        # Add more phases as per your mission definition
        is_takeoff_config = flight_phase in ["v0v1", "v1v0", "v1vr", "rotate"]
        aero_config = "takeoff" if is_takeoff_config else "clean"

        # 1. Parasite Drag Coefficient (CD0)
        # Inputs like ac|geom|fuselage|length, ac|geom|wing|S_ref, etc., are expected
        # to be connected or have defaults set from STWSpecs.py and wingGeometry.py.
        parasite_drag_promos = [
            "fltcond|Utrue",
            "fltcond|rho",
            "fltcond|T",
            "ac|geom|fuselage|length",
            "ac|geom|fuselage|height",
            "ac|geom|fuselage|S_wet",
            "ac|geom|hstab|S_ref",
            "ac|geom|hstab|AR",
            "ac|geom|hstab|taper",
            "ac|geom|hstab|toverc",
            "ac|geom|vstab|S_ref",
            "ac|geom|vstab|AR",
            "ac|geom|vstab|taper",
            "ac|geom|vstab|toverc",
            "ac|geom|wing|S_ref",
            "ac|geom|wing|AR",
            "ac|geom|wing|taper",
            "ac|geom|wing|toverc",
            "ac|geom|nacelle|length",
            "ac|geom|nacelle|S_wet",
            "ac|propulsion|num_engines",
        ]
        # Add inputs specific to takeoff configuration if needed by ParasiteDragCoefficient_JetTransport
        if aero_config == "takeoff":
            parasite_drag_promos.extend(["ac|aero|takeoff_flap_deg", "ac|geom|wing|c4sweep"])

        self.add_subsystem(
            "parasite_drag",
            ParasiteDragCoefficient_JetTransport(num_nodes=nn, include_wing=True, configuration=aero_config),
            promotes_inputs=parasite_drag_promos,
        )

        # 2. Total Drag Calculation using PolarDrag
        # ac|aero|polar|e (Oswald efficiency) and other geometric params are expected as inputs.
        self.add_subsystem(
            "drag_polar",
            PolarDrag(
                num_nodes=nn, vec_CD0=True
            ),  # vec_CD0=True because CD0 comes from parasite_drag and has shape (nn,)
            promotes_inputs=[
                "fltcond|CL",
                "fltcond|q",
                "ac|geom|wing|S_ref",
                "ac|geom|wing|AR",
                ("e", "ac|aero|polar|e"),  # Oswald efficiency factor
            ],
            promotes_outputs=["drag"],
        )
        self.connect("parasite_drag.CD0", "drag_polar.CD0")
