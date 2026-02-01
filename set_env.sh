#!/bin/bash
# Set environment variables for api-test.py
# Usage: source set_env.sh
# Then run the test
# python3 api-test.py --env test

_is_sourced() {
    # Check if the script is being sourced
    [[ ${BASH_SOURCE[0]} != ${0} ]]
}

if ! _is_sourced; then
    echo "❌ Error: This script must be sourced. Use 'source set_env.sh' or '. set_env.sh'"
    exit 1
fi

#SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
SCRIPT_DIR="$(dirname "$(realpath -- "${BASH_SOURCE[0]}")")"
SECRETS_FILE="$SCRIPT_DIR/.secrets"

if [[ ! -f $SECRETS_FILE ]]; then
    echo "❌ Error: .secrets file not found at $SECRETS_FILE"
    echo "Create it with API_KEY, PROD_API_URL, and TEST_API_URL"
    return 1
fi

# Source secrets and export
set -a
source "$SECRETS_FILE"
set +a

echo "Environment variables set:"
echo "  API_KEY: [hidden]"
echo "  PROD_API_URL: $PROD_API_URL"
echo "  TEST_API_URL: $TEST_API_URL"
