"""Master pipeline for Bluestock mutual fund analysis."""

import subprocess
import sys


def run_command(command):
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {command}")


def main():
    steps = [
        "python data/processed/data_cleaning.py",
        "python data/processed/data_ingestion.py",
        "python compute_metrics.py",
        "python generate_advanced_analytics_outputs.py",
        "python validate_returns.py",
        "python generate_eda.py",
        "python build_final_report.py",
        "python build_presentation.py",
    ]

    for step in steps:
        run_command(step)

    print("\nPipeline completed successfully.")
    print("Artifacts generated: Final_Report.pdf, Bluestock_MF_Presentation.pptx, dashboard/dashboard.html")


if __name__ == "__main__":
    main()
