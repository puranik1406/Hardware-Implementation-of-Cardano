#!/usr/bin/env python3
"""
AWS Bedrock Setup Script for Agent A
"""

import boto3
import json
from botocore.exceptions import ClientError, NoCredentialsError
from aws_config import aws_config

def test_aws_connection():
    """Test AWS credentials and Bedrock access"""
    print("🔐 Testing AWS Bedrock Connection...")
    print("=" * 50)
    
    try:
        # Test basic AWS connection
        print("1. Testing AWS credentials...")
        session = boto3.Session(
            aws_access_key_id=aws_config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=aws_config.AWS_SECRET_ACCESS_KEY,
            region_name=aws_config.AWS_REGION
        )
        
        # Test STS (Security Token Service) to validate credentials
        sts_client = session.client('sts')
        identity = sts_client.get_caller_identity()
        print(f"   ✅ AWS credentials valid")
        print(f"   📋 Account ID: {identity.get('Account', 'Unknown')}")
        print(f"   👤 User ARN: {identity.get('Arn', 'Unknown')}")
        
    except NoCredentialsError:
        print("   ❌ AWS credentials not found")
        return False
    except ClientError as e:
        print(f"   ❌ AWS credentials invalid: {e}")
        return False
    except Exception as e:
        print(f"   ❌ AWS connection failed: {e}")
        return False
    
    try:
        # Test Bedrock access
        print("\n2. Testing Bedrock access...")
        bedrock_client = session.client('bedrock-runtime')
        
        # List available models
        print("   📋 Available Bedrock models:")
        try:
            # Note: This might not work in all regions, but it's a good test
            response = bedrock_client.list_foundation_models()
            models = response.get('modelSummaries', [])
            for model in models[:5]:  # Show first 5 models
                print(f"      - {model.get('modelId', 'Unknown')}")
        except Exception as e:
            print(f"      ⚠️  Could not list models: {e}")
            print("      (This is normal in some regions)")
        
        print("   ✅ Bedrock client created successfully")
        
    except ClientError as e:
        print(f"   ❌ Bedrock access failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Bedrock connection failed: {e}")
        return False
    
    return True

def test_bedrock_inference():
    """Test actual Bedrock inference"""
    print("\n3. Testing Bedrock inference...")
    
    try:
        session = boto3.Session(
            aws_access_key_id=aws_config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=aws_config.AWS_SECRET_ACCESS_KEY,
            region_name=aws_config.AWS_REGION
        )
        
        bedrock_client = session.client('bedrock-runtime')
        
        # Test prompt
        test_prompt = """
You are Agent A, a buyer AI agent. Please respond with a JSON object in this exact format:
{
    "status": "accepted",
    "amount": 1000000,
    "offer_id": "test-123",
    "decision_reason": "Test decision",
    "timestamp": "2024-01-01T00:00:00Z"
}

Respond with ONLY the JSON object, no other text.
"""
        
        print("   🧪 Sending test prompt to Bedrock...")
        response = bedrock_client.invoke_model(
            modelId=aws_config.BEDROCK_MODEL_ID,
            body=json.dumps({
                "prompt": test_prompt,
                "max_tokens_to_sample": 200,
                "temperature": 0.7
            })
        )
        
        response_body = json.loads(response['body'].read())
        completion = response_body['completion']
        
        print(f"   📤 Raw response: {completion}")
        
        # Try to parse JSON
        try:
            parsed = json.loads(completion.strip())
            print(f"   ✅ JSON parsed successfully: {parsed}")
            return True
        except json.JSONDecodeError:
            print(f"   ⚠️  Response is not valid JSON: {completion}")
            return False
            
    except ClientError as e:
        print(f"   ❌ Bedrock inference failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Bedrock test failed: {e}")
        return False

def setup_environment():
    """Set up environment variables for Agent A"""
    print("\n4. Setting up environment...")
    
    env_vars = {
        "AWS_ACCESS_KEY_ID": aws_config.AWS_ACCESS_KEY_ID,
        "AWS_SECRET_ACCESS_KEY": aws_config.AWS_SECRET_ACCESS_KEY,
        "AWS_REGION": aws_config.AWS_REGION,
        "USE_MOCK_BEDROCK": "false",
        "BEDROCK_MODEL_ID": aws_config.BEDROCK_MODEL_ID,
        "LOG_LEVEL": "INFO"
    }
    
    print("   📋 Environment variables to set:")
    for key, value in env_vars.items():
        if "SECRET" in key:
            print(f"      {key}=***hidden***")
        else:
            print(f"      {key}={value}")
    
    return env_vars

def main():
    """Main setup function"""
    print("🚀 AWS Bedrock Setup for Agent A")
    print("=" * 50)
    
    # Print current configuration
    aws_config.print_config()
    
    # Test AWS connection
    if not test_aws_connection():
        print("\n❌ AWS setup failed. Please check your credentials.")
        return False
    
    # Test Bedrock inference
    if not test_bedrock_inference():
        print("\n⚠️  Bedrock inference test failed, but connection is working.")
        print("   This might be due to model availability in your region.")
    
    # Set up environment
    env_vars = setup_environment()
    
    print("\n✅ AWS Bedrock setup completed!")
    print("\n📋 Next steps:")
    print("1. Set the environment variables above")
    print("2. Start Agent A service: python start_agent_a.py")
    print("3. Test with real Bedrock: python test_agent_a.py")
    
    return True

if __name__ == "__main__":
    main()
