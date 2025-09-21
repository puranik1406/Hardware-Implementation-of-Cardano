"""
Configuration settings for Agent A
"""

import os
from typing import Optional

class Config:
    """Configuration class for Agent A service"""
    
    # AWS Bedrock Configuration - Using provided credentials
    BEDROCK_MODEL_ID: str = os.getenv("BEDROCK_MODEL_ID", "FTQPCW1EV3")
    AWS_REGION: str = os.getenv("AWS_REGION", "eu-north-1")
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "YOUR_AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "YOUR_AWS_SECRET_ACCESS_KEY")
    
    # Service Configuration
    USE_MOCK_BEDROCK: bool = os.getenv("USE_MOCK_BEDROCK", "false").lower() == "true"  # Default to real Bedrock
    FALLBACK_THRESHOLD: float = float(os.getenv("FALLBACK_THRESHOLD", "1000000"))  # 1 ADA in lovelace
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # API Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8001"))
    
    # Router Integration
    ROUTER_URL: str = os.getenv("ROUTER_URL", "http://localhost:5000")
    
    # Offer Schema Configuration
    MIN_OFFER_AMOUNT: float = float(os.getenv("MIN_OFFER_AMOUNT", "100000"))  # 0.1 ADA
    MAX_OFFER_AMOUNT: float = float(os.getenv("MAX_OFFER_AMOUNT", "10000000"))  # 10 ADA
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration settings"""
        if not cls.USE_MOCK_BEDROCK:
            if not cls.AWS_ACCESS_KEY_ID or not cls.AWS_SECRET_ACCESS_KEY:
                print("Warning: AWS credentials not set, falling back to mock mode")
                cls.USE_MOCK_BEDROCK = True
                return False
        
        if cls.FALLBACK_THRESHOLD < cls.MIN_OFFER_AMOUNT:
            print(f"Warning: Fallback threshold {cls.FALLBACK_THRESHOLD} is below minimum offer amount {cls.MIN_OFFER_AMOUNT}")
            return False
            
        return True

# Global config instance
config = Config()

