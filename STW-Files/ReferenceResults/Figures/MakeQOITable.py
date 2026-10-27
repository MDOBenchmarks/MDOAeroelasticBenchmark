"""
==============================================================================

==============================================================================
@File    :   MakeQOITable.py
@Date    :   2025/12/02
@Author  :   Alasdair Christison Gray
@Description :
"""

# ==============================================================================
# Standard Python modules
# ==============================================================================
import os

# ==============================================================================
# External Python modules
# ==============================================================================
import pandas as pd
import tabulate

# ==============================================================================
# Extension modules
# ==============================================================================
from utils import findSubmissionDirs, QOI_MAP

submissions = findSubmissionDirs()

data = {}

for submissionName, submissionDir in submissions.items():
    for case in [2,3]:
        caseFile = os.path.join(submissionDir, f"Case{case}", "QoI.csv")
        try:
            caseData = pd.read_csv(caseFile)
            if len(caseData) == 0:
                print(f"\nNo data in {caseFile}, skipping\n")
                continue
            if submissionName not in data:
                data[submissionName] = {}
            data[submissionName][f"Case{case}"] = caseData
        except FileNotFoundError:
            print(f"\nCould not find {caseFile}, skipping\n")
            continue

tableData = []
tableData.append([r"\textbf{Quantity}"])
for case in [2,3]:
    for submissionName in data.keys():
        tableData[0].append(rf"\textbf{{{submissionName} Case {case}}}")
tableData[0].append(r"\textbf{Units}")

for QOIName in QOI_MAP:
    row = [QOI_MAP[QOIName]["name"]]
    units = QOI_MAP[QOIName]["units"]
    for case in [2,3]:
        for submissionName in data.keys():
            caseData = data[submissionName][f"Case{case}"]
            if QOIName in caseData.columns:
                value = caseData[QOIName].values[0]
                row.append(f"{value:.2f}")
            else:
                row.append(" ")
    row.append(units)
    tableData.append(row)

tabulatedData = tabulate.tabulate(tableData, headers="firstrow", tablefmt="latex_raw")
print(tabulatedData)
