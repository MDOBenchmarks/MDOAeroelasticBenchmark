"""
This model is defined in Berard and Isikvern "Conceptual Design Prediction
of the Buffet Envelope of Transport Aircraft" Journal of Aircraft, 2012.
"""

from dataclasses import dataclass

import numpy as np
from scipy.interpolate import Rbf


@dataclass
class BuffetGeometryParameters:
    sweep_max_thickness: float = 0.0  # deg
    aspect_ratio: float = 0.0
    taper_ratio: float = 0.0

    # value at wing tip
    thickness_to_chord_ratio: float = 0.0
    camber: float = 0.0
    chord_position_of_max_thickness: float = 0.0  # normalized by chord


@dataclass
class BuffetData:
    """
    Full set of buffet parameters
    """

    geom: BuffetGeometryParameters
    mach: float = 0.0
    cl: float = 0.0


def get_reference_buffet_envelope_lift_coefficient(mach: float):
    """
    Read the reference buffet CL vs Mach data
    """
    data = np.loadtxt("reference_buffet_envelope.dat", skiprows=2, delimiter=",")
    rbf = Rbf(data[:, 0], data[:, 1], function="multiquadric")
    return rbf(mach)


def get_reference_data(mach=0.77):
    return BuffetData(
        geom=BuffetGeometryParameters(
            # table 8 from the paper
            sweep_max_thickness=24.42,
            aspect_ratio=7.889,
            taper_ratio=0.2698,
            thickness_to_chord_ratio=0.1101,
            camber=0.0115,
            chord_position_of_max_thickness=0.3763,
        ),
        mach=mach,
        cl=get_reference_buffet_envelope_lift_coefficient(mach),
    )


def compute_sweep_max_thickness_from_sweep_quarter_chord(geom: BuffetGeometryParameters, sweep_quarter_chord: float):
    geom.sweep_max_thickness = np.rad2deg(
        np.arctan(
            np.tan(np.deg2rad(sweep_quarter_chord))
            + 4.0
            / geom.aspect_ratio
            * (geom.taper_ratio - 1.0)
            / (geom.taper_ratio + 1.0)
            * (geom.chord_position_of_max_thickness - 0.25)
        )
    )


@dataclass
class BuffetData2d:
    """
    Buffet information
    """

    mach: float = 0.0
    cl: float = 0.0
    thickness_to_chord_ratio: float = 0.0
    camber: float = 0.0


