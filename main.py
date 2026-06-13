"""
IoT Smart Agriculture Monitoring System
File: main.py

Main entry point — runs simulation then opens dashboard.

Usage:
    python main.py                    # Normal scenario, 20 readings
    python main.py --scenario dry     # Dry soil scenario
    python main.py --scenario hot     # High temperature scenario
    python main.py --scenario low_water
    python main.py --no-dashboard     # Skip dashboard launch
"""

import argparse
import subprocess
import sys
import os

# Make sure imports work from root
sys.path.insert(0, os.path.dirname(__file__))

from python_simulation.sensor_simulator import run_simulation


def main():
    parser = argparse.ArgumentParser(
        description="IoT Smart Agriculture Monitoring System"
    )
    parser.add_argument(
        "--scenario",
        choices=["normal", "dry", "hot", "low_water", "mixed"],
        default="normal",
        help="Simulation scenario"
    )
    parser.add_argument(
        "--readings", type=int, default=20,
        help="Number of sensor readings to simulate"
    )
    parser.add_argument(
        "--interval", type=float, default=0.5,
        help="Seconds between readings"
    )
    parser.add_argument(
        "--no-dashboard", action="store_true",
        help="Skip Streamlit dashboard launch"
    )

    args = parser.parse_args()

    print("\n" + "="*55)
    print("  IoT Smart Agriculture Monitoring System")
    print("="*55)

    # Step 1: Run simulation
    print(f"\n[STEP 1] Running sensor simulation ({args.scenario} scenario)...")
    run_simulation(
        total_readings=args.readings,
        interval_sec=args.interval,
        scenario=args.scenario
    )

    # Step 2: Launch dashboard
    if not args.no_dashboard:
        print("\n[STEP 2] Launching Streamlit dashboard...")
        print("  → Open browser at: http://localhost:8501")
        print("  → Press Ctrl+C to stop\n")
        try:
            subprocess.run([
                sys.executable, "-m", "streamlit", "run",
                os.path.join(os.path.dirname(__file__), "dashboard", "app.py")
            ])
        except KeyboardInterrupt:
            print("\n[INFO] Dashboard closed by user.")
    else:
        print("\n[INFO] Dashboard skipped. Run manually:")
        print("  streamlit run dashboard/app.py")


if __name__ == "__main__":
    main()
