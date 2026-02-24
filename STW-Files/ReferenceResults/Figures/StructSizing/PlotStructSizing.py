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

plt.style.use(niceplots.get_style())

submissions = findSubmissionDirs()

colours = niceplots.get_colors()
coloursList = niceplots.get_colors_list()
linestyles = ["-", "-.", ":", "--"]

compNameMap = {"LSkin": "Lower Skin", "USkin": "Upper Skin", "FSpar": "Front Spar", "RSpar": "Rear Spar"}
spanwiseStations = {"Root": -0.5, "SOB": 2.5, "Tip": 21.5}


def plotThickness(ax, t, **kwargs):
    t = t.copy()
    if np.max(t) < 1.0:
        t *= 1000  # Convert to mm
    stationNumbers = np.arange(len(t))
    stepValues = np.repeat(t, 2)
    stationOffsets = np.tile([-0.5, 0.5], len(t))
    stepLocations = np.repeat(stationNumbers, 2) + stationOffsets
    (line,) = ax.plot(stepLocations, stepValues, **kwargs)
    return line


for case in range(1, 4):
    fig, axes = plt.subplots(2, 2, sharex=True, sharey="row", figsize=(12, 10))
    for ax in axes[:, 0]:
        ax.set_ylabel("Equivalent Thickness [mm]")
    for ax in axes[1, :]:
        ax.set_xticks(list(spanwiseStations.values()))
        ax.set_xticklabels(list(spanwiseStations.keys()))

    for ii, (name, subDir) in enumerate(submissions.items()):
        colour = coloursList[ii]
        resultsDir = f"{subDir}/Case{case}/StructSizing"
        try:
            fileName = os.path.join(resultsDir, "StructSizing.csv")
            thicknessData = pd.read_csv(fileName)
            if len(thicknessData["USkin thickness"]) == 0:
                print(f"\nNo thickness data in {fileName}, skipping\n")
                continue

            compNames = ["USkin", "LSkin", "FSpar", "RSpar"]
            for compName, ax in zip(compNames, axes.flatten()):
                thicknesses = thicknessData[f"{compName} thickness"].to_numpy()
                line = plotThickness(ax, thicknesses, color=colour, clip_on=False, label=name)
                ax.set_title(compNameMap[compName])
                niceplots.adjust_spines(ax)
                ax.axvline(
                    spanwiseStations["SOB"],
                    color=colours["Axis"],
                    linestyle="-",
                    alpha=0.7,
                    linewidth=1.0,
                    zorder=-10,
                    clip_on=False,
                )

            axes[0, 0].legend(labelcolor="linecolor")

        except FileNotFoundError:
            print(f"\nCould not find {fileName}, skipping\n")
            continue
    niceplots.save_figs(fig, f"ThicknessDists_Case{case}", ["png", "pdf", "svg"])
