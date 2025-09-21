@echo off
REM AWS Bedrock Environment Setup for Agent A

echo Setting up AWS Bedrock environment for Agent A...

REM Set AWS credentials
set AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY_ID
set AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_ACCESS_KEY
set AWS_REGION=eu-north-1

REM Set Agent A configuration
set USE_MOCK_BEDROCK=false
set BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
set LOG_LEVEL=INFO
set HOST=0.0.0.0
set PORT=8001

echo Environment variables set:
echo   AWS_REGION=%AWS_REGION%
echo   USE_MOCK_BEDROCK=%USE_MOCK_BEDROCK%
echo   BEDROCK_MODEL_ID=%BEDROCK_MODEL_ID%
echo   LOG_LEVEL=%LOG_LEVEL%

echo.
echo Starting Agent A service with AWS Bedrock...
python start_agent_a.py
