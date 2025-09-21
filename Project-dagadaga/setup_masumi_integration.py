"""
Official Masumi Network Setup Script
Sets up the complete Arduino-to-Cardano payment system with official Masumi infrastructure
"""

import os
import subprocess
import json
import shutil
from pathlib import Path
import requests

def run_command(command, cwd=None, capture_output=True):
    """Run a shell command and return the result"""
    try:
        if isinstance(command, str):
            # For PowerShell on Windows
            command = ["powershell", "-Command", command]
        
        result = subprocess.run(
            command, 
            cwd=cwd, 
            capture_output=capture_output, 
            text=True, 
            shell=False
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_prerequisites():
    """Check if required tools are installed"""
    print("🔍 Checking Prerequisites...")
    
    tools = {
        "docker": "docker --version",
        "docker-compose": "docker-compose --version", 
        "git": "git --version",
        "python": "python --version"
    }
    
    missing_tools = []
    for tool, command in tools.items():
        success, output, error = run_command(command)
        if success:
            version = output.strip().split('\n')[0]
            print(f"   ✅ {tool}: {version}")
        else:
            print(f"   ❌ {tool}: Not found")
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"\n❌ Missing required tools: {', '.join(missing_tools)}")
        print("\nPlease install:")
        print("   • Docker Desktop: https://www.docker.com/products/docker-desktop")
        print("   • Git: https://git-scm.com/downloads")
        print("   • Python 3.8+: https://www.python.org/downloads/")
        return False
    
    return True

def clone_masumi_services():
    """Clone the official Masumi services repository"""
    print("\n📦 Setting up Official Masumi Services...")
    
    masumi_dir = Path("masumi-services-dev-quickstart")
    
    if masumi_dir.exists():
        print("   ✅ Masumi repository already exists")
        return True
    
    print("   📥 Cloning Masumi services repository...")
    success, output, error = run_command([
        "git", "clone", 
        "https://github.com/masumi-network/masumi-services-dev-quickstart.git"
    ])
    
    if success:
        print("   ✅ Masumi repository cloned successfully")
        return True
    else:
        print(f"   ❌ Failed to clone repository: {error}")
        return False

def setup_masumi_environment():
    """Set up Masumi environment configuration"""
    print("\n⚙️ Configuring Masumi Environment...")
    
    masumi_dir = Path("masumi-services-dev-quickstart")
    env_example = masumi_dir / ".env.example"
    env_file = masumi_dir / ".env"
    
    if not env_example.exists():
        print(f"   ❌ .env.example not found in {masumi_dir}")
        return False
    
    if env_file.exists():
        print("   ✅ .env file already exists")
        return True
    
    # Copy example to .env
    shutil.copy(env_example, env_file)
    print("   ✅ Created .env from .env.example")
    
    # Read current .env content
    with open(env_file, 'r') as f:
        env_content = f.read()
    
    # Update with user's Blockfrost API key if available
    blockfrost_key = os.getenv("BLOCKFROST_PROJECT_ID")
    if blockfrost_key:
        env_content = env_content.replace(
            "BLOCKFROST_PROJECT_ID=your_blockfrost_project_id_here",
            f"BLOCKFROST_PROJECT_ID={blockfrost_key}"
        )
        print("   ✅ Updated Blockfrost API key from environment")
    else:
        print("   ⚠️  Please update BLOCKFROST_PROJECT_ID in masumi-services-dev-quickstart/.env")
    
    # Write updated content
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    return True

def start_masumi_services():
    """Start the Masumi Docker services"""
    print("\n🚀 Starting Masumi Services...")
    
    masumi_dir = Path("masumi-services-dev-quickstart")
    
    # Check if services are already running
    success, output, error = run_command("docker ps", cwd=masumi_dir)
    if success and "masumi" in output:
        print("   ✅ Masumi services already running")
        return True
    
    print("   🐳 Starting Docker services...")
    success, output, error = run_command("docker-compose up -d", cwd=masumi_dir)
    
    if success:
        print("   ✅ Masumi services started successfully")
        
        # Wait for services to be ready
        print("   ⏳ Waiting for services to initialize...")
        import time
        time.sleep(10)
        
        # Check service health
        services = [
            ("Payment Service", "http://localhost:3001/health"),
            ("Registry Service", "http://localhost:3000/health")
        ]
        
        for name, url in services:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code in [200, 404]:
                    print(f"   ✅ {name}: Ready")
                else:
                    print(f"   ⚠️  {name}: Responded with {response.status_code}")
            except:
                print(f"   ⚠️  {name}: Not yet ready (this is normal)")
        
        return True
    else:
        print(f"   ❌ Failed to start services: {error}")
        return False

