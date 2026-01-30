# Python & Bash Scripts (API Test for PromptGPT)

Tests the backend API endpoints for success and error scenarios.

## Setup

### Create .secrets File Locally
```
# With the following format. Do not commit.
API_KEY=...
PROD_API_URL=https://...
TEST_API_URL=https://...
```
### Source the script for the key & URL

```bash
source set_env.sh
```

## Usage

```bash
python3 api-test.py --env test          # Run all tests on test
python3 api-test.py --env prod          # Run all tests on prod
python3 api-test.py --env test -v       # Verbose output
python3 api-test.py --env test -t invalid-json  # Run specific test
```
run_tests.sh is a convenience script that runs set_env.sh before api-test.py.


## Tests

| Test | Expected |
|------|----------|
| Valid request | 200 |
| Missing body / Invalid JSON / Missing threadId / Empty messages | 400 |
| Missing / Invalid API key | 403 |
| CORS preflight | 200 with headers |
