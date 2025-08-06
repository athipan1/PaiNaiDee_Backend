#!/usr/bin/env python3
"""
Test runner script for PaiNaiDee Backend API

This script runs all tests in the tests directory using pytest.
It provides a convenient way to run all tests with proper configuration.

Usage:
    python tests/run_all_tests.py
    python tests/run_all_tests.py --verbose
    python tests/run_all_tests.py --coverage
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description='Run all tests for PaiNaiDee Backend')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Run tests with verbose output')
    parser.add_argument('--coverage', '-c', action='store_true',
                       help='Run tests with coverage report')
    parser.add_argument('--specific', '-s', type=str,
                       help='Run specific test file (e.g., test_app.py)')
    
    args = parser.parse_args()
    
    # Get the project root directory (parent of tests directory)
    tests_dir = Path(__file__).parent
    project_root = tests_dir.parent
    
    # Change to project root directory
    os.chdir(project_root)
    
    # Build pytest command
    cmd = ['python', '-m', 'pytest']
    
    if args.specific:
        # Run specific test file
        test_path = tests_dir / args.specific
        if test_path.exists():
            cmd.append(str(test_path))
        else:
            print(f"Error: Test file '{args.specific}' not found in tests directory")
            return 1
    else:
        # Run all tests in tests directory
        cmd.append('tests/')
    
    # Add verbose flag if requested
    if args.verbose:
        cmd.append('-v')
    
    # Add coverage if requested
    if args.coverage:
        cmd.extend(['--cov=src', '--cov-report=term-missing'])
    
    # Add other useful pytest options
    cmd.extend([
        '--tb=short',  # Shorter traceback format
        '--strict-markers',  # Strict marker checking
        '--disable-warnings'  # Disable warnings for cleaner output
    ])
    
    print("=" * 60)
    print("🧪 Running PaiNaiDee Backend Tests")
    print("=" * 60)
    print(f"Command: {' '.join(cmd)}")
    print(f"Working directory: {project_root}")
    print("-" * 60)
    
    try:
        # Run the tests
        result = subprocess.run(cmd, check=False)
        
        print("-" * 60)
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print(f"❌ Tests failed with exit code {result.returncode}")
        print("=" * 60)
        
        return result.returncode
        
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        return 130
    except FileNotFoundError:
        print("❌ Error: pytest not found. Please install dependencies:")
        print("   pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())