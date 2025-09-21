# AWS Bedrock Environment Setup for Agent A (PowerShell)

Write-Host "Setting up AWS Bedrock environment for Agent A..." -ForegroundColor Green

# Set AWS credentials
$env:AWS_ACCESS_KEY_ID = "YOUR_AWS_ACCESS_KEY_ID"
$env:AWS_SECRET_ACCESS_KEY = "YOUR_AWS_SECRET_ACCESS_KEY"
$env:AWS_REGION = "eu-north-1"

# Set Agent A configuration
$env:USE_MOCK_BEDROCK = "false"
$env:BEDROCK_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"
$env:LOG_LEVEL = "INFO"
$env:HOST = "0.0.0.0"
$env:PORT = "8001"

Write-Host "Environment variables set:" -ForegroundColor Yellow
Write-Host "  AWS_REGION=$env:AWS_REGION"
Write-Host "  USE_MOCK_BEDROCK=$env:USE_MOCK_BEDROCK"
Write-Host "  BEDROCK_MODEL_ID=$env:BEDROCK_MODEL_ID"
Write-Host "  LOG_LEVEL=$env:LOG_LEVEL"

Write-Host ""
Write-Host "Starting Agent A service with AWS Bedrock..." -ForegroundColor Green
python start_agent_a.py
