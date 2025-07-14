"""
==============================================================================
Baseline geometry definition
==============================================================================
@File    :   wingGeometry.py
@Date    :   2023/03/28
@Author  :   Alasdair Christison Gray
@Description : This file contains all data required to define the geometry of the OML and wingbox for the MACH tutorial wing. Any code that works with the geometry of the wing should import this file and use the data contained within.
"""

# ==============================================================================
# Standard Python modules
# ==============================================================================

# ==============================================================================
# External Python modules
# ==============================================================================
import numpy as np

# ==============================================================================
# Extension modules
# ==============================================================================

# ==============================================================================
# Direction definition
# ==============================================================================
spanIndex = 1  # index of the spanwise direction (0=x, 1=y, 2=z)
chordIndex = 0  # index of the chordwise direction (0=x, 1=y, 2=z)
verticalIndex = 2  # index of the vertical direction (0=x, 1=y, 2=z)

# ==============================================================================
# OML Definition
# ==============================================================================
semiSpan = 14.0  # semi-span of the wing in metres

sectionEta = np.array([0.0, 1.0])  # Normalised spanwise coordinates of the wing sections
sectionChord = np.array([5.0, 1.5])  # Chord length of the wing sections in metres
sectionChordwiseOffset = np.array([0.0, 7.5])  # Offset of each section in the chordwise direction in metres
sectionVerticalOffset = np.array([0.0, 0.0])  # Offset of each section in the vertical direction in metres
sectionTwist = np.array([0.0, 0.0])  # Twist of each section (around the spanwise axis) in degrees
sectionProfiles = ["rae2822.dat"] * 2  # Airfoil profile files for each section

teHeight = 0.25 * 0.0254  # thickness of the trailing edge (1/4 inch) in metres

LECoords = np.zeros((2, 3))  # Leading edge coordinates of each section
LECoords[:, spanIndex] = semiSpan * sectionEta
LECoords[:, chordIndex] = sectionChordwiseOffset
LECoords[:, verticalIndex] = sectionVerticalOffset

TECoords = np.zeros((2, 3))  # Trailing edge coordinates of each section
TECoords = np.zeros((2, 3))  # Trailing edge coordinates of each section
TECoords[:, spanIndex] = semiSpan * sectionEta
TECoords[:, chordIndex] = sectionChordwiseOffset + sectionChord * np.cos(np.deg2rad(sectionTwist))
TECoords[:, verticalIndex] = sectionVerticalOffset - sectionChord * np.sin(np.deg2rad(sectionTwist))

rootChord = sectionChord[0]
tipChord = sectionChord[1]
planformArea = semiSpan * (rootChord + tipChord) * 0.5
meanAerodynamicChord = (2.0 / 3.0) * (rootChord + tipChord - rootChord * tipChord / (rootChord + tipChord))
aspectRatio = 2 * (semiSpan**2) / planformArea
taperRatio = tipChord / rootChord

# quarter-chord sweep angle (quarter chord tip point minus quarter chord root point)
quarterChordCoords = 0.75 * LECoords + 0.25 * TECoords
quarterChordLine = quarterChordCoords[1] - quarterChordCoords[0]
quarterChordSweep = np.abs(np.rad2deg(np.arctan2(quarterChordLine[chordIndex], quarterChordLine[spanIndex])))

# --- High lift devices ---
# These fracttions are measured very roughly from the planform drawing at the start of the Boeing 717 airport planning
# document. The span/area fractions assume the flaps and slats are not present inboard of the SOB

SOB = 1.5  # Spanwise coordinate of the side-of-body junction in metres
FLAP_INBOARD_SPAN_FRAC = SOB / semiSpan
FLAP_OUTBOARD_SPAN_FRAC = 0.625
FLAP_CHORD_FRAC = 0.2
SLAT_INBOARD_SPAN_FRAC = FLAP_INBOARD_SPAN_FRAC
SLAT_OUTBOARD_SPAN_FRAC = 0.96
SLAT_CHORD_FRAC = 0.15

# Compute the fraction of the wing area that is flapped
midFlapSpanFrac = 0.5 * (FLAP_OUTBOARD_SPAN_FRAC - FLAP_INBOARD_SPAN_FRAC)
midFlapChord = rootChord * (1.0 - midFlapSpanFrac) + tipChord * midFlapSpanFrac
FLAP_AREA_FRAC = semiSpan * (FLAP_OUTBOARD_SPAN_FRAC - FLAP_INBOARD_SPAN_FRAC) * midFlapChord / planformArea

