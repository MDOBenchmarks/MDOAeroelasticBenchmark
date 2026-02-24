import os

thisDir = os.path.dirname(os.path.abspath(__file__))
dataDir = os.path.join(thisDir, "..", "Data")


def findSubmissionDirs():
    submissionDirs = {}
    # Find all the subdirectories in the data directory
    for entry in os.listdir(dataDir):
        fullPath = os.path.join(dataDir, entry)
        if os.path.isdir(fullPath):
            submissionDirs[entry] = fullPath
    return submissionDirs

QOI_MAP = {"M_wingbox": {"name": r"$M_\text{wingbox}$", "units": r"\si{\kilo\gram}"},
           "M_wing": {"name": r"$M_\text{wing}$", "units": r"\si{\kilo\gram}"},
           "LGM": {"name": r"$LGM$", "units": r"\si{\kilo\gram}"},
           "TOGM": {"name": r"$TOGM$", "units": r"\si{\kilo\gram}"},
           "M_fuel": {"name": r"$M_\text{fuel}$", "units": r"\si{\kilo\gram}"},
           "aoa_cruise": {"name": r"$\alpha_\text{cruise}$", "units": r"\si{\degree}"},
           "aoa_pullup": {"name": r"$\alpha_\text{2.5g}$", "units": r"\si{\degree}"},
           "aoa_pushdown": {"name": r"$\alpha_\text{-1g}$", "units": r"\si{\degree}"},
           "L/D": {"name": r"Cruise $L/D$", "units": r""},
           "tank usage": {"name": r"Fuel tank usage", "units": r"\%"},
           "semispan": {"name": r"Semispan", "units": r"\si{\meter}"},
           "AR": {"name": r"Aspect ratio", "units": r""},
           "taper": {"name": r"Taper ratio", "units": r""},
           "sweep": {"name": r"Leading edge sweep", "units": r"\si{\degree}"},
           "area": {"name": r"Planform area", "units": r"\si{\meter\squared}"},
}
