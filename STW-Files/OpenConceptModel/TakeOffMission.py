"""
==============================================================================
Take-off analysis model
==============================================================================
@File    :   TakeOffMission.py
@Date    :   2025/05/25
@Author  :   Alasdair Christison Gray
@Description : This class defines an OpenConcept "mission" that only includes the takeoff phases.
"""

# ==============================================================================
# Standard Python modules
# ==============================================================================

# ==============================================================================
# External Python modules
# ==============================================================================
import openmdao.api as om
from openconcept.mission.profiles import FullMissionAnalysis
from openconcept.mission.phases import (
    BFLImplicitSolve,
    GroundRollPhase,
    RotationPhase,
    RobustRotationPhase,
    ClimbAnglePhase,
)
import numpy as np

# ==============================================================================
# Extension modules
# ==============================================================================


class TakeoffAnalysis(FullMissionAnalysis):
    """
    A mission analysis class that only includes the takeoff analysis,
    inheriting from FullMissionWithReserve but customizing the setup
    to exclude climb, cruise, descent, and reserve phases.

    Inputs
    ------
    ac|* : various
        All relevant airplane design variables to pass to the airplane model.
    takeoff|h : float
        Takeoff altitude (default 0 ft).
    cruise|h0 : float
        Initial cruise altitude (default 28000 ft). Not used by takeoff phases.
        This parameter is kept for structural consistency with the parent class's
        mission parameters.
    mission_range : float
        Design range (default 1250 NM). Not used by takeoff phases.
        This parameter is kept for structural consistency.
    payload : float
        Mission payload (default 1000 lbm). Not used by takeoff phases.
        This parameter is kept for structural consistency.

    Outputs
    -------
    takeoff|v1 : float
        Decision speed.

    Options
    -------
    aircraft_model : class
        An aircraft model class with the standard OpenConcept interfaces.
    num_nodes : int
        Number of analysis points per phase.
    transition_method : str
        Analysis method for rotation/transition ("simplified" or "ode").
        Default "simplified".
    """

    def setup(self):
        nn = self.options["num_nodes"]
        acmodelclass = self.options["aircraft_model"]

        # Add mission parameters.
        mp = self.add_subsystem("missionparams", om.IndepVarComp(), promotes_outputs=["*"])
        mp.add_output("takeoff|h", val=0.0, units="ft")
        mp.add_output("takeoff|TempIncrement", val=np.full(nn, 0.0), units="degC")

        # ======================================================================
        # Takeoff phases (structure from FullMissionWithReserve.setup())
        # ======================================================================
        # add the four balanced field length takeoff phases and the implicit v1 solver
        # v0v1 - from a rolling start to v1 speed
        # v1vr - from the decision speed to rotation
        # rotate - in the air following rotation in 2DOF
        # v1v0 - emergency stopping from v1 to a stop.

        self.add_subsystem("bfl", BFLImplicitSolve(), promotes_outputs=["takeoff|v1"])
        v0v1 = self.add_subsystem(
            "v0v1",
            GroundRollPhase(num_nodes=nn, aircraft_model=acmodelclass, flight_phase="v0v1"),
            promotes_inputs=["ac|*", "takeoff|v1", ("fltcond|TempIncrement", "takeoff|TempIncrement")],
        )
        v1vr = self.add_subsystem(
            "v1vr",
            GroundRollPhase(num_nodes=nn, aircraft_model=acmodelclass, flight_phase="v1vr"),
            promotes_inputs=["ac|*", ("fltcond|TempIncrement", "takeoff|TempIncrement")],
        )
        self.connect("takeoff|v1", "v1vr.fltcond|Utrue_initial")
        self.connect("v0v1.range_final", "v1vr.range_initial")
        if self.options["transition_method"] == "simplified":
            rotate = self.add_subsystem(
                "rotate",
                RobustRotationPhase(num_nodes=nn, aircraft_model=acmodelclass, flight_phase="rotate"),
                promotes_inputs=["ac|*", ("fltcond|TempIncrement", "takeoff|TempIncrement")],
            )
        elif self.options["transition_method"] == "ode":
            rotate = self.add_subsystem(
                "rotate",
                RotationPhase(num_nodes=nn, aircraft_model=acmodelclass, flight_phase="rotate"),
                promotes_inputs=["ac|*", ("fltcond|TempIncrement", "takeoff|TempIncrement")],
            )
            self.connect("v1vr.fltcond|Utrue_final", "rotate.fltcond|Utrue_initial")
        else:
            raise IOError("Invalid option for transition method")
        self.connect("v1vr.range_final", "rotate.range_initial")
        self.connect("rotate.range_final", "bfl.distance_continue")
        self.connect("v1vr.takeoff|vr", "bfl.takeoff|vr")
        v1v0 = self.add_subsystem(
            "v1v0",
            GroundRollPhase(num_nodes=nn, aircraft_model=acmodelclass, flight_phase="v1v0"),
            promotes_inputs=["ac|*", "takeoff|v1", ("fltcond|TempIncrement", "takeoff|TempIncrement")],
        )
        self.connect("v0v1.range_final", "v1v0.range_initial")
        self.connect("v1v0.range_final", "bfl.distance_abort")
        # self.add_subsystem(
        #     "engineoutclimb",
        #     ClimbAnglePhase(num_nodes=1, aircraft_model=acmodelclass, flight_phase="EngineOutClimbAngle"),
        #     promotes_inputs=["ac|*", ("fltcond|TempIncrement", "takeoff|TempIncrement")],
        # )

        # ======================================================================
        # Phase linking for takeoff segments
        # ======================================================================
        self.link_phases(v0v1, v1vr, states_to_skip=["fltcond|Utrue", "range"])
        self.link_phases(v1vr, rotate, states_to_skip=["fltcond|Utrue", "range"])
        self.link_phases(v0v1, v1v0, states_to_skip=["fltcond|Utrue", "range"])
