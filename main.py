"""
main.py
-------
Entry point for Poll Results Visualizer.
Run this file to execute the full pipeline end-to-end.

  python main.py

Pipeline:
  1. Generate synthetic poll data  → data/poll_data.csv
  2. Clean and preprocess          → data/poll_data_clean.csv
  3. Run analysis                  → printed report
  4. Generate all visualizations   → outputs/*.png
"""

import subprocess
import sys
import os

STEPS = [
    ("Generating synthetic dataset",  "src/generate_data.py"),
    ("Cleaning data",                  "src/clean_data.py"),
    ("Running analysis",               "src/analyze.py"),
    ("Generating visualizations",      "src/visualize.py"),
]

def run(label, script):
    print(f"\n{'─'*60}")
    print(f"  ▶  {label}")
    print(f"{'─'*60}")
    result = subprocess.run(
        [sys.executable, script],
        capture_output=False,
        text=True
    )
    if result.returncode != 0:
        print(f"\n❌  Error in {script}. Stopping.")
        sys.exit(1)

def main():
    print("\n" + "═"*60)
    print("   POLL RESULTS VISUALIZER — Full Pipeline")
    print("═"*60)

    for label, script in STEPS:
        run(label, script)

    print("\n" + "═"*60)
    print("   ✅  Pipeline complete!")
    print(f"   📊  Charts saved in: {os.path.abspath('outputs')}")
    print(f"   📁  Data saved in  : {os.path.abspath('data')}")
    print("═"*60 + "\n")

if __name__ == "__main__":
    main()
