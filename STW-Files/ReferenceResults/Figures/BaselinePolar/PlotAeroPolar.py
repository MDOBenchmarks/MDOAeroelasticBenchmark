"""
==============================================================================
Baseline design aero polar plotting
==============================================================================
@File    :   PlotAeroPolar.py
@Date    :   2025/11/25
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

polarFig, polarAx = plt.subplots(figsize=(10, 5))
polarAx.set_xlabel("$C_D$ [cts]")
polarAx.set_ylabel("$C_L$", rotation="horizontal", ha="right")
niceplots.adjust_spines(polarAx)

alphaFig, alphaAxes = plt.subplots(nrows=2, sharex=True, figsize=(10, 10))
alphaAxes[1].set_xlabel(r"$\alpha$ [deg]")
alphaAxes[0].set_ylabel("$C_L$", rotation="horizontal", ha="right")
alphaAxes[1].set_ylabel("$C_D$ [cts]", rotation="horizontal", ha="right")
niceplots.adjust_spines(alphaAxes[0])
niceplots.adjust_spines(alphaAxes[1])

for ii, (name, subDir) in enumerate(submissions.items()):
    resultsFile = os.path.join(subDir, "BenchmarkAnalyses", "Aero", "RigidPolarResults.csv")
    colour = coloursList[ii]

    try:
        polarData = pd.read_csv(resultsFile)
        polarData["cd"] *= 1e4  # convert to counts
    except FileNotFoundError:
        print(f"Could not find {resultsFile}, skipping")
        continue

    polarAx.plot(polarData["cd"], polarData["cl"], "-o", markersize=10, label=name, clip_on=False)
    alphaAxes[0].plot(polarData["aoa"], polarData["cl"], "-o", markersize=10, label=name, clip_on=False)
    alphaAxes[1].plot(polarData["aoa"], polarData["cd"], "-o", markersize=10, label=name, clip_on=False)

polarAx.legend(labelcolor="linecolor")
alphaAxes[0].legend(labelcolor="linecolor")

niceplots.save_figs(polarFig, "polar", ["png", "pdf", "svg"])
niceplots.save_figs(alphaFig, "alphaCurves", ["png", "pdf", "svg"])
