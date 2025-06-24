# Balanced Field Length Calculation

This directory contains a simple model you can use for calculating the balanced field length (BFL) during your optimizations.
The model is quick to run and has analytically computed gradients.

The takeoff trajectory used in the calculation has 4 phases:

- v0 -> v1: The aircraft accelerates from a standstill to the decision speed, v1, with both engines at full throttle.
- v1 -> vr: The aircraft accelerates from the decision speed, v1, to the rotation speed, vr, with engine at full throttle, the other engine is assumed to have failed.
- vr -> v2: The aircraft rotates, takes off, and climbs to an altitude of 35ft, accelerating to v2, still with only one engine at full throttle.
- v1 -> v0: The aircraft rejects the takeoff at the decision speed, decelerating from v1 to a standstill with both engines at idle. This phases is linked to the end of the v0 -> v1 phase.

Drag throughout the calculation is computed using a simple drag model:

$$ C_D = C_{D0} + \frac{C_L^2}{\pi e AR} $$

The zero-lift drag coefficient, $C_{D0}$, is computed for the whole aircraft using equations from Roskam and Raymer.
The Oswald efficiency factor, $e$ is assumed to be 0.9 throughout the calculation.

During the acceleration and rotation phases, the rolling resistance of the aircraft is assumed to be 0.03, the deceleration phase models the application of the brakes by increasing this to 0.4, a typical value for a dry asphalt runway.

The rotation speed vr is 110% of the stall speed, $V_{S}$, which is computed using a maximum lift coefficient estimated using the methods of Raymer (Equation 12.15, 1992 edition) and Roskam (Equations 8.18, 8.29, 8.30, 1989 Edition).
A flap setting of 20 degrees (the maximum takeoff flap setting for a Boeing 717) is assumed throughout.

The decision speed, v1, is solved for during the analysis, such that the distance required to decelerate from v1 to a standstill is equal to the distance required to continue the takeoff and reach a height of 35ft with one engine inoperative.

The following parameters are assumed to vary during optimization:

- Takeoff mass
- Wing area
- Wing aspect ratio
- Wing taper ratio
- Wing quarter-chord sweep
- Wing thickness-to-chord ratio

## Using the Model

There are two ways to use the model.

### 1. In your own OpenMDAO model

If you are using OpenMDAO already, you can add the BFL calculation as a group in your model:

```python
from STWFiles.OMGroups import STWTakeoffAnalysisGroup
.
.
.
# Add the group to your model
inputs = [
    "ac|geom|wing|S_ref",
    "ac|geom|wing|AR",
    "ac|geom|wing|c4sweep",
    "ac|geom|wing|taper",
    "ac|geom|wing|toverc",
    "ac|weights|MTOW",
]
BFLGroup = STWTakeoffAnalysisGroup(num_nodes=numNodes, ivc_excludes=inputs)
self.add_subsystem("BFLGroup", BFLGroup, promotes_inputs=inputs)
.
.
.
```

By default, all the variables expected to change during optimization will be included in an `IndepVarComp` within the
group. If you are using this takeoff analysis group as part of a larger OpenMDAO model, where you want these values to
instead come from the outputs of other components, you can exclude them from the `IndepVarComp` by passing a list of
variable names to the `ivc_excludes` argument.

Set the following initial values for the model after you have run `setup` on your problem:

```python
prob.setup()

# Initial guesses for takeoff speeds to help with convergence
prob.set_val("BFLGroup.v0v1.fltcond|Utrue", np.full(numNodes, 50), units="kn")
prob.set_val("BFLGroup.v1vr.fltcond|Utrue", np.full(numNodes, 85), units="kn")
prob.set_val("BFLGroup.v1v0.fltcond|Utrue", np.full(numNodes, 85), units="kn")

# Need these if using ODE transition method
prob.set_val("BFLGroup.rotate.fltcond|Utrue", np.full(numNodes, 90), units="kn")
prob.set_val("BFLGroup.rotate.accel_vert", np.full(numNodes, 0.1), units="m/s**2")
```

See the `OMGroups.py` file for a full example of how to use the `STWTakeoffAnalysisGroup` group.

### 2. As a standalone model

If you are not using OpenMDAO, and don't want to learn how, use the wrapper class in `BFLCalculation.py` to run the BFL calculation as a standalone model.
The wrapper class has simple methods for setting the inputs, running the BFL calculation, and computing the gradients:

```python
from pprint import pprint
import nump as np
from STWFiles.BFLCalculation import BFLCalculation

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
plt.show()
```

See `BFLCalculation.py` for more details of the methods of the class and their inputs/outputs.
