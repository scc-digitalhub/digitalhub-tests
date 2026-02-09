#!/usr/bin/env python
"""
Main test runner for CRUD tests.
"""

import os
import sys
from pathlib import Path

import digitalhub as dh
from registry import TEST_CLASSES

sys.path.append(str(Path(__file__).resolve().parents[1]))
from logging_utils import configure_logging

PROJECT_NAME = os.environ.get("PROJECT_NAME", "digitalhub-tests")
logger = configure_logging(__name__)


def run_test_class(test_class, class_name, project):
    """Run all test methods in a test class."""
    logger.info("Running %s", class_name)

    instance = test_class(project)
    test_methods = [m for m in dir(instance) if m.startswith("test_")]

    passed = 0
    failed = 0

    for method_name in test_methods:
        try:
            logger.info("  ▶ %s...", method_name)
            getattr(instance, method_name)()
            passed += 1
        except Exception as e:
            logger.exception("✗ FAILED: %s", e)
            failed += 1

    logger.info("  Results: %s passed, %s failed", passed, failed)
    return passed, failed


def main():
    """Run all CRUD tests."""
    logger.info("DIGITALHUB SDK - CRUD TESTS")

    dh.delete_project(PROJECT_NAME)
    p = dh.get_or_create_project(PROJECT_NAME)

    total_passed = 0
    total_failed = 0

    for test_class, class_name in TEST_CLASSES:
        passed, failed = run_test_class(test_class, class_name, p)
        total_passed += passed
        total_failed += failed

    # Final summary
    logger.info("FINAL SUMMARY")
    logger.info("Total tests: %s", total_passed + total_failed)
    logger.info("Passed: %s", total_passed)
    logger.info("Failed: %s", total_failed)

    if total_failed > 0:
        sys.exit(1)
    else:
        logger.info("✓ All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
