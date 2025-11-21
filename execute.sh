#!/bin/bash
# Execute main.py in the specified test folder
# Usage: ./execute.sh <folder_name> [additional args...]
# Example: ./execute.sh s0-crud --verbose --config=test.yaml

set -e

if [ -z "$1" ]; then
    echo "Error: No test folder specified"
    echo "Usage: $0 <folder_name> [additional args...]"
    echo "Available folders: s0-crud, s1-etl, s2-dbt, s3-scikit-learn, s4-mlflow, s5-custom-ml-model"
    exit 1
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
