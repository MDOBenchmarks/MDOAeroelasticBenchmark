import numpy as np
import pytest
from semiempirical_buffet_model import (
    BuffetData,
    BuffetGeometryParameters,
    SemiEmpiricalBuffetModel,
    compute_sweep_max_thickness_from_sweep_quarter_chord,
    get_reference_data,
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


@pytest.fixture
def ref_aircraft_geom():
    sweep_quarter_chord = 33.1
    ref_aircraft = BuffetGeometryParameters(
        sweep_max_thickness=-1,
        thickness_to_chord_ratio=0.105,
        camber=0.0110,
        chord_position_of_max_thickness=0.370,
        aspect_ratio=6.81,
        taper_ratio=0.328,
    )
    compute_sweep_max_thickness_from_sweep_quarter_chord(ref_aircraft, sweep_quarter_chord)
    assert ref_aircraft.sweep_max_thickness == pytest.approx(31.6, abs=0.1)
    return ref_aircraft


@pytest.fixture
def target_aircraft_geom():
    sweep_quarter_chord = 27.0
    target_aircraft = BuffetGeometryParameters(
        sweep_max_thickness=-1.0,
        thickness_to_chord_ratio=0.130,
        camber=0.0150,
        chord_position_of_max_thickness=0.400,
        aspect_ratio=9.0,
        taper_ratio=0.25,
    )
    compute_sweep_max_thickness_from_sweep_quarter_chord(target_aircraft, sweep_quarter_chord)
    assert target_aircraft.sweep_max_thickness == pytest.approx(25.2, abs=0.1)
    return target_aircraft


def test_2d_transforms(ref_aircraft_geom, target_aircraft_geom):
    model = SemiEmpiricalBuffetModel()
    ref_data = BuffetData(geom=ref_aircraft_geom, mach=0.8, cl=0.6)
    ref_2d, target_2d = model._compute_2d_transformed_data(target_aircraft_geom, ref_data)

    assert ref_2d.thickness_to_chord_ratio == pytest.approx(0.1233, abs=0.0001)
    assert ref_2d.camber == pytest.approx(0.01292, abs=0.000001)

    assert target_2d.thickness_to_chord_ratio == pytest.approx(0.1436, abs=0.0001)
    assert target_2d.camber == pytest.approx(0.01658, abs=0.00001)


def test_recovery_of_esdu_reference_data():
    mach = 0.77
    target = get_reference_data(mach).geom
    ref = get_reference_data(mach)

    model = SemiEmpiricalBuffetModel()
    buffet_mach, buffet_cl = model.compute_buffet_lift_coefficient(target, ref)
    assert buffet_mach == pytest.approx(mach)
    assert buffet_cl == pytest.approx(0.7722)
