# Data Upload Instructions

These instructions describe the folder and file structure required for uploading your results for the three optimization cases and benchmark analyses.
Please follow the folder/file/column naming conventions exactly to ensure everyone's results can be processed automatically.

To create all the necessary folders and CSV template files, following the instructions below, you can use the provided `CreateSubmissionDirs.py` script in the `Data` directory:

```bash
python CreateSubmissionDirs.py ParticipantName
```

## 1

Make a subfolder inside the `Data` folder with the name you'd like to use to identify your results (e.g., your initials or organization name).
Then create `BenchmarkAnalyses` and `Case1/2/3` folders inside that folder, e.g:

```
Data
└── ParticipantName
    ├── BenchmarkAnalyses
    ├── Case1
    ├── Case2
    └── Case3
```

## 2 Benchmark Analysis Results

If you ran benchmark analyses with multiple meshes, **please only upload results for the meshes you used in your optimizations.**

Create the following folder and file structure for benchmark analysis results:

```
Data/
└── ParticipantName
    ├── BenchmarkAnalyses
    │   ├── Aero
    │   ├── Aeroelastic
    │   └── Struct
```

### 2.1 Aerodynamic Results

Place a CSV file named `RigidPolarResults.csv` inside `BenchmarkAnalyses/Aero` with the following columns:

- `aoa`: Angle of attack in degrees
- `cl`: Lift coefficient
- `cd`: Drag coefficient

### 2.2 Structural Results

Place a CSV file named `StructAnalysisResults.csv` inside `BenchmarkAnalyses/Struct` with the following columns:

- `tip disp`: Tip z displacement in meters
- `tip twist`: Tip twist in degrees
- `comp`: Compliance in kJ
- `mat fos`: Material failure factor of safety
- `buckling fos`: Buckling failure factor of safety

### 2.3 Aeroelastic Results

Place a CSV file named `AeroelasticAnalysisResults.csv` inside `BenchmarkAnalyses/Aeroelastic` with the following columns:

- `cl`: Lift coefficient
- `cd`: Drag coefficient
- `tip disp`: Tip z displacement in meters
- `tip twist`: Tip twist in degrees
- `comp`: Compliance in kJ
- `mat fos`: Material failure factor of safety
- `buckling fos`: Buckling failure factor of safety

## 3 Case 1 Results

Create the following folder and file structure for Case 1 results:

```
Data/
└── ParticipantName
    ├── Case1
    │   ├── SpanwiseDistributions
    │   └── StructSizing
```

Please supply results files for your **optimised design only**, since we may all have used different initial designs.

### 3.1 Spanwise Distributions

For maximum flexibility, please upload each distribution for each flight condition as a separate CSV file inside the `SpanwiseDistributions` folder with the following naming convention:

- `PullupLiftDist.csv`
- `PullupTwistDist.csv`
- `PushdownLiftDist.csv`
- `PushdownTwistDist.csv`

In the lift distribution files, include the following columns:

- `eta`: Normalised spanwise coordinate (0 at root, 1 at tip)
- `lift`: Normalised lift per unit span (lift per unit span divided by spanwise average lift per unit span)

In the twist distribution files, include the following columns:

- `eta`: As above
- `twist`: Local twist in degrees

### 3.2 Structural Sizing

Add a CSV file named `StructSizing.csv` inside the `StructSizing` folder with the following columns:

- `USkin thickness`: Upper skin equivalent thickness in meters
- `LSkin thickness`: Lower skin equivalent thickness in meters
- `FSpar thickness`: Front spar equivalent thickness in meters
- `RSpar thickness`: Rear spar equivalent thickness in meters

Values should be ordered from the symmetry plane (first row) to the wingtip (last row).

### 3.3 Quantities of Interest

Add a CSV file named `QoI.csv` inside the `Case1` folder with the following columns:

- `M_wingbox`: Wingbox mass in kg
- `M_wing`: Total wing mass in kg
- `LGM`: Landing gross mass in kg
- `aoa_pullup`: Pull-up manoeuvre angle of attack in degrees
- `aoa_pushdown`: Push-down manoeuvre angle of attack in degrees

## 4 Case 2 Results

Create a folder named `Case2` inside your participant folder with the following structure:

```
Data/
└── ParticipantName
    └── Case2
        ├── PostOptPolar
        ├── SectionShapes
        ├── SpanwiseDistributions
        └── StructSizing
```

Upload all of the same results files as for Case 1, plus the following additions:

### 4.1 Additional Spanwise Distributions

Include lift and twist distributions for the cruise flight condition in `CruiseLiftDist.csv` and `CruiseTwistDist.csv` files, and the jig twist distribution in `JigTwistDist.csv`.

### 4.2 Additional Quantities of Interest

