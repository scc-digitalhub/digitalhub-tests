#!/usr/bin/env python
"""
Main test runner for CRUD tests.
"""

import sys
import traceback

import digitalhub as dh
from registry import TEST_CLASSES

PROJECT_NAME = "digitalhub-tests"


def run_test_class(test_class, class_name, project):
    """Run all test methods in a test class."""
    print(f"\n{'=' * 70}")
    print(f"Running {class_name}")
    print("=" * 70)

    instance = test_class(project)
    test_methods = [m for m in dir(instance) if m.startswith("test_")]

    passed = 0
    failed = 0

    for method_name in test_methods:
        try:
            print(f"\n  ▶ {method_name}...", end=" ")
            getattr(instance, method_name)()
            print("✓ PASSED")
            passed += 1
        except Exception as e:
            raise e
            print("✗ FAILED")
            print(f"    Error: {e}")
            traceback.print_exc(limit=3)
            failed += 1

    print(f"\n  Results: {passed} passed, {failed} failed")
    return passed, failed


def main():
    """Run all CRUD tests."""
    print("\n" + "=" * 70)
    print("DIGITALHUB SDK - CRUD TESTS")
    print("=" * 70)

    dh.delete_project(PROJECT_NAME)
    p = dh.get_or_create_project(PROJECT_NAME)

    total_passed = 0
    total_failed = 0

    for test_class, class_name in TEST_CLASSES:
        passed, failed = run_test_class(test_class, class_name, p)
        total_passed += passed
        total_failed += failed

    # Final summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print(f"Total tests: {total_passed + total_failed}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    print("=" * 70)

    if total_failed > 0:
        sys.exit(1)
    else:
        print("\n✓ All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
