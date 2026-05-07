"""
==============================================================================
Thickness distribution plotting
==============================================================================
@File    :   PlotLiftTwistDists.py
@Date    :   2025/11/18
@Author  :   Alasdair Christison Gray
@Description :
"""

# ==============================================================================
# Standard Python modules
# ==============================================================================
import os
import sys

# ==============================================================================
# External Python modules
# ==============================================================================
import pandas as pd
import matplotlib.pyplot as plt
import niceplots
import numpy as np

# ==============================================================================
# Extension modules
# ==============================================================================
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils import findSubmissionDirs


def cleanAirfoilCoords(x, z):
    coords = np.zeros((len(x), 2))
    coords[:, 0] = x
    coords[:, 1] = z
    # Hacky method, assume the point with the highest x coord is the leading edge and just shift that to (0,0)
    leadingEdgeIdx = np.argmin(coords[:, 0])
    coords -= coords[leadingEdgeIdx, :]
    return coords[:, 0], coords[:, 1]


plt.style.use(niceplots.get_style())

submissions = findSubmissionDirs()

colours = niceplots.get_colors()
coloursList = niceplots.get_colors_list()

stationNumbers = [10, 30, 50, 70, 90]
numRows = len(stationNumbers)

# Figure dimensions
sectionAxWidth = 10.0
cpAxWidth = sectionAxWidth * 0.3 / 0.7
axHeight = 2.0
v_space = 0.1  # vertical spacing between subplots
figHeight = axHeight * numRows + v_space * axHeight * (numRows - 1) + 2.0

# Load baseline RAE 2822 data for comparison
RAECoords = np.loadtxt(os.path.join(os.path.dirname(__file__), "rae2822.csv"), delimiter=",")

lineProps = {
    "linewidth": 2,
    "alpha": 0.8,
    "clip_on": False,
}

for case in [2, 3]:
    # ==============================================================================
    # Plot jig shape sections
    # ==============================================================================
    jigFig, jigAxes = plt.subplots(numRows, 1, sharex=True, figsize=(sectionAxWidth, figHeight))

    for ii, stationNumber in enumerate(stationNumbers):
        ax = jigAxes[ii]
        ax.set_title(f"$\eta$ = {stationNumber}%")
        ax.set_aspect("equal")
        ax.set_ylabel("Z/C")
        niceplots.adjust_spines(ax)

        # Plot RAE 2822 for comparison with the jig shape
        ax.plot(
            RAECoords[:, 0],
            RAECoords[:, 1],
            color=colours["Axis"],
            linestyle="--",
            label="Baseline",
            zorder=-100000,
            **lineProps,
        )

    for ii, (name, subDir) in enumerate(submissions.items()):
        resultsDir = f"{subDir}/Case{case}/SectionShapes"

        for jj, stationNumber in enumerate(stationNumbers):
            ax = jigAxes[jj]
            try:
                fileName = f"{resultsDir}/Section{stationNumber}Jig.csv"
                sectionData = pd.read_csv(fileName)
                if len(sectionData) == 0:
                    print(f"\nNo data in {fileName}, skipping\n")
                    continue
                x = sectionData["x"].to_numpy()
                z = sectionData["z"].to_numpy()
                x, z = cleanAirfoilCoords(x, z)
                ax.plot(x, z, color=coloursList[ii], label=name, **lineProps, zorder=10-ii)
            except FileNotFoundError:
                print(f"\nCould not find {fileName}, skipping\n")
                continue

        # ==============================================================================
        # Plot cruise section shapes and pressure distributions
        # ==============================================================================
        cruiseFig, cruiseAxes = plt.subplots(
            numRows,
            2,
            sharex=True,
            figsize=(sectionAxWidth + cpAxWidth, figHeight),
            gridspec_kw={"width_ratios": [sectionAxWidth, cpAxWidth]},
        )
        for ii, stationNumber in enumerate(stationNumbers):
            sectionAx = cruiseAxes[ii, 0]
            cpAx = cruiseAxes[ii, 1]
            sectionAx.set_title(f"$\eta$ = {stationNumber}%")
            sectionAx.set_aspect("equal")
            sectionAx.set_ylabel("Z/C")

            cpAx.set_ylabel("$C_P$")
            cpAx.invert_yaxis()

            niceplots.adjust_spines(sectionAx)
            niceplots.adjust_spines(cpAx)

        for ii, (name, subDir) in enumerate(submissions.items()):
            resultsDir = f"{subDir}/Case{case}/SectionShapes"

            for jj, stationNumber in enumerate(stationNumbers):
                sectionAx = cruiseAxes[jj, 0]
                cpAx = cruiseAxes[jj, 1]
                try:
                    fileName = f"{resultsDir}/Section{stationNumber}Cruise.csv"
                    sectionData = pd.read_csv(fileName)
                    if len(sectionData) == 0:
                        print(f"\nNo data in {fileName}, skipping\n")
                        continue
                    x = sectionData["x"].to_numpy()
                    z = sectionData["z"].to_numpy()
                    x, z = cleanAirfoilCoords(x, z)
                    sectionAx.plot(x, z, color=coloursList[ii], label=name, **lineProps, zorder=10-ii)
                    cpAx.plot(sectionData["x"], sectionData["cp"], color=coloursList[ii], label=name, **lineProps, zorder=10-ii)
                except FileNotFoundError:
                    print(f"\nCould not find {fileName}, skipping\n")
                    continue

    jigAxes[0].legend(loc="lower center", bbox_to_anchor=(0.5, 1.10), labelcolor="linecolor", ncol=len(submissions))
    niceplots.save_figs(jigFig, f"JigSectionShapes_Case{case}", ["png", "pdf", "svg"])

    cruiseAxes[0, 0].legend(
        loc="lower center", bbox_to_anchor=(0.5, 1.10), labelcolor="linecolor", ncol=len(submissions)
    )
    niceplots.save_figs(cruiseFig, f"CruiseSectionShapes_Case{case}", ["png", "pdf", "svg"])