Including the following additional columns in the `QoI.csv` file:

- `TOGM`: Take-off gross mass in kg
- `M_fuel`: Mission fuel burn in kg
- `aoa_cruise`: Cruise angle of attack in degrees
- `L/D`: Cruise lift-to-drag ratio (including airframe drag)
- `tank usage`: Total fuel volume (fuel burn plus reserves) as a fraction of total tank volume

### 4.3 Wing Section Shapes

Upload a separate CSV file for each wing section at 10, 30, 50, 70, 90% span and for the jig and cruise shapes inside the `SectionShapes` folder with the naming convention `Section<X><Cruise/Jig>.csv`, e.g. `Section10Cruise.csv`, `Section90Jig.csv`.

Each file should contain the following columns:

- `x`: Normalised chordwise coordinate (0 at leading edge, 1 at trailing edge)
- `z`: Normalised vertical coordinate (0 at leading edge, divided by chord length)
- `cp`: Pressure coefficient (for the cruise shape files only)

### 4.4 Post-Optimization Polar

Place a CSV file named `PostOptPolar.csv` inside the `PostOptPolar` folder containing the L/D values from the Mach/alpha polar following the template below:

```csv
  ,	0.75, 0.77, 0.79
-1,14.46,14.55,14.6
 0,16.02,16.06,15.86
 1,16.66,16.41,15.45
```

Where the values in the first row are the Mach numbers for each column, and the values in the first column are the angle of attack offset (from your cruise angle of attack) in degrees for each row.

## 5 Case 3 Results

Create a folder named `Case3` inside your participant folder with the same structure as Case 2.

Upload all of the same results files as for Case 2, plus the following additions:

### 5.1 Additional Quantities of Interest

Include the following additional columns in the `QoI.csv` file:

- `semispan`: Wing semispan in meters
- `AR`: Wing aspect ratio
- `taper`: Wing taper ratio
- `sweep`: Wing leading edge sweep in degrees
- `area`: Wing planform area in square meters


The final file structure if you are uploading results for all cases should look like this:

```
Data/
└── Participant
    ├── BenchmarkAnalyses
    │   ├── Aero
    │   │   └── RigidPolarResults.csv
    │   ├── Aeroelastic
    │   │   └── AeroelasticAnalysisResults.csv
    │   └── Struct
    │       └── StructAnalysisResults.csv
    ├── Case1
    │   ├── QoI.csv
    │   ├── SpanwiseDistributions
    │   │   ├── PullupLiftDist.csv
    │   │   ├── PullupTwistDist.csv
    │   │   ├── PushdownLiftDist.csv
    │   │   └── PushdownTwistDist.csv
    │   └── StructSizing
    │       └── StructSizing.csv
    ├── Case2
    │   ├── PostOptPolar
    │   │   └── PostOptPolar.csv
    │   ├── QoI.csv
    │   ├── SectionShapes
    │   │   ├── Section10Cruise.csv
    │   │   ├── Section10Jig.csv
    │   │   ├── Section30Cruise.csv
    │   │   ├── Section30Jig.csv
    │   │   ├── Section50Cruise.csv
    │   │   ├── Section50Jig.csv
    │   │   ├── Section70Cruise.csv
    │   │   ├── Section70Jig.csv
    │   │   ├── Section90Cruise.csv
    │   │   └── Section90Jig.csv
    │   ├── SpanwiseDistributions
    │   │   ├── CruiseLiftDist.csv
    │   │   ├── CruiseTwistDist.csv
    │   │   ├── JigTwistDist.csv
    │   │   ├── PullupLiftDist.csv
    │   │   ├── PullupTwistDist.csv
    │   │   ├── PushdownLiftDist.csv
    │   │   └── PushdownTwistDist.csv
    │   └── StructSizing
    │       └── StructSizing.csv
    └── Case3
        ├── PostOptPolar
        │   └── PostOptPolar.csv
        ├── QoI.csv
        ├── SectionShapes
        │   ├── Section10Cruise.csv
        │   ├── Section10Jig.csv
        │   ├── Section30Cruise.csv
        │   ├── Section30Jig.csv
        │   ├── Section50Cruise.csv
        │   ├── Section50Jig.csv
        │   ├── Section70Cruise.csv
        │   ├── Section70Jig.csv
        │   ├── Section90Cruise.csv
        │   └── Section90Jig.csv
        ├── SpanwiseDistributions
        │   ├── CruiseLiftDist.csv
        │   ├── CruiseTwistDist.csv
        │   ├── JigTwistDist.csv
        │   ├── PullupLiftDist.csv
        │   ├── PullupTwistDist.csv
        │   ├── PushdownLiftDist.csv
        │   └── PushdownTwistDist.csv
        └── StructSizing
            └── StructSizing.csv
```
