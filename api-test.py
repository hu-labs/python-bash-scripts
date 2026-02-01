#!/usr/bin/env python3
"""
API Endpoint Test Script

Tests the backend API for various success and failure scenarios.
Supports both prod and test environments.

Usage:
    python api-test.py --env test
    python api-test.py --env prod
    python api-test.py --env test --verbose

Environment Variables:
    API_KEY: API key for authentication (required)
    PROD_API_URL: Production API endpoint URL (required for --env prod)
    TEST_API_URL: Test API endpoint URL (required for --env test)
"""

import argparse
import json
import os
import sys
import requests


def get_api_key() -> str:
    """Retrieve API key from environment variable."""
    api_key = os.environ.get("API_KEY")
    if not api_key:
        raise EnvironmentError(
            "API_KEY environment variable is not set.\n"
            "Set it with: export API_KEY=your_api_key"
        )
    return api_key


def get_api_url(env: str) -> str:
    """Retrieve API URL from environment variable based on environment."""
    if env == "prod":
        url = os.environ.get("PROD_API_URL")
        if not url:
            raise EnvironmentError(
                "PROD_API_URL environment variable is not set.\n"
                "Set it with: export PROD_API_URL=your_prod_url"
            )
    else:
        url = os.environ.get("TEST_API_URL")
        if not url:
            raise EnvironmentError(
                "TEST_API_URL environment variable is not set.\n"
                "Set it with: export TEST_API_URL=your_test_url"
            )
    return url


def make_request(
    url: str,
    api_key: str,
    payload: dict,
    headers_override: dict | None = None,
    verbose: bool = False,
) -> requests.Response:
    """Make a POST request to the API endpoint."""
    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": api_key,
    }
    if headers_override:
        headers.update(headers_override)

    if verbose:
        print(f"  URL: {url}")
        print(f"  Headers: {json.dumps(headers, indent=2)}")
        print(f"  Payload: {json.dumps(payload, indent=2)}")

    response = requests.post(url, headers=headers, json=payload, timeout=30)
    return response


def print_result(test_name: str, passed: bool, details: str = ""):
    """Print test result with consistent formatting."""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")
    if details:
        print(f"       {details}")


def test_success_request(url: str, api_key: str, verbose: bool = False) -> bool:
    """Test a valid request that should succeed."""
    print("\n--- Test: Valid Request (Success) ---")
    payload = {
        "threadId": "test-thread-001",
        "messages": [{"role": "user", "content": "Say 'Hello test' and nothing else."}],
    }

    try:
        response = make_request(url, api_key, payload, verbose=verbose)

        if verbose:
            print(f"  Status Code: {response.status_code}")
            print(f"  Response: {response.text[:500]}...")

        if response.status_code == 200:
            data = response.json()
            if "assistant" in data and "content" in data["assistant"]:
                print_result("Valid Request", True, f"Got response: {data['assistant']['content'][:50]}...")
                return True
            else:
                print_result("Valid Request", False, "Missing 'assistant.content' in response")
                return False
        else:
            print_result("Valid Request", False, f"Expected 200, got {response.status_code}")
            return False

    except requests.exceptions.Timeout:
        print_result("Valid Request", False, "Request timed out")
        return False
    except requests.exceptions.RequestException as e:
        print_result("Valid Request", False, f"Request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print_result("Valid Request", False, f"Invalid JSON response: {e}")
        return False


def test_missing_body(url: str, api_key: str, verbose: bool = False) -> bool:
    """Test request with missing body (should return 400)."""
    print("\n--- Test: Missing Request Body ---")
    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": api_key,
    }

    try:
        # Send request with empty body
        response = requests.post(url, headers=headers, data="", timeout=30)

        if verbose:
            print(f"  Status Code: {response.status_code}")
            print(f"  Response: {response.text}")

        if response.status_code == 400:
            data = response.json()
            if "error" in data:
                print_result("Missing Body", True, f"Got expected error: {data['error']}")
                return True
            else:
                print_result("Missing Body", False, "Expected error message in response")
                return False
        else:
            print_result("Missing Body", False, f"Expected 400, got {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print_result("Missing Body", False, f"Request failed: {e}")
        return False


def test_invalid_json(url: str, api_key: str, verbose: bool = False) -> bool:
    """Test request with invalid JSON payload (should return 400)."""
    print("\n--- Test: Invalid JSON Payload ---")
    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": api_key,
    }

    try:
        # Send malformed JSON
        response = requests.post(url, headers=headers, data="{invalid json", timeout=30)

        if verbose:
            print(f"  Status Code: {response.status_code}")
            print(f"  Response: {response.text}")

        if response.status_code == 400:
            data = response.json()
            if "error" in data and "Invalid JSON" in data["error"]:
                print_result("Invalid JSON", True, f"Got expected error: {data['error']}")
                return True
            else:
                print_result("Invalid JSON", True, f"Got 400 with error: {data.get('error', 'unknown')}")
                return True
        else:
            print_result("Invalid JSON", False, f"Expected 400, got {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print_result("Invalid JSON", False, f"Request failed: {e}")
        return False


def test_missing_thread_id(url: str, api_key: str, verbose: bool = False) -> bool:
    """Test request with missing threadId (should return 400)."""
    print("\n--- Test: Missing threadId ---")
    payload = {
        "messages": [{"role": "user", "content": "Hello"}],
    }

    try:
        response = make_request(url, api_key, payload, verbose=verbose)

        if verbose:
            print(f"  Status Code: {response.status_code}")
            print(f"  Response: {response.text}")

        if response.status_code == 400:
            data = response.json()
            if "error" in data and "threadId" in data["error"]:
                print_result("Missing threadId", True, f"Got expected error: {data['error']}")
                return True
            else:
                print_result("Missing threadId", False, f"Unexpected error: {data.get('error', 'unknown')}")
                return False
        else:
            print_result("Missing threadId", False, f"Expected 400, got {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print_result("Missing threadId", False, f"Request failed: {e}")
        return False


def test_messages_not_array(url: str, api_key: str, verbose: bool = False) -> bool:
    """Test request with messages as non-array (should return 400)."""
    print("\n--- Test: Messages Not Array ---")
    payload = {
        "threadId": "test-thread",
        "messages": "not an array",
    }

    try:
        response = make_request(url, api_key, payload, verbose=verbose)

        if verbose:
            print(f"  Status Code: {response.status_code}")
            print(f"  Response: {response.text}")

        if response.status_code == 400:
            data = response.json()
            if "error" in data and "array" in data["error"]:
                print_result("Messages Not Array", True, f"Got expected error: {data['error']}")
                return True
            else:
                print_result("Messages Not Array", False, f"Unexpected error: {data.get('error', 'unknown')}")
                return False
        else:
            print_result("Messages Not Array", False, f"Expected 400, got {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print_result("Messages Not Array", False, f"Request failed: {e}")
        return False


def test_empty_messages(url: str, api_key: str, verbose: bool = False) -> bool:
    """Test request with empty messages array (should return 400)."""
    print("\n--- Test: Empty Messages Array ---")
    payload = {
        "threadId": "test-thread",
        "messages": [],
    }

    try:
        response = make_request(url, api_key, payload, verbose=verbose)

        if verbose:
            print(f"  Status Code: {response.status_code}")
            print(f"  Response: {response.text}")

        if response.status_code == 400:
            data = response.json()
            if "error" in data and "empty" in data["error"]:
                print_result("Empty Messages", True, f"Got expected error: {data['error']}")
                return True
            else:
                print_result("Empty Messages", False, f"Unexpected error: {data.get('error', 'unknown')}")
                return False
        else:
            print_result("Empty Messages", False, f"Expected 400, got {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print_result("Empty Messages", False, f"Request failed: {e}")
        return False


def test_missing_api_key(url: str, api_key: str, verbose: bool = False) -> bool:
    """Test request without API key (should return 403)."""
    print("\n--- Test: Missing API Key ---")
    payload = {
        "threadId": "test-thread",
        "messages": [{"role": "user", "content": "Hello"}],
    }
    headers = {
        "Content-Type": "application/json",
        # Deliberately omitting X-Api-Key
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        if verbose:
            print(f"  Status Code: {response.status_code}")
            print(f"  Response: {response.text}")

        if response.status_code == 403:
            print_result("Missing API Key", True, "Got expected 403 Forbidden")
            return True
        else:
            print_result("Missing API Key", False, f"Expected 403, got {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print_result("Missing API Key", False, f"Request failed: {e}")
        return False


def test_invalid_api_key(url: str, api_key: str, verbose: bool = False) -> bool:
    """Test request with invalid API key (should return 403)."""
    print("\n--- Test: Invalid API Key ---")
    payload = {
        "threadId": "test-thread",
        "messages": [{"role": "user", "content": "Hello"}],
    }

    try:
        response = make_request(url, "invalid-api-key-12345", payload, verbose=verbose)

        if verbose:
            print(f"  Status Code: {response.status_code}")
            print(f"  Response: {response.text}")

        if response.status_code == 403:
            print_result("Invalid API Key", True, "Got expected 403 Forbidden")
            return True
        else:
            print_result("Invalid API Key", False, f"Expected 403, got {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print_result("Invalid API Key", False, f"Request failed: {e}")
        return False


def test_cors_preflight(url: str, api_key: str, verbose: bool = False) -> bool:
    """Test CORS preflight OPTIONS request."""
    print("\n--- Test: CORS Preflight (OPTIONS) ---")
    headers = {
        "Access-Control-Request-Method": "POST",
        "Origin": "http://localhost:5173",
    }

    try:
        response = requests.options(url, headers=headers, timeout=30)

        if verbose:
            print(f"  Status Code: {response.status_code}")
            print(f"  Headers: {dict(response.headers)}")

        if response.status_code == 200:
            cors_origin = response.headers.get("Access-Control-Allow-Origin", "")
            cors_methods = response.headers.get("Access-Control-Allow-Methods", "")

            if cors_origin and cors_methods:
                print_result("CORS Preflight", True, f"Origin: {cors_origin}, Methods: {cors_methods}")
                return True
            else:
                print_result("CORS Preflight", False, "Missing CORS headers in response")
                return False
        else:
            print_result("CORS Preflight", False, f"Expected 200, got {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print_result("CORS Preflight", False, f"Request failed: {e}")
        return False


def run_all_tests(url: str, api_key: str, verbose: bool = False) -> dict:
    """Run all tests and return summary."""
    tests = [
        ("Success Request", test_success_request),
        ("Missing Body", test_missing_body),
        ("Invalid JSON", test_invalid_json),
        ("Missing threadId", test_missing_thread_id),
        ("Messages Not Array", test_messages_not_array),
        ("Empty Messages", test_empty_messages),
        ("Missing API Key", test_missing_api_key),
        ("Invalid API Key", test_invalid_api_key),
        ("CORS Preflight", test_cors_preflight),
    ]

    results = {"passed": 0, "failed": 0, "details": []}

    for name, test_func in tests:
        try:
            passed = test_func(url, api_key, verbose)
            if passed:
                results["passed"] += 1
            else:
                results["failed"] += 1
            results["details"].append((name, passed))
        except Exception as e:
            print_result(name, False, f"Unexpected error: {e}")
            results["failed"] += 1
            results["details"].append((name, False))

    return results


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Test API endpoints for success and failure scenarios.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python test_api.py --env test
    python test_api.py --env prod --verbose
    python test_api.py --env test --test success
        """,
    )
    parser.add_argument(
        "--env",
        choices=["prod", "test"],
        default="test",
        help="Environment to test (default: test)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed request/response information",
    )
    parser.add_argument(
        "--test", "-t",
        choices=["all", "success", "missing-body", "invalid-json", "missing-threadid",
                 "messages-not-array", "empty-messages", "missing-key", "invalid-key", "cors"],
        default="all",
        help="Specific test to run (default: all)",
    )
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    # Get API key and URL
    try:
        api_key = get_api_key()
        url = get_api_url(args.env)
    except EnvironmentError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    print(f"\n{'='*60}")
    print(f"API Test Suite - Environment: {args.env.upper()}")
    print(f"URL: {url}")
    print(f"{'='*60}")

    # Run tests
    test_map = {
        "success": test_success_request,
        "missing-body": test_missing_body,
        "invalid-json": test_invalid_json,
        "missing-threadid": test_missing_thread_id,
        "messages-not-array": test_messages_not_array,
        "empty-messages": test_empty_messages,
        "missing-key": test_missing_api_key,
        "invalid-key": test_invalid_api_key,
        "cors": test_cors_preflight,
    }

    if args.test == "all":
        results = run_all_tests(url, api_key, args.verbose)

        # Print summary
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        print(f"Passed: {results['passed']}")
        print(f"Failed: {results['failed']}")
        print(f"Total:  {results['passed'] + results['failed']}")

        if results["failed"] > 0:
            print("\nFailed tests:")
            for name, passed in results["details"]:
                if not passed:
                    print(f"  - {name}")
            sys.exit(1)
        else:
            print("\n✅ All tests passed!")
            sys.exit(0)
    else:
        # Run single test
        test_func = test_map[args.test]
        passed = test_func(url, api_key, args.verbose)
        sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
