#!/usr/bin/env python3
"""
Setup script for creating participant folder structure and CSV templates.

Generated using GitHub Copilot
"""

import sys
import os


def create_csv_with_headers(filepath, headers, data_dir):
    """Create a CSV file with the given headers."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        f.write(",".join(headers) + "\n")
    print(f"Created: {os.path.relpath(filepath, data_dir)}")


def create_polar_template(filepath, data_dir):
    """Create a PostOptPolar.csv file with template data."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        f.write("  ,0.75,0.77,0.79\n")
        f.write("-1,14.46,14.55,14.6\n")
        f.write(" 0,16.02,16.06,15.86\n")
        f.write(" 1,16.66,16.41,15.45\n")
    print(f"Created: {os.path.relpath(filepath, data_dir)}")


def create_spanwise_distributions(
    base_path, case_name, conditions, data_dir, lift_header, twist_header, include_jig=False
):
    """Create lift and twist distribution CSV files for given conditions."""
    for condition in conditions:
        create_csv_with_headers(
            os.path.join(base_path, case_name, "SpanwiseDistributions", f"{condition}LiftDist.csv"),
            lift_header,
            data_dir,
        )
        create_csv_with_headers(
            os.path.join(base_path, case_name, "SpanwiseDistributions", f"{condition}TwistDist.csv"),
            twist_header,
            data_dir,
        )

    if include_jig:
        create_csv_with_headers(
            os.path.join(base_path, case_name, "SpanwiseDistributions", "JigTwistDist.csv"), twist_header, data_dir
        )


def create_section_shapes(base_path, case_name, span_locations, data_dir, section_header):
    """Create section shape CSV files for cruise and jig conditions."""
    for span_loc in span_locations:
        # Cruise shapes (with cp column)
        create_csv_with_headers(
            os.path.join(base_path, case_name, "SectionShapes", f"Section{span_loc}Cruise.csv"),
            section_header,
            data_dir,
        )
        # Jig shapes (without cp column)
        create_csv_with_headers(
            os.path.join(base_path, case_name, "SectionShapes", f"Section{span_loc}Jig.csv"),
            section_header[:-1],  # exclude cp
            data_dir,
        )


def setup_participant_folders(participant_name):
    """Create all necessary folders and files for a participant."""

    data_dir = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.join(data_dir, participant_name)

    # Headers
    structSizingHeader = ["USkin thickness", "LSkin thickness", "FSpar thickness", "RSpar thickness"]
    liftDistHeader = ["eta", "lift"]
    twistDistHeader = ["eta", "twist"]
    sectionShapeHeader = ["x", "z", "cp"]
    QOI = [
        "M_wingbox",
        "M_wing",
        "LGM",
        "aoa_pullup",
        "aoa_pushdown",
        "TOGM",
        "M_fuel",
        "aoa_cruise",
        "L/D",
        "tank usage",
        "semispan",
        "AR",
        "taper",
        "sweep",
        "area",
    ]

    # Constants
    SPAN_LOCATIONS = [10, 30, 50, 70, 90]
    FLIGHT_CONDITIONS = ["Pullup", "Pushdown", "Cruise"]

    if os.path.exists(base_path):
        response = input(f"Folder '{participant_name}' already exists. Continue anyway? (y/n): ")
        if response.lower() != "y":
            print("Aborted.")
            return

    print(f"\nCreating folder structure for participant: {participant_name}\n")

    # ===== BenchmarkAnalyses =====
    print("Setting up BenchmarkAnalyses...")

    # Aero
    create_csv_with_headers(
        os.path.join(base_path, "BenchmarkAnalyses", "Aero", "RigidPolarResults.csv"), ["aoa", "cl", "cd"], data_dir
    )

    # Struct
    create_csv_with_headers(
        os.path.join(base_path, "BenchmarkAnalyses", "Struct", "StructAnalysisResults.csv"),
        ["tip disp", "tip twist", "comp", "mat fos", "buckling fos"],
        data_dir,
    )

    # Aeroelastic (note: using "Aeroelastic" as per final file tree in instructions)
    create_csv_with_headers(
        os.path.join(base_path, "BenchmarkAnalyses", "Aeroelastic", "AeroelasticAnalysisResults.csv"),
        ["cl", "cd", "tip disp", "tip twist", "comp", "mat fos", "buckling fos"],
        data_dir,
    )

    # ===== Case 1 =====
    print("\nSetting up Case1...")

    # QoI
    create_csv_with_headers(os.path.join(base_path, "Case1", "QoI.csv"), QOI[:5], data_dir)

    # SpanwiseDistributions
    create_spanwise_distributions(
        base_path, "Case1", FLIGHT_CONDITIONS[:2], data_dir, liftDistHeader, twistDistHeader, include_jig=False
    )

    # StructSizing
    create_csv_with_headers(
        os.path.join(base_path, "Case1", "StructSizing", "StructSizing.csv"), structSizingHeader, data_dir
    )

    # ===== Case 2 =====
    print("\nSetting up Case2...")

    # QoI
    create_csv_with_headers(os.path.join(base_path, "Case2", "QoI.csv"), QOI[:10], data_dir)

    # SpanwiseDistributions
    create_spanwise_distributions(
        base_path, "Case2", FLIGHT_CONDITIONS, data_dir, liftDistHeader, twistDistHeader, include_jig=True
    )

    # StructSizing
    create_csv_with_headers(
        os.path.join(base_path, "Case2", "StructSizing", "StructSizing.csv"), structSizingHeader, data_dir
    )

    # SectionShapes
    create_section_shapes(base_path, "Case2", SPAN_LOCATIONS, data_dir, sectionShapeHeader)

    # PostOptPolar
    create_polar_template(os.path.join(base_path, "Case2", "PostOptPolar", "PostOptPolar.csv"), data_dir)

    # ===== Case 3 =====
    print("\nSetting up Case3...")

    # QoI (includes additional planform parameters)
    create_csv_with_headers(os.path.join(base_path, "Case3", "QoI.csv"), QOI, data_dir)

    # SpanwiseDistributions
    create_spanwise_distributions(
        base_path, "Case3", FLIGHT_CONDITIONS, data_dir, liftDistHeader, twistDistHeader, include_jig=True
    )

    # StructSizing
    create_csv_with_headers(
        os.path.join(base_path, "Case3", "StructSizing", "StructSizing.csv"), structSizingHeader, data_dir
    )

    # SectionShapes
    create_section_shapes(base_path, "Case3", SPAN_LOCATIONS, data_dir, sectionShapeHeader)

    # PostOptPolar
    create_polar_template(os.path.join(base_path, "Case3", "PostOptPolar", "PostOptPolar.csv"), data_dir)

    print(f"\n✓ Successfully created folder structure for '{participant_name}'")
    print("\nAll CSV files have been created with appropriate headers.")
    print("You can now populate them with your results data.\n")


def main():
    if len(sys.argv) != 2:
        print("Error: Missing participant name argument")
        print("\nUsage:")
        print("    python setup_participant.py <participant_name>")
        print("\nExample:")
        print("    python setup_participant.py NASA")
        sys.exit(1)

    participant_name = sys.argv[1]

    # Validate participant name
    if not participant_name.strip():
        print("Error: Participant name cannot be empty")
        sys.exit(1)

    # Check for problematic characters
    if any(char in participant_name for char in ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]):
        print("Error: Participant name contains invalid characters")
        sys.exit(1)

    setup_participant_folders(participant_name)


if __name__ == "__main__":
    main()
