#!/usr/bin/env python3
"""Test runner script for the chat bot application."""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {description} failed with exit code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run tests for the chat bot application")
    parser.add_argument(
        "--service",
        choices=["auth", "api", "admin", "chat", "graph", "services", "all"],
        default="all",
        help="Specific service to test (default: all)"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run tests with coverage report"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Run tests in verbose mode"
    )
    parser.add_argument(
        "--parallel",
        "-n",
        type=int,
        help="Number of parallel workers for pytest-xdist"
    )
    parser.add_argument(
        "--markers",
        "-m",
        help="Run tests with specific markers (e.g., 'not slow')"
    )
    parser.add_argument(
        "--failfast",
        "-x",
        action="store_true",
        help="Stop on first failure"
    )
    parser.add_argument(
        "--lf",
        action="store_true",
        help="Run only tests that failed in the last run"
    )
    parser.add_argument(
        "--tb",
        choices=["short", "long", "auto", "line", "native", "no"],
        default="short",
        help="Traceback print mode"
    )
    
    args = parser.parse_args()
    
    # Check if we're in the right directory
    if not Path("tests").exists():
        print("ERROR: tests directory not found. Please run from project root.")
        sys.exit(1)
    
    # Base pytest command
    pytest_cmd = ["python", "-m", "pytest"]
    
    # Add test path based on service
    if args.service == "all":
        pytest_cmd.append("tests/")
    else:
        test_path = f"tests/{args.service}/"
        if not Path(test_path).exists():
            print(f"ERROR: Test directory {test_path} not found.")
            sys.exit(1)
        pytest_cmd.append(test_path)
    
    # Add coverage if requested
    if args.coverage:
        pytest_cmd.extend([
            "--cov=app",
            "--cov-report=html:htmlcov",
            "--cov-report=term-missing",
            "--cov-report=xml"
        ])
    
    # Add verbose mode
    if args.verbose:
        pytest_cmd.append("-v")
    
    # Add parallel execution
    if args.parallel:
        pytest_cmd.extend(["-n", str(args.parallel)])
    
    # Add markers
    if args.markers:
        pytest_cmd.extend(["-m", args.markers])
    
    # Add fail fast
    if args.failfast:
        pytest_cmd.append("-x")
    
    # Add last failed
    if args.lf:
        pytest_cmd.append("--lf")
    
    # Add traceback mode
    pytest_cmd.extend(["--tb", args.tb])
    
    # Add other useful options
    pytest_cmd.extend([
        "--strict-markers",
        "--strict-config",
        "--color=yes"
    ])
    
    # Run the tests
    success = run_command(pytest_cmd, f"Running tests for {args.service}")
    
    if success:
        print(f"\n✅ All tests passed for {args.service}!")
        
        if args.coverage:
            print("\n📊 Coverage report generated:")
            print("  - HTML: htmlcov/index.html")
            print("  - XML: coverage.xml")
    else:
        print(f"\n❌ Some tests failed for {args.service}")
        sys.exit(1)


def run_specific_tests():
    """Run specific test categories."""
    test_categories = {
        "unit": "tests/ -m 'not integration and not e2e'",
        "integration": "tests/ -m integration",
        "e2e": "tests/ -m e2e",
        "slow": "tests/ -m slow",
        "fast": "tests/ -m 'not slow'",
        "auth": "tests/auth/",
        "api": "tests/api/",
        "admin": "tests/admin/",
        "chat": "tests/chat/",
        "graph": "tests/graph/",
        "services": "tests/services/"
    }
    
    print("Available test categories:")
    for category, path in test_categories.items():
        print(f"  {category}: {path}")


def check_test_environment():
    """Check if the test environment is properly set up."""
    print("Checking test environment...")
    
    # Check if pytest is installed
    try:
        import pytest
        print(f"✅ pytest {pytest.__version__} is installed")
    except ImportError:
        print("❌ pytest is not installed. Run: pip install pytest")
        return False
    
    # Check if required test dependencies are installed
    required_packages = [
        "pytest-asyncio",
        "pytest-cov",
        "httpx",
        "faker"
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is not installed")
    
    # Check if test files exist
    test_dirs = ["auth", "api", "admin", "chat", "graph", "services"]
    for test_dir in test_dirs:
        test_path = Path(f"tests/{test_dir}")
        if test_path.exists():
            test_files = list(test_path.glob("test_*.py"))
            print(f"✅ {test_dir} tests: {len(test_files)} files")
        else:
            print(f"❌ {test_dir} test directory not found")
    
    return True


def generate_test_report():
    """Generate a comprehensive test report."""
    commands = [
        (
            ["python", "-m", "pytest", "tests/", "--collect-only", "-q"],
            "Collecting all tests"
        ),
        (
            ["python", "-m", "pytest", "tests/", "--cov=app", "--cov-report=term", "--tb=short"],
            "Running all tests with coverage"
        )
    ]
    
    for command, description in commands:
        success = run_command(command, description)
        if not success:
            print(f"Failed to generate test report: {description}")
            return False
    
    return True


if __name__ == "__main__":
    # Add additional commands
    if len(sys.argv) > 1:
        if sys.argv[1] == "check":
            check_test_environment()
            sys.exit(0)
        elif sys.argv[1] == "categories":
            run_specific_tests()
            sys.exit(0)
        elif sys.argv[1] == "report":
            generate_test_report()
            sys.exit(0)
    
    main()