class SemiEmpiricalBuffetModel:
    # Regression constants from table 6
    K1 = -0.1024
    K2 = 1.0
    K3 = 2.4872
    K4 = 0.2963
    K5 = -1.0
    K6 = 3.1464
    TAU = 10.0
    BETA = 25.353
    THETA = 2.0364
    GAMMA = 10.050

    def compute_buffet_lift_coefficient(
        self,
        geom: BuffetGeometryParameters,
        data0: BuffetData = None,
    ):
        if data0 is None:
            data0 = get_reference_data()

        self.data_2d_0, self.data_2d_1 = self._compute_2d_transformed_data(geom, data0)

        self.cl_buffet1_2d = self._compute_2d_buffet_lift_coefficient(geom, data0, self.data_2d_0, self.data_2d_1)

        # reverse simple sweep theory to get 3D buffet
        cl = self._compute_3d_buffet_lift_coefficent(geom, self.cl_buffet1_2d)
        mach = self._compute_3d_buffet_mach_number(geom, self.data_2d_1)
        return mach, cl

    def _compute_2d_transformed_data(self, geom: BuffetGeometryParameters, data0: BuffetData):
        """
        Use simple sweep theory to get 2D reference conditions
        """

        data_2d_0 = BuffetData2d()
        cos0 = np.cos(np.deg2rad(data0.geom.sweep_max_thickness))

        # equations 8-11
        data_2d_0.mach = data0.mach * cos0
        data_2d_0.cl = data0.cl / (cos0**2.0)
        data_2d_0.thickness_to_chord_ratio = data0.geom.thickness_to_chord_ratio / cos0
        data_2d_0.camber = data0.geom.camber / cos0

        data_2d_1 = BuffetData2d()
        cos1 = np.cos(np.deg2rad(geom.sweep_max_thickness))

        # equations 12 - 13
        data_2d_1.thickness_to_chord_ratio = geom.thickness_to_chord_ratio / cos1
        data_2d_1.camber = geom.camber / cos1
        data_2d_1.mach = data_2d_0.mach

        return data_2d_0, data_2d_1

    def _compute_2d_buffet_lift_coefficient(
        self, geom: BuffetGeometryParameters, data0: BuffetData, data_2d_0: BuffetData2d, data_2d_1: BuffetData2d
    ):

        # equation 17a
        sweep0 = data0.geom.sweep_max_thickness
        alpha = self.K1 + self.K2 * data_2d_0.mach**self.K3
        fractional_increase_sweep = geom.sweep_max_thickness / data0.geom.sweep_max_thickness - 1.0
        phi_sweep = (1.0 + (self.TAU * sweep0) / (self.TAU * sweep0 + 1.0) * fractional_increase_sweep) ** alpha

        # equation 17b
        omega = self.K4 + self.K5 * data_2d_0.mach**self.K6
        fractional_increase_thickness = data_2d_1.thickness_to_chord_ratio / data_2d_0.thickness_to_chord_ratio - 1.0
        phi_thickness = (
            1.0
            + (omega * data_2d_0.thickness_to_chord_ratio)
            / (omega * data_2d_0.thickness_to_chord_ratio + 1.0)
            * fractional_increase_thickness
        ) ** self.BETA

        # equation 17c
        fractional_increase_camber = data_2d_1.camber / data_2d_0.camber - 1.0
        phi_camber = (
            1.0 + self.THETA * data_2d_0.camber / (self.THETA * data_2d_0.camber + 1.0) * fractional_increase_camber
        ) ** self.GAMMA

        # equation  18
        return data_2d_0.cl * phi_sweep * phi_thickness * phi_camber

    def _compute_3d_buffet_mach_number(self, geom: BuffetGeometryParameters, data_2d_1: BuffetData2d):
        # equation 20
        return data_2d_1.mach * 1.0 / np.cos(np.deg2rad(geom.sweep_max_thickness))

    def _compute_3d_buffet_lift_coefficent(self, geom: BuffetGeometryParameters, cl_buffet1_2d: float):
        # equation 21
        return cl_buffet1_2d * np.cos(np.deg2rad(geom.sweep_max_thickness)) ** 2.0

    def differentiate_buffet_lift(self, geom: BuffetGeometryParameters, data0: BuffetData):
        """
        differentiate the buffet computation using complex step
        """
        h = 1e-30
        dgeom = BuffetGeometryParameters()

        geom.aspect_ratio += h * 1.0j
        dgeom.aspect_ratio = np.imag(self.compute_buffet_lift_coefficient(geom, data0)) / h
        geom.aspect_ratio = np.real(geom.aspect_ratio)

        geom.sweep_max_thickness += h * 1.0j
        dgeom.sweep_max_thickness = np.imag(self.compute_buffet_lift_coefficient(geom, data0)) / h
        geom.sweep_max_thickness = np.real(geom.sweep_max_thickness)

        geom.taper_ratio += h * 1.0j
        dgeom.taper_ratio = np.imag(self.compute_buffet_lift_coefficient(geom, data0)) / h
        geom.taper_ratio = np.real(geom.taper_ratio)

        geom.thickness_to_chord_ratio += h * 1.0j
        dgeom.thickness_to_chord_ratio = np.imag(self.compute_buffet_lift_coefficient(geom, data0)) / h
        geom.thickness_to_chord_ratio = np.real(geom.thickness_to_chord_ratio)

        geom.camber += h * 1.0j
        dgeom.camber = np.imag(self.compute_buffet_lift_coefficient(geom, data0)) / h
        geom.camber = np.real(geom.camber)

        geom.chord_position_of_max_thickness += h * 1.0j
        dgeom.chord_position_of_max_thickness = np.imag(self.compute_buffet_lift_coefficient(geom, data0)) / h
        geom.chord_position_of_max_thickness = np.real(geom.chord_position_of_max_thickness)
        return dgeom