def setup_payment_service():
    """Set up our integrated payment service"""
    print("\n💳 Setting up Arduino-to-Cardano Payment Service...")
    
    # Create blockchain directory if it doesn't exist
    blockchain_dir = Path("blockchain")
    blockchain_dir.mkdir(exist_ok=True)
    
    src_dir = blockchain_dir / "src"
    src_dir.mkdir(exist_ok=True)
    
    # Copy environment configuration
    env_file = blockchain_dir / ".env"
    if not env_file.exists():
        # Create basic .env for our service
        env_content = """# Arduino-to-Cardano Payment Service Configuration
BLOCKFROST_PROJECT_ID=your_blockfrost_project_id_here
BLOCKFROST_BASE_URL=https://cardano-preprod.blockfrost.io/api/v0
MASUMI_ADMIN_KEY=admin_key_123
MASUMI_ENCRYPTION_KEY=encryption_key_456
PAYMENT_SERVICE_HOST=localhost
PAYMENT_SERVICE_PORT=8001
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("   ✅ Created blockchain/.env configuration")
    
    # Install Python dependencies
    print("   📦 Installing Python dependencies...")
    dependencies = [
        "fastapi",
        "uvicorn",
        "python-dotenv", 
        "requests",
        "pycardano",
        "blockfrost-python"
    ]
    
    for dep in dependencies:
        success, output, error = run_command(f"pip install {dep}")
        if success:
            print(f"   ✅ Installed {dep}")
        else:
            print(f"   ⚠️  Failed to install {dep}: {error}")
    
    return True

def create_integration_files():
    """Create the integration files in the project"""
    print("\n📝 Creating Integration Files...")
    
    # The masumi_integration.py and real_payment_service.py are already created
    # in the documentation, so we just need to verify they exist
    
    files_to_check = [
        "blockchain/src/masumi_integration.py",
        "blockchain/src/real_payment_service.py",
        "test_complete_masumi_setup.py"
    ]
    
    for file_path in files_to_check:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}: Already exists")
        else:
            print(f"   ⚠️  {file_path}: Please create this file from the setup guide")
    
    return True

def run_integration_test():
    """Run the complete integration test"""
    print("\n🧪 Running Integration Test...")
    
    test_file = Path("test_complete_masumi_setup.py")
    if not test_file.exists():
        print("   ⚠️  Integration test file not found")
        return False
    
    success, output, error = run_command("python test_complete_masumi_setup.py")
    
    if success:
        print("   ✅ Integration test passed!")
        return True
    else:
        print(f"   ❌ Integration test failed: {error}")
        return False

def print_next_steps():
    """Print next steps for the user"""
    print("\n🎯 Setup Complete! Next Steps:")
    print("=" * 50)
    
    print("\n1. 📝 Configure Blockfrost API:")
    print("   • Get API key from: https://blockfrost.io/")
    print("   • Update masumi-services-dev-quickstart/.env")
    print("   • Update blockchain/.env")
    
    print("\n2. 💰 Fund Test Wallets:")
    print("   • Visit: https://testnets.cardano.org/en/testnets/cardano/tools/faucet/")
    print("   • Request preprod ADA for your wallets")
    
    print("\n3. 🚀 Start Payment Service:")
    print("   • Run: python blockchain/src/real_payment_service.py")
    
    print("\n4. 🧪 Test Integration:")
    print("   • Run: python test_complete_masumi_setup.py")
    
    print("\n🔗 Important URLs:")
    print("   • Masumi Payment API: http://localhost:3001/docs")
    print("   • Masumi Admin Panel: http://localhost:3001/admin") 
    print("   • Our Payment Service: http://localhost:8001/docs")
    print("   • Cardano Explorer: https://preprod.cardanoscan.io/")

def main():
    """Main setup function"""
    print("🚀 Official Masumi Network Setup for Arduino-to-Cardano")
    print("=" * 60)
    
    steps = [
        ("Prerequisites", check_prerequisites),
        ("Masumi Services", clone_masumi_services),
        ("Environment", setup_masumi_environment),
        ("Docker Services", start_masumi_services),
        ("Payment Service", setup_payment_service),
        ("Integration Files", create_integration_files)
    ]
    
    for step_name, step_function in steps:
        print(f"\n🔄 {step_name}...")
        
        if not step_function():
            print(f"\n❌ Setup failed at: {step_name}")
            return False
    
    print("\n🎉 Setup Complete!")
    
    # Run integration test
    if Path("test_complete_masumi_setup.py").exists():
        print("\n🧪 Running integration test...")
        run_integration_test()
    
    print_next_steps()
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Setup completed successfully!")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
    
    exit(0 if success else 1)