# --- Now define the tails ---
hTailRootChord = 3.25
hTailTipChord = 1.22
hTailSemiSpan = 6.5
hTailPlanformArea = hTailSemiSpan * (hTailRootChord + hTailTipChord) * 0.5
hTailMeanAerodynamicChord = hTailPlanformArea * (
    (2.0 / 3.0) * (hTailRootChord + hTailTipChord - hTailRootChord * hTailTipChord / (hTailRootChord + hTailTipChord))
)
hTailaspectRatio = 2 * (hTailSemiSpan**2) / hTailPlanformArea
hTailSweep = 30.0
hTailTaperRatio = hTailTipChord / hTailRootChord

vTailRootChord = 15.3 * 0.3048
vTailTipChord = 12.12 * 0.3048
vTailSemiSpan = 15.72 * 0.3048
vTailPlanformArea = vTailSemiSpan * (vTailRootChord + vTailTipChord) * 0.5
vTailMeanAerodynamicChord = vTailPlanformArea * (
    (2.0 / 3.0) * (vTailRootChord + vTailTipChord - vTailRootChord * vTailTipChord / (vTailRootChord + vTailTipChord))
)
vTailaspectRatio = 2 * (vTailSemiSpan**2) / vTailPlanformArea
vTailSweep = 37.0
vTailTaperRatio = vTailTipChord / vTailRootChord

# Values for textbook drag estimate
Q_TAIL = 1.03  # Interference factor for clean tail, presumably from Raymer sec 12?
TAIL_THICKNESS = 0.1  # Guess of tail t/c

# --- Nacelle ---
nacelleLength = 5.865
nacelleDiameter = 1.8
nacelleArea = np.pi * nacelleDiameter * nacelleLength
nacelle_f = nacelleLength / nacelleDiameter
NACELLE_FORM_FACTOR = 1.3 * (
    1.0 + 0.35 / (nacelle_f)
)  # Raymer sec 12.5.4 eq 12.32, Multiply by form factor of 1.3 for nacelle mounted with one diameter of fuselage, Raymer sec 12.5.5

# --- Fuselage ---
fuselageLength = 112 * 0.3048  # 112 ft in metres
fuselageWidth = 3.4  # metres
fuselageArea = fuselageLength * np.pi * fuselageWidth  # very approximate

# ==============================================================================
# Wingbox Definition
# ==============================================================================
LESparFrac = 0.15  # Normalised chordwise location of the leading-edge spar
TESparFrac = 0.65  # Normalised chordwise location of the trailing-edge spar
numRibsCentrebody = 4  # Number of ribs in the centre wingbox
numRibsOuter = 19  # Number of ribs outboard of the SOB
numRibs = numRibsCentrebody + numRibsOuter  # Total number of ribs
numSpars = 2  # Number of spars (front and rear only)

LESparCoords = np.zeros((3, 3))  # Leading edge spar coordinates of each section
TESparCoords = np.zeros((3, 3))  # Trailing edge spar coordinates of each section

# Tip is easy because we know the chord length there
LESparCoords[-1] = LECoords[-1] + LESparFrac * (TECoords[-1] - LECoords[-1])
TESparCoords[-1] = LECoords[-1] + TESparFrac * (TECoords[-1] - LECoords[-1])

# We need to shift the tip of the wingbox slightly off from the tip of the OML so that pylayout's projections work
LESparCoords[-1, spanIndex] -= 1e-3
TESparCoords[-1, spanIndex] -= 1e-3

# For the side of body, we need to interpolate the leading and trailing edge coordinates
sobLE = LECoords[0] + SOB / semiSpan * (LECoords[1] - LECoords[0])
sobTE = TECoords[0] + SOB / semiSpan * (TECoords[1] - TECoords[0])
LESparCoords[1] = sobLE + LESparFrac * (sobTE - sobLE)
TESparCoords[1] = sobLE + TESparFrac * (sobTE - sobLE)

# From the side of body to the root, there is no sweep, so we just shift the SOB coordinates in the spanwise direction,
# then correct the vertical position so that the spar points lie on the root chord line
# We again need to shift the root of the wingbox slightly off from the root of the OML so that pylayout's projections work
LESparCoords[0] = LESparCoords[1]
LESparCoords[0, spanIndex] = 1e-3

