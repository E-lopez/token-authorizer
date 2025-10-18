#!/bin/bash

set -e

# Configuration
ENVIRONMENT=${1:-dev}
S3_BUCKET=${2:-token-authorizer-deployment-bucket}
USER_POOL_ID=${3}
EXPECTED_AUDIENCE=${4}
COGNITO_REGION=${5:-us-east-1}
STACK_NAME="token-authorizer-${ENVIRONMENT}"
AWS_REGION="us-east-1"

echo "Deploying Token Authorizer Lambda for environment: $ENVIRONMENT"
echo "S3 Bucket: $S3_BUCKET"
echo "Stack Name: $STACK_NAME"
echo "Region: $AWS_REGION"

# Create deployment package
echo "Creating deployment package..."
rm -rf package/
mkdir -p package/

# Install dependencies with proper wheels for Lambda
echo "Installing dependencies..."

# Install dependencies for token authorizer
python3 -m pip install \
--platform manylinux2014_aarch64 \
--target=package \
--implementation cp \
--python-version 3.13 \
--only-binary=:all: --upgrade \
requests PyJWT cryptography

# Copy source code
echo "Copying source code..."
cp lambda_function.py package/

# Create ZIP file
echo "Creating ZIP file..."
cd package
zip -r ../function.zip . -x "*.pyc" "*__pycache__*"
cd ..

# Upload to S3
echo "Uploading to S3..."
aws s3 cp function.zip s3://${S3_BUCKET}/token-authorizer/function.zip

# Deploy CloudFormation stack
echo "Deploying CloudFormation stack..."
aws cloudformation deploy \
    --template-file cloudformation-template.yaml \
    --stack-name ${STACK_NAME} \
    --parameter-overrides \
        Environment=${ENVIRONMENT} \
        S3Bucket=${S3_BUCKET} \
        S3Key=token-authorizer/function.zip \
        UserPoolId=${USER_POOL_ID} \
        ExpectedAudience=${EXPECTED_AUDIENCE} \
        CognitoRegion=${COGNITO_REGION} \
    --capabilities CAPABILITY_IAM \
    --region ${AWS_REGION}

# Get function ARN
echo "Getting function ARN..."
FUNCTION_ARN=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --query 'Stacks[0].Outputs[?OutputKey==`TokenAuthorizerFunctionArn`].OutputValue' \
    --output text \
    --region ${AWS_REGION})

echo ""
echo "Deployment completed successfully!"
echo "Environment: $ENVIRONMENT"
echo "Function ARN: $FUNCTION_ARN"
echo ""
echo "Token authorizer is ready to be attached to API Gateway routes"
echo ""
echo "Clean up..."
rm -rf package/
rm function.zip