#!/usr/bin/env python3
"""
Script to run DirectIA test suite.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py --unit       # Run only unit tests
    python run_tests.py --integration # Run only integration tests
    python run_tests.py --cov        # Run with coverage report
    python run_tests.py --verbose    # Run with verbose output
"""
import sys
import subprocess
import argparse


def run_tests(args):
    """Run tests with pytest."""
    cmd = ["pytest"]

    # Test selection
    if args.unit:
        cmd.append("tests/unit/")
    elif args.integration:
        cmd.append("tests/integration/")
    else:
        cmd.append("tests/")

    # Verbosity
    if args.verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")

    # Coverage
    if args.cov:
        cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])

    # Additional options
    if args.failed:
        cmd.append("--lf")  # Run last failed tests

    if args.exitfirst:
        cmd.append("-x")  # Exit on first failure

    if args.markers:
        cmd.extend(["-m", args.markers])

    # Color output
    cmd.append("--color=yes")

    # Run pytest
    print(f"Running: {' '.join(cmd)}")
    print("-" * 70)

    result = subprocess.run(cmd)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Run DirectIA test suite")

    # Test selection
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")

    # Output options
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--cov", action="store_true", help="Generate coverage report")

    # Execution options
    parser.add_argument("--failed", action="store_true", help="Run only last failed tests")
    parser.add_argument("-x", "--exitfirst", action="store_true", help="Exit on first failure")
    parser.add_argument("-m", "--markers", help="Run tests matching marker expression")

    args = parser.parse_args()

    exit_code = run_tests(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
