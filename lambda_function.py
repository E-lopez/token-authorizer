import os
import jwt
import time
from config import Config

# Get configuration from environment variables
ENV = os.environ.get('ENVIRONMENT', 'dev')
DOPPLER_TOKEN = os.environ.get('DOPPLER_TOKEN', 'DOPPLER_TOKEN')


def lambda_handler(event, context):
    print("UPDATED CODE - 2025-01-16 15:30:00 - NEW VERSION")
    print("Incoming event new version:", event)
    print("Event keys:", list(event.keys()))
    if 'queryStringParameters' in event:
        print("Query parameters:", event['queryStringParameters'])
    if 'headers' in event:
        print("Headers:", event['headers'])
    
    # Debug environment variables
    print(f"ENV: {ENV}")
    print(f"DOPPLER_TOKEN: {DOPPLER_TOKEN}")
    
    # Validate required environment variables
    if not ENV or not DOPPLER_TOKEN:
        print("Missing required environment variables.")
        return deny_response("Server configuration error")

    # For HTTP API v2 with identity source $request.querystring.token,
    # API Gateway passes the token in identitySource array
    identity_source = event.get('identitySource', [])
    token = identity_source[0] if identity_source and identity_source[0] else None
    
    # Fallback to queryStringParameters if identitySource is empty
    if not token:
        query_params = event.get('queryStringParameters') or {}
        token = query_params.get('token')
    
    print(f"Token extracted: {token[:20] if token else 'None'}...")
    
    if not token:
        print("Missing token in query parameter or Authorization header.")
        return deny_response("No token provided")

    try:
        config = Config()
        SECRET = config.SECRET_KEY

        print(f"Decoding token... {SECRET[:20]}...{SECRET[-5:]}")

        # For Cognito access tokens, we don't validate audience as they don't have 'aud' field
        decoded_token = jwt.decode(
            token,
            SECRET,
            algorithms=["HS256"],
        )

        # Optionally check scope, token_use, etc.
        token_use = decoded_token.get("token_use")
        print(f"Token use: {token_use}")
        if token_use != "access":
            return deny_response(f"Invalid token_use: {token_use}")

        token_issuer = decoded_token.get("iss")
        print(f"Token issuer: {token_issuer}")
        if token_issuer != "https://kredilatam.com/token-issuer":
            return deny_response(f"Invalid token_issuer: {token_issuer}")

        current_time = int(time.time())
        if decoded_token['exp'] < current_time:
            return deny_response('Token expired')

        print("Authorized token:", decoded_token)
        
        # For HTTP API v2 with Simple response mode, return boolean or context object
        response = {
            "isAuthorized": True
        }
        print("Returning authorization response:", response)
        return response

    except Exception as e:
        print(f"Authorization failed: {str(e)}")
        return deny_response(str(e))


def deny_response(message="Unauthorized"):
    # For HTTP API v2 with Simple response mode
    return {
        "isAuthorized": False
    }
