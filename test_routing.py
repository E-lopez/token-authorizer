#!/usr/bin/env python3

import json
from lambda_function import lambda_handler

# Test API Gateway v2 event format for POST /token
test_event_v2 = {
    "version": "2.0",
    "routeKey": "ANY /{proxy+}",
    "rawPath": "/token",
    "rawQueryString": "",
    "headers": {
        "content-type": "application/json"
    },
    "requestContext": {
        "http": {
            "method": "POST",
            "path": "/token",
            "protocol": "HTTP/1.1",
            "sourceIp": "127.0.0.1"
        }
    },
    "body": "",
    "isBase64Encoded": False
}

# Test API Gateway v1 event format for comparison
test_event_v1 = {
    "httpMethod": "POST",
    "path": "/token",
    "headers": {
        "Content-Type": "application/json"
    },
    "body": "",
    "pathParameters": None,
    "queryStringParameters": None
}

print("Testing API Gateway v2 format:")
print("Event:", json.dumps(test_event_v2, indent=2))
response_v2 = lambda_handler(test_event_v2, {})
print("Response:", json.dumps(response_v2, indent=2))

print("\n" + "="*50 + "\n")

print("Testing API Gateway v1 format:")
print("Event:", json.dumps(test_event_v1, indent=2))
response_v1 = lambda_handler(test_event_v1, {})
print("Response:", json.dumps(response_v1, indent=2))