TESparCoords[0] = TESparCoords[1]
TESparCoords[0, spanIndex] = 1e-3

rootLESparFrac = (LESparCoords[0, chordIndex] - LECoords[0, chordIndex]) / (
    TECoords[0, chordIndex] - LECoords[0, chordIndex]
)
rootTESparFrac = (TESparCoords[0, chordIndex] - LECoords[0, chordIndex]) / (
    TECoords[0, chordIndex] - LECoords[0, chordIndex]
)

LESparCoords[0, verticalIndex] = LECoords[0, verticalIndex] + rootLESparFrac * (
    TECoords[0, verticalIndex] - LECoords[0, verticalIndex]
)
TESparCoords[0, verticalIndex] = LECoords[0, verticalIndex] + rootTESparFrac * (
    TECoords[0, verticalIndex] - LECoords[0, verticalIndex]
)

# ==============================================================================
# Put everything in a dictionary
# ==============================================================================

wingGeometry = {}
wingGeometry["spanIndex"] = spanIndex
wingGeometry["chordIndex"] = chordIndex
wingGeometry["verticalIndex"] = verticalIndex
wingGeometry["wing"] = {
    "semiSpan": semiSpan,
    "sectionEta": sectionEta,
    "sectionChord": sectionChord,
    "sectionChordwiseOffset": sectionChordwiseOffset,
    "sectionVerticalOffset": sectionVerticalOffset,
    "sectionTwist": sectionTwist,
    "sectionProfiles": sectionProfiles,
    "teHeight": teHeight,
    "LECoords": LECoords,
    "TECoords": TECoords,
    "planformArea": planformArea,
    "meanAerodynamicChord": meanAerodynamicChord,
    "aspectRatio": aspectRatio,
    "taperRatio": taperRatio,
    "quarterChordSweep": quarterChordSweep,
    "flapInboardSpanFrac": FLAP_INBOARD_SPAN_FRAC,
    "flapOutboardSpanFrac": FLAP_OUTBOARD_SPAN_FRAC,
    "flapChordFrac": FLAP_CHORD_FRAC,
    "slatInboardSpanFrac": SLAT_INBOARD_SPAN_FRAC,
    "slatOutboardSpanFrac": SLAT_OUTBOARD_SPAN_FRAC,
    "slatChordFrac": SLAT_CHORD_FRAC,
    "FlapAreaFrac": FLAP_AREA_FRAC,
}
wingGeometry["hTail"] = {
    "rootChord": hTailRootChord,
    "tipChord": hTailTipChord,
    "semiSpan": hTailSemiSpan,
    "planformArea": hTailPlanformArea,
    "meanAerodynamicChord": hTailMeanAerodynamicChord,
    "aspectRatio": hTailaspectRatio,
    "taperRatio": hTailTaperRatio,
    "sweep": hTailSweep,
    "QFactor": Q_TAIL,
    "toverc": TAIL_THICKNESS,
}
wingGeometry["vTail"] = {
    "rootChord": vTailRootChord,
    "tipChord": vTailTipChord,
    "semiSpan": vTailSemiSpan,
    "planformArea": vTailPlanformArea,
    "meanAerodynamicChord": vTailMeanAerodynamicChord,
    "aspectRatio": vTailaspectRatio,
    "taperRatio": vTailTaperRatio,
    "sweep": vTailSweep,
    "QFactor": Q_TAIL,
    "toverc": TAIL_THICKNESS,
}
wingGeometry["nacelle"] = {
    "length": nacelleLength,
    "diameter": nacelleDiameter,
    "area": nacelleArea,
    "formFactor": NACELLE_FORM_FACTOR,
}
wingGeometry["fuselage"] = {
    "length": fuselageLength,
    "width": fuselageWidth,
    "area": fuselageArea,
}
wingGeometry["wingbox"] = {
    "SOB": SOB,
    "LESparFrac": LESparFrac,
    "TESparFrac": TESparFrac,
    "numRibsCentrebody": numRibsCentrebody,
    "numRibsOuter": numRibsOuter,
    "numRibs": numRibs,
    "numSpars": numSpars,
    "LESparCoords": LESparCoords,
    "TESparCoords": TESparCoords,
}
