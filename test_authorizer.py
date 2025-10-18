#!/usr/bin/env python3

import json
from lambda_function import lambda_handler

# Test event that mimics what API Gateway sends to Lambda authorizer
test_event = {
    "type": "REQUEST",
    "methodArn": "arn:aws:execute-api:us-east-1:123456789012:abcdef123/test/GET/request",
    "resource": "/request",
    "path": "/request",
    "httpMethod": "GET",
    "headers": {
        "X-AMZ-Date": "20170718T062915Z",
        "Accept": "*/*",
        "HeaderAuth1": "headerValue1",
        "CloudFront-Viewer-Country": "US",
        "CloudFront-Forwarded-Proto": "https",
        "CloudFront-Is-Tablet-Viewer": "false"
    },
    "queryStringParameters": {
        "QueryString1": "queryValue1",
        "token": "eyJraWQiOiJRVXQ2MGN4ZzRJVmhaV05MeDNVNnhtYTQ2VTN2N2JjeWY4S2RhMkx2UHpNPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIxNWpvN2xkNjE4ZTV2cmI2Z2ZyNGRwa29rOSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiZGVmYXVsdC1tMm0tcmVzb3VyY2Utc2VydmVyLXlscHNlb1wvcmVhZCIsImF1dGhfdGltZSI6MTc2MDY2NzE2NywiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMS5hbWF6b25hd3MuY29tXC91cy1lYXN0LTFfSmFQd2s3T2lRIiwiZXhwIjoxNzYwNjcwNzY3LCJpYXQiOjE3NjA2NjcxNjcsInZlcnNpb24iOjIsImp0aSI6ImFjNzM4OTJhLTQwZTUtNGQyOC05YjI4LTQyZmNlNzViMjA0OCIsImNsaWVudF9pZCI6IjE1am83bGQ2MThlNXZyYjZnZnI0ZHBrb2s5In0.EOA2d2CSuJMGjvFHE7Q6OnE5703FpahjfCEPUo65sG3eVCGT8JN6o3J96SQcXuCMUnO61iChDTG-18WcNuHvYWfHdnOEuVKfWSXS9WBGaSbwBI4Tsi6QjXaFoUbWthMIqur1VAhM9LARxSuoV4dmp6txvue0OQ38DVzdj_0XJV7MpeBN4MUgljsE4aBKOj23ipRUYRX5WIobk4Dv92kWGOX-gW0wAQFDBPFjfM46eeIOHKfihqOfOwK53UxO353h0nxqVO2rzzBxhKNkZdV3ODSq1LBOH81W40sUtO5u0njDGiY2nPtRam3B06zA3uj_12oT4aZNAnSFYYm-ycsGNg"
    },
    "pathParameters": {
        "PathParam1": "pathValue1"
    },
    "stageVariables": {
        "StageVar1": "stageValue1"
    },
    "requestContext": {
        "path": "/request",
        "accountId": "123456789012",
        "resourceId": "05c7jb",
        "stage": "test",
        "requestId": "...",
        "identity": {
            "apiKey": "...",
            "sourceIp": "...",
            "clientCert": "..."
        },
        "resourcePath": "/request",
        "httpMethod": "GET",
        "apiId": "abcdef123"
    },
    # For identity source $request.querystring.token, API Gateway puts the token here
    "authorizationToken": "eyJraWQiOiJRVXQ2MGN4ZzRJVmhaV05MeDNVNnhtYTQ2VTN2N2JjeWY4S2RhMkx2UHpNPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIxNWpvN2xkNjE4ZTV2cmI2Z2ZyNGRwa29rOSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiZGVmYXVsdC1tMm0tcmVzb3VyY2Utc2VydmVyLXlscHNlb1wvcmVhZCIsImF1dGhfdGltZSI6MTc2MDY2NzE2NywiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMS5hbWF6b25hd3MuY29tXC91cy1lYXN0LTFfSmFQd2s3T2lRIiwiZXhwIjoxNzYwNjcwNzY3LCJpYXQiOjE3NjA2NjcxNjcsInZlcnNpb24iOjIsImp0aSI6ImFjNzM4OTJhLTQwZTUtNGQyOC05YjI4LTQyZmNlNzViMjA0OCIsImNsaWVudF9pZCI6IjE1am83bGQ2MThlNXZyYjZnZnI0ZHBrb2s5In0.EOA2d2CSuJMGjvFHE7Q6OnE5703FpahjfCEPUo65sG3eVCGT8JN6o3J96SQcXuCMUnO61iChDTG-18WcNuHvYWfHdnOEuVKfWSXS9WBGaSbwBI4Tsi6QjXaFoUbWthMIqur1VAhM9LARxSuoV4dmp6txvue0OQ38DVzdj_0XJV7MpeBN4MUgljsE4aBKOj23ipRUYRX5WIobk4Dv92kWGOX-gW0wAQFDBPFjfM46eeIOHKfihqOfOwK53UxO353h0nxqVO2rzzBxhKNkZdV3ODSq1LBOH81W40sUtO5u0njDGiY2nPtRam3B06zA3uj_12oT4aZNAnSFYYm-ycsGNg"
}

if __name__ == "__main__":
    # Set environment variables for testing
    import os
    os.environ['USER_POOL_ID'] = 'us-east-1_JaPwk7OiQ'
    os.environ['EXPECTED_AUDIENCE'] = '15jo7ld618e5vrb6gfr4dpkok9'
    os.environ['COGNITO_REGION'] = 'us-east-1'
    
    try:
        result = lambda_handler(test_event, None)
        print("SUCCESS:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print("ERROR:")
        print(str(e))