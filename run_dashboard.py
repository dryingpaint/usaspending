#!/usr/bin/env python3
"""
Launch script for the Federal Clean Energy Funding Dashboard.

This script provides an easy way to start the Streamlit dashboard.
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Launch the dashboard."""
    dashboard_path = Path("src/visualizer/dashboard.py")

    if not dashboard_path.exists():
        print(
            "❌ Dashboard file not found. Please ensure the project structure is correct."
        )
        return

    print("🚀 Starting Federal Clean Energy Funding Dashboard...")
    print("📊 The dashboard will open in your default web browser.")
    print("🔗 URL: http://localhost:8501")
    print("\n💡 Use Ctrl+C to stop the dashboard")

    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(dashboard_path),
                "--server.port=8501",
                "--server.address=localhost",
            ]
        )
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped.")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure Streamlit is installed: pip install streamlit")
        print(
            "2. Check that all dependencies are installed: pip install -r requirements.txt"
        )


if __name__ == "__main__":
    main()
