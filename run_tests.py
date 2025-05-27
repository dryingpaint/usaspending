#!/usr/bin/env python3
"""
Test runner script for the federal clean energy funding analysis project.

This script provides convenient ways to run different types of tests.
"""

import sys
import subprocess


def run_command(cmd, description):
    """Run a command and handle the output."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def main():
    """Main test runner function."""
    if len(sys.argv) < 2:
        print("Usage: python run_tests.py [test_type]")
        print("\nAvailable test types:")
        print("  all          - Run all tests")
        print("  unit         - Run only unit tests (fast)")
        print("  integration  - Run only integration tests")
        print("  data_processor - Run only data processor tests")
        print("  api_client   - Run only API client tests")
        print("  transformer  - Run only data transformer tests")
        print("  analytics    - Run only analytics engine tests")
        print("  core         - Run only core processor tests")
        print("  coverage     - Run tests with coverage report")
        print("  verbose      - Run tests with verbose output")
        sys.exit(1)

    test_type = sys.argv[1].lower()

    # Base pytest command
    base_cmd = [sys.executable, "-m", "pytest"]

    # Test type specific commands
    if test_type == "all":
        cmd = base_cmd + ["tests/"]
        description = "All tests"

    elif test_type == "unit":
        cmd = base_cmd + ["-m", "unit", "tests/"]
        description = "Unit tests only"

    elif test_type == "integration":
        cmd = base_cmd + ["-m", "integration", "tests/"]
        description = "Integration tests only"

    elif test_type == "data_processor":
        cmd = base_cmd + ["tests/test_data_processor/"]
        description = "Data processor component tests"

    elif test_type == "api_client":
        cmd = base_cmd + ["tests/test_data_processor/test_api_client.py"]
        description = "API client tests"

    elif test_type == "transformer":
        cmd = base_cmd + ["tests/test_data_processor/test_data_transformer.py"]
        description = "Data transformer tests"

    elif test_type == "analytics":
        cmd = base_cmd + ["tests/test_data_processor/test_analytics_engine.py"]
        description = "Analytics engine tests"

    elif test_type == "core":
        cmd = base_cmd + ["tests/test_data_processor/test_core_processor.py"]
        description = "Core processor tests"

    elif test_type == "coverage":
        cmd = base_cmd + [
            "--cov=src",
            "--cov-report=html",
            "--cov-report=term",
            "tests/",
        ]
        description = "All tests with coverage report"

    elif test_type == "verbose":
        cmd = base_cmd + ["-vv", "-s", "tests/"]
        description = "All tests with verbose output"

    else:
        print(f"Unknown test type: {test_type}")
        sys.exit(1)

    # Run the tests
    success = run_command(cmd, description)

    if success:
        print(f"\n✅ {description} completed successfully!")

        if test_type == "coverage":
            print("\n📊 Coverage report generated:")
            print("  - Terminal report shown above")
            print("  - HTML report: htmlcov/index.html")

    else:
        print(f"\n❌ {description} failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
