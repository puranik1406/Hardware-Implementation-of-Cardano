"""
AWS Bedrock Configuration for Agent A
"""

import os
from typing import Optional

class AWSConfig:
    """AWS Bedrock configuration management"""
    
    # AWS Credentials
    AWS_ACCESS_KEY_ID: str = "YOUR_AWS_ACCESS_KEY_ID"
    AWS_SECRET_ACCESS_KEY: str = "YOUR_AWS_SECRET_ACCESS_KEY"
    AWS_REGION: str = "eu-north-1"
    
    # Bedrock Configuration
    BEDROCK_MODEL_ID: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    USE_MOCK_BEDROCK: bool = False  # Set to False for real Bedrock
    
    # Service Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    LOG_LEVEL: str = "INFO"
    
    # Offer Configuration
    FALLBACK_THRESHOLD: float = 1000000  # 1 ADA in lovelace
    MIN_OFFER_AMOUNT: float = 100000     # 0.1 ADA
    MAX_OFFER_AMOUNT: float = 10000000   # 10 ADA
    
    @classmethod
    def get_bedrock_config(cls) -> dict:
        """Get Bedrock configuration dictionary"""
        return {
            "aws_access_key_id": cls.AWS_ACCESS_KEY_ID,
            "aws_secret_access_key": cls.AWS_SECRET_ACCESS_KEY,
            "region_name": cls.AWS_REGION
        }
    
    @classmethod
    def validate_credentials(cls) -> bool:
        """Validate AWS credentials are set"""
        return all([
            cls.AWS_ACCESS_KEY_ID,
            cls.AWS_SECRET_ACCESS_KEY,
            cls.AWS_REGION
        ])
    
    @classmethod
    def print_config(cls):
        """Print current configuration (without secrets)"""
        print("AWS Bedrock Configuration:")
        print(f"  Region: {cls.AWS_REGION}")
        print(f"  Model ID: {cls.BEDROCK_MODEL_ID}")
        print(f"  Mock Mode: {cls.USE_MOCK_BEDROCK}")
        print(f"  Credentials: {'✅ Set' if cls.validate_credentials() else '❌ Missing'}")

# Global config instance
aws_config = AWSConfig()
