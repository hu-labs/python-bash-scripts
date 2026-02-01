#!/bin/bash
# Wrapper script to set environment variables and run api-test.py
# Usage: ./run_tests.sh [args...]
# Examples:
#   ./run_tests.sh --env test
#   ./run_tests.sh --env prod --verbose
#   ./run_tests.sh --env test --test success

#SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
SCRIPT_DIR="$(dirname "$(realpath -- "${BASH_SOURCE[0]}")")"

# Source environment variables
source "$SCRIPT_DIR/set_env.sh"

# Run the Python script with all passed arguments
python3 "$SCRIPT_DIR/api-test.py" "$@"
