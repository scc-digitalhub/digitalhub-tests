#!/bin/bash
set -e

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 PROJECT_NAME_TEST" >&2
    exit 1
fi

cd "$(dirname "$0")"
export PROJECT_NAME_TEST="$1"

pids=()
for test_folder in s1-etl s2-dbt s3-scikit-learn s4-mlflow s5-container; do
    python "$test_folder/main.py" &
    pids+=("$!")
done

status=0
for pid in "${pids[@]}"; do
    wait "$pid" || status=1
done

exit "$status"
