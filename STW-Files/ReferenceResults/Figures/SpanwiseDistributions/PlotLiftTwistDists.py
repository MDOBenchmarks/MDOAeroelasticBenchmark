"""
==============================================================================
Lift/Twist distribution plotting
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

import matplotlib.pyplot as plt
import niceplots
import numpy as np

# ==============================================================================
# External Python modules
# ==============================================================================
import pandas as pd
from matplotlib.lines import Line2D

# ==============================================================================
# Extension modules
# ==============================================================================
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils import findSubmissionDirs


def cleanupDist(x, y):
    """Sometimes, at the wingtip, the lift/twist distributions can have weird spikes. This function removes those spikes
    by checking for large changes in gradient.
    """
    x = x.copy()
    y = y.copy()
    slope = (y[1:] - y[:-1]) / (x[1:] - x[:-1])
    slope2 = (slope[1:] - slope[:-1]) / (x[2:] - x[:-2])
    if np.abs(slope2[-1]) > 5.0 * np.max(np.abs(slope2[:-1])):
        # This is a bad point, skip it
        x = x[:-1]
        y = y[:-1]
    return x, y


submissions = findSubmissionDirs()

plt.style.use(niceplots.get_style())
colours = niceplots.get_colors()
coloursList = niceplots.get_colors_list()

ARROW_PROPS = {
    "arrowstyle": "-",
    "color": colours["Axis"],
    "alpha": 0.7,
    "patchB": None,
    "shrinkB": 0,
    "connectionstyle": "arc3,rad=0.3",
}

linestyles = {"Jig": "-.", "Cruise": "-", "Pullup": ":", "Pushdown": "--"}
flightPointNames = linestyles.keys()

ellipticalX = np.sin(np.linspace(0, np.pi / 2, 200))
ellipticalY = np.sqrt(1 - ellipticalX**2)
ellipticalY /= np.trapz(ellipticalY, ellipticalX)  # Normalize area to 1


for case in range(1, 4):

    flightPoints = ["Pullup", "Pushdown"]
    if case > 1:
        flightPoints.append("Cruise")
    numFlightPoints = len(flightPoints)

    fig, axes = plt.subplots(nrows=2, ncols=numFlightPoints, sharex=True, sharey="row", figsize=(16, 8))
    twistAxes = axes[0, :]
    liftAxes = axes[1, :]
    jigTwistLabelled = False

    for ii, ax in enumerate(twistAxes):
        if ii == 0:
            ax.set_ylabel("Twist [deg]", rotation="horizontal", ha="right")
        niceplots.adjust_spines(ax, ["left"])
        ax.set_title(f"{flightPoints[ii]}")
        if case == 1:
            ax.axhline(0, color=colours["Axis"], linestyle="--", zorder=0, clip_on=False, label="Jig")

    for ii, ax in enumerate(liftAxes):
        if ii == 0:
            ax.set_ylabel("Normalized\nLift", rotation="horizontal", ha="right")
        ax.set_xlabel("Normalized Span")
        niceplots.adjust_spines(ax)

        # Plot elliptical and zero lift lines for reference
        ax.plot(
            ellipticalX, ellipticalY, "-", lw=1, color=colours["Axis"], label="Elliptical", clip_on=False, alpha=0.7
        )
        if ii == 0:
            ax.annotate(
                "Elliptical",
                xy=(0.634, 0.987),
                xycoords="data",
                xytext=(0.75, 1.05),
                va="center",
                arrowprops=ARROW_PROPS,
            )
        ax.axhline(0, color=colours["Axis"], linestyle="--", alpha=0.7, zorder=0, clip_on=False)

    # --- Legend ---
    # We need three different types of legend entry:
    # 1. Participants (Solid lines with different colours)
    legendEntries = {}

    minYCenterOfLift = np.inf
    minXCenterOfLift = np.inf

    for ii, (name, subDir) in enumerate(submissions.items()):
        resultsDir = f"{subDir}/Case{case}/SpanwiseDistributions"
        colour = coloursList[ii]

        for jj, flightPoint in enumerate(flightPoints):
            try:
                fileName = f"{resultsDir}/{flightPoint}TwistDist.csv"
                twistData = pd.read_csv(fileName)
                if len(twistData) == 0:
                    print(f"\nNo data in {fileName}, skipping\n")
                    continue

                # Plot twist distribution
                eta, twist = cleanupDist(twistData["eta"].to_numpy(), twistData["twist"].to_numpy())
                (twistLine,) = twistAxes[jj].plot(
                    eta,
                    twist,
                    c=colour,
                    clip_on=False,
                )
                if name not in legendEntries:
                    fakeLine = Line2D([0], [0])
                    fakeLine.update_from(twistLine)
                    fakeLine.set_linestyle("-")
                    legendEntries[name] = fakeLine

            except FileNotFoundError:
                print(f"\nCould not find {fileName}, skipping\n")
                continue

            # Plot jig twist if not case 1
            if case != 1:
                try:
                    fileName = f"{resultsDir}/JigTwistDist.csv"
                    jigTwistData = pd.read_csv(fileName)
                    if len(jigTwistData) == 0:
                        print(f"\nNo data in {fileName}, skipping\n")
                        continue

                    # Plot jig twist distribution
                    eta, jigTwist = cleanupDist(jigTwistData["eta"].to_numpy(), jigTwistData["twist"].to_numpy())
                    twistAxes[jj].plot(
                        eta,
                        jigTwist,
                        c=colour,
                        linestyle="--",
                        clip_on=False,
                        zorder=0,
                        label="Jig" if not jigTwistLabelled else None,
                    )
                    jigTwistLabelled = True

                except FileNotFoundError:
                    print(f"\nCould not find {fileName}, skipping\n")
                    continue

            try:
                fileName = f"{resultsDir}/{flightPoint}LiftDist.csv"
                liftData = pd.read_csv(fileName)
                if len(liftData) == 0:
                    print(f"\nNo data in {fileName}, skipping\n")
                    continue

                # Plot lift distribution
                eta = liftData["eta"].to_numpy()
                lift = liftData["lift"].to_numpy()
                # lift /= np.trapz(lift, eta)  # Normalize area under lift curve to 1
                eta, lift = cleanupDist(eta, lift)
                liftAxes[jj].plot(
                    eta,
                    lift,
                    c=colour,
                    clip_on=False,
                )

                # Compute the spanwise centre of lift and plot a marker there
                xCentroid = np.trapz(eta * lift, eta) / np.trapz(lift, eta)
                yCentroid = np.interp(xCentroid, eta, lift)
                if yCentroid < minYCenterOfLift:
                    minYCenterOfLift = yCentroid
                    minXCenterOfLift = xCentroid

                (line,) = liftAxes[jj].plot(
                    xCentroid,
                    yCentroid,
                    marker="o",
                    markersize=12,
                    color=colour,
                    clip_on=False,
                )

            except FileNotFoundError:
                print(f"\nCould not find {fileName}, skipping\n")
                continue

    # Annotate the centre of lift
    liftAxes[0].annotate(
        "Center of Lift",
        xy=(minXCenterOfLift, minYCenterOfLift),
        xycoords="data",
        xytext=(minXCenterOfLift - 0.05, minYCenterOfLift - 0.1),
        ha="right",
        va="top",
        arrowprops=ARROW_PROPS,
    )
    # Since there are a lot of legen entries, we will split them across the two subplots
    twistPlotLegendEntires = {}
    liftPlotLegendEntries = {}

    for name, line in legendEntries.items():
        if name in flightPointNames:
            twistPlotLegendEntires[name] = line
        else:
            liftPlotLegendEntries[name] = line

    twistAxes[0].legend(legendEntries.values(), legendEntries.keys(), labelcolor="linecolor")

    niceplots.label_line_ends(twistAxes[0], colors=colours["Axis"])
    niceplots.save_figs(fig, f"LiftTwistDists_Case{case}", ["png", "pdf", "svg"])
