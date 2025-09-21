@echo off
echo ========================================
echo Agent A Manual Setup Guide
echo ========================================

echo.
echo Step 1: Setting environment variables...
set AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY_ID
set AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_ACCESS_KEY
set AWS_REGION=us-east-1
set USE_MOCK_BEDROCK=true
set BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
set LOG_LEVEL=INFO
set HOST=0.0.0.0
set PORT=8001

echo Environment variables set successfully!

echo.
echo Step 2: Installing dependencies...
pip install fastapi uvicorn boto3 pydantic requests python-multipart python-json-logger

echo.
echo Step 3: Testing Python imports...
python -c "import fastapi, uvicorn, boto3; print('All packages imported successfully')"

echo.
echo Step 4: Starting Agent A service...
echo Service will be available at: http://localhost:8001
echo API Documentation: http://localhost:8001/docs
echo.
echo Press Ctrl+C to stop the service
echo ========================================

python start_with_aws.py
