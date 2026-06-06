"""
Local test script for the URL Shortener Lambda function.
Run: python test_lambda.py
Requires: AWS credentials configured + DynamoDB table exists
"""

import json
from lambda_function import lambda_handler

# ── Test 1: Shorten a URL ───────────────────────────────────────────────────
print("=== Test 1: POST /shorten ===")
event_post = {
    "httpMethod": "POST",
    "path": "/shorten",
    "pathParameters": None,
    "body": json.dumps({"url": "https://www.google.com"})
}
response = lambda_handler(event_post, {})
print(f"Status: {response['statusCode']}")
body = json.loads(response['body'])
print(f"Response: {json.dumps(body, indent=2)}")
short_code = body.get('short_code', 'abc123')

# ── Test 2: Redirect using short code ───────────────────────────────────────
print(f"\n=== Test 2: GET /{short_code} (redirect) ===")
event_get = {
    "httpMethod": "GET",
    "path": f"/{short_code}",
    "pathParameters": {"short_code": short_code},
    "body": None
}
response = lambda_handler(event_get, {})
print(f"Status: {response['statusCode']}")
print(f"Location: {response.get('headers', {}).get('Location', 'N/A')}")

# ── Test 3: Invalid short code ───────────────────────────────────────────────
print("\n=== Test 3: GET /invalid (404) ===")
event_invalid = {
    "httpMethod": "GET",
    "path": "/invalid",
    "pathParameters": {"short_code": "invalid"},
    "body": None
}
response = lambda_handler(event_invalid, {})
print(f"Status: {response['statusCode']}")
print(f"Response: {response['body']}")

# ── Test 4: Missing URL in body ──────────────────────────────────────────────
print("\n=== Test 4: POST /shorten with missing URL (400) ===")
event_bad = {
    "httpMethod": "POST",
    "path": "/shorten",
    "pathParameters": None,
    "body": json.dumps({})
}
response = lambda_handler(event_bad, {})
print(f"Status: {response['statusCode']}")
print(f"Response: {response['body']}")
