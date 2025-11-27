#!/bin/bash
# Execute main.py in the specified test folder
# Usage: ./execute.sh <folder_name> [additional args...]
# Example: ./execute.sh s0-crud --verbose --config=test.yaml
# If no folder is specified, all tests will be executed

set -e

if [ -z "$1" ]; then
    echo "No test folder specified - executing all tests..."
    for TEST_FOLDER in $(ls -d s*/ | tr -d '/'); do
        MAIN_FILE="/app/${TEST_FOLDER}/main.py"
        if [ -f "$MAIN_FILE" ]; then
            echo "========================================"
            echo "Executing tests in ${TEST_FOLDER}..."
            echo "========================================"
            cd "/app/${TEST_FOLDER}"
            python main.py || echo "Warning: ${TEST_FOLDER} failed"
            cd /app
        fi
    done
    exit 0
fi

TEST_FOLDER="$1"
shift  # Remove first argument, keep the rest
MAIN_FILE="/app/${TEST_FOLDER}/main.py"

if [ ! -f "$MAIN_FILE" ]; then
    echo "Error: ${MAIN_FILE} not found"
    exit 1
fi

echo "Executing tests in ${TEST_FOLDER}..."
cd "/app/${TEST_FOLDER}"
python main.py "$@"
