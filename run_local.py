#!/usr/bin/env python3
"""
Local development server for data-tracker Lambda
Run with: python run_local.py
"""

print("Starting run_local.py...")

import sys
import os
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Configure logging for local development
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Import Lambda function from current directory
from lambda_function import lambda_handler

class LocalHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request('GET')
    
    def do_POST(self):
        self.handle_request('POST')
    
    def do_OPTIONS(self):
        self.handle_request('OPTIONS')
    
    def handle_request(self, method):
        print(f"Received {method} request to {self.path}")
        try:
            # Parse URL
            parsed_url = urlparse(self.path)
            
            # Read body for POST requests
            body = None
            if method == 'POST':
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    body = self.rfile.read(content_length).decode('utf-8')
            
            # Create Lambda event
            event = {
                'httpMethod': method,
                'path': parsed_url.path,
                'body': body,
                'headers': dict(self.headers),
                'pathParameters': {},
                'queryStringParameters': dict(parse_qs(parsed_url.query)) if parsed_url.query else {}
            }
            
        # This code extracts URL path parameters from endpoints with dynamic values
        # For example, in the URL "/repayment-plan/123":
        # - path_parts[0] would be "repayment-plan" 
        # - path_parts[1] would be "123"
        # If you add new endpoints with path parameters like "/users/{id}/profile":
        # - Add another condition to check path_parts[0] == "users"
        # - Map parameters to event['pathParameters'] based on position
        # Example:
        #   if len(path_parts) >= 3 and path_parts[0] == "users":
        #       event['pathParameters'] = {'id': path_parts[1]}
            path_parts = parsed_url.path.strip('/').split('/')
            if len(path_parts) >= 2 and path_parts[0] == 'repayment-plan':
                event['pathParameters'] = {'user_id': path_parts[1]}
            
            # Call Lambda handler
            response = lambda_handler(event, {})
            
            # Send response
            self.send_response(response['statusCode'])
            
            # Set headers
            for key, value in response.get('headers', {}).items():
                self.send_header(key, value)
            self.end_headers()
            
            # Send body
            self.wfile.write(response['body'].encode('utf-8'))
            
        except Exception as e:
            print(f"Error handling request: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = json.dumps({'error': str(e)})
            self.wfile.write(error_response.encode('utf-8'))

def main():
    # Set environment variables for local testing
    os.environ['ENVIRONMENT'] = 'local'
    
    print("Environment variables:")
    print(f"  COGNITO_CLIENT_ID: {os.environ.get('COGNITO_CLIENT_ID', 'NOT SET')}")
    print(f"  COGNITO_CLIENT_SECRET: {os.environ.get('COGNITO_CLIENT_SECRET', 'NOT SET')}")
    print(f"  COGNITO_TOKEN_URL: {os.environ.get('COGNITO_TOKEN_URL', 'NOT SET')}")

    
    port = 8080
    server = HTTPServer(('localhost', port), LocalHandler)
    
    print(f"🚀 Auth Handler running locally at http://localhost:{port}")
    print("📋 Available endpoints:")
    print("  GET  /health - Health check")
    print("  POST /token - Get M2M Cognito token")
    print("\n💡 Test with:")
    print(f"  curl http://localhost:{port}/health")
    print(f"  curl -X POST http://localhost:{port}/token")
    print("\n⏹️  Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        server.shutdown()

if __name__ == '__main__':
    main()