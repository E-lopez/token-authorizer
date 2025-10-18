import os
import jwt
from jwt import PyJWKClient

# Get configuration from environment variables
COGNITO_REGION = os.environ.get('COGNITO_REGION', 'us-east-1')
USER_POOL_ID = os.environ.get('USER_POOL_ID')
EXPECTED_AUDIENCE = os.environ.get('EXPECTED_AUDIENCE')

# Only set ISSUER and JWKS_URL if USER_POOL_ID exists
if USER_POOL_ID:
    ISSUER = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{USER_POOL_ID}"
    JWKS_URL = f"{ISSUER}/.well-known/jwks.json"
else:
    ISSUER = None
    JWKS_URL = None

def lambda_handler(event, context):
    print("UPDATED CODE - 2025-01-16 15:30:00 - NEW VERSION")
    print("Incoming event new version:", event)
    print("Event keys:", list(event.keys()))
    if 'queryStringParameters' in event:
        print("Query parameters:", event['queryStringParameters'])
    if 'headers' in event:
        print("Headers:", event['headers'])
    
    # Debug environment variables
    print(f"USER_POOL_ID: {USER_POOL_ID}")
    print(f"EXPECTED_AUDIENCE: {EXPECTED_AUDIENCE}")
    print(f"COGNITO_REGION: {COGNITO_REGION}")
    print(f"All env vars: {dict(os.environ)}")
    
    # Validate required environment variables
    if not USER_POOL_ID or not EXPECTED_AUDIENCE:
        print("Missing required environment variables: USER_POOL_ID, EXPECTED_AUDIENCE")
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
        jwk_client = PyJWKClient(JWKS_URL)
        signing_key = jwk_client.get_signing_key_from_jwt(token)

        # For Cognito access tokens, we don't validate audience as they don't have 'aud' field
        decoded_token = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=ISSUER,
            options={"verify_aud": False}  # Cognito access tokens don't have audience
        )

        # Optionally check scope, token_use, etc.
        token_use = decoded_token.get("token_use")
        if token_use != "access":
            return deny_response(f"Invalid token_use: {token_use}")

        print("Authorized token:", decoded_token)
        
        # For HTTP API v2 with Simple response mode, return context object
        return {
            "isAuthorized": True,
            "context": {
                "client_id": decoded_token.get("client_id", ""),
                "scope": decoded_token.get("scope", ""),
                "sub": decoded_token.get("sub", ""),
            }
        }

    except Exception as e:
        print(f"Authorization failed: {str(e)}")
        return deny_response(str(e))


def deny_response(message="Unauthorized"):
    # For HTTP API v2 with Simple response mode
    return {
        "isAuthorized": False,
        "context": {
            "error": message
        }
    }
