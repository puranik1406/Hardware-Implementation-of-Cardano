#!/usr/bin/env python3
"""
Setup script for Cardano-Arduino-AI Hackathon Project
Automatically installs dependencies and sets up the environment
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description, check=True):
    """Run a command and handle errors"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def setup_virtual_environment():
    """Set up Python virtual environment"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    # Create virtual environment
    if not run_command(f"{sys.executable} -m venv venv", "Creating virtual environment"):
        return False
    
    return True

def activate_virtual_environment():
    """Get activation command for virtual environment"""
    system = platform.system().lower()
    
    if system == "windows":
        return "venv\\Scripts\\activate"
    else:
        return "source venv/bin/activate"

def install_dependencies():
    """Install Python dependencies"""
    # Determine pip executable
    system = platform.system().lower()
    if system == "windows":
        pip_cmd = "venv\\Scripts\\pip"
    else:
        pip_cmd = "venv/bin/pip"
    
    # Upgrade pip first
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies"):
        return False
    
    return True

def setup_environment_file():
    """Set up environment configuration"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if env_example.exists():
        # Copy example to .env
        try:
            import shutil
            shutil.copy(env_example, env_file)
            print("✅ Created .env file from .env.example")
            print("📝 Please update .env file with your actual configuration values")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("❌ .env.example file not found")
        return False

def check_optional_tools():
    """Check for optional tools and provide setup instructions"""
    print("\n🔍 Checking optional tools...")
    
    # Check for Arduino IDE
    arduino_paths = [
        "C:\\Program Files\\Arduino\\arduino.exe",
        "C:\\Program Files (x86)\\Arduino\\arduino.exe",
        "/Applications/Arduino.app",
        "/usr/bin/arduino"
    ]
    
    arduino_found = False
    for path in arduino_paths:
        if Path(path).exists():
            print("✅ Arduino IDE found")
            arduino_found = True
            break
    
    if not arduino_found:
        print("⚠️ Arduino IDE not found")
        print("   Download from: https://www.arduino.cc/en/software")
    
    # Check for Git
    if run_command("git --version", "Checking Git", check=False):
        print("✅ Git found")
    else:
        print("⚠️ Git not found - recommended for version control")
    
    # Check for Node.js (for potential web interface)
    if run_command("node --version", "Checking Node.js", check=False):
        print("✅ Node.js found")
    else:
        print("⚠️ Node.js not found - optional for web development")

def create_directories():
    """Create necessary directories"""
    directories = [
        "logs",
        "data",
        "backups",
        "tests/logs",
        "docs/generated"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Created necessary directories")

def setup_logging():
    """Set up logging configuration"""
    log_config = """
[loggers]
keys=root,cardano_arduino

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=INFO
handlers=consoleHandler

[logger_cardano_arduino]
level=INFO
handlers=consoleHandler,fileHandler
qualname=cardano_arduino
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=simpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=INFO
formatter=simpleFormatter
args=('logs/system.log',)

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
"""
    
    try:
        with open("logging.conf", "w") as f:
            f.write(log_config.strip())
        print("✅ Created logging configuration")
    except Exception as e:
        print(f"⚠️ Failed to create logging config: {e}")

def run_basic_tests():
    """Run basic import tests"""
    print("\n🧪 Running basic tests...")
    
    test_imports = [
        "fastapi",
        "uvicorn", 
        "flask",
        "requests",
        "pydantic",
        "dotenv",
        "serial"
    ]
    
    failed_imports = []
    
    for module in test_imports:
        try:
            if module == "dotenv":
                __import__("dotenv")
            elif module == "serial":
                __import__("serial")
            else:
                __import__(module)
            print(f"✅ {module} import successful")
        except ImportError as e:
            print(f"❌ {module} import failed: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed imports: {failed_imports}")
        print("Try running: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All imports successful")
        return True

def display_next_steps():
    """Display next steps for the user"""
    activate_cmd = activate_virtual_environment()
    
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    print("\n📋 Next Steps:")
    print(f"1. Activate virtual environment: {activate_cmd}")
    print("2. Update .env file with your configuration")
    print("3. Connect your Arduino devices")
    print("4. Upload Arduino sketches:")
    print("   • src/arduino/arduino_a.ino → First Arduino")
    print("   • src/arduino/arduino_b.ino → Second Arduino")
    print("5. Start the system: python main.py")
    print("\n🔧 Configuration:")
    print("• Update BLOCKFROST_PROJECT_ID in .env for real blockchain")
    print("• Update ARDUINO_A_PORT and ARDUINO_B_PORT for your setup")
    print("• Set MOCK_MODE=false for real transactions")
    print("\n📚 Documentation:")
    print("• README.md - Complete project overview")
    print("• docs/ - Detailed documentation")
    print("• Check system status: http://localhost:8003/status")
    print("\n💡 Test Commands:")
    print("• python main.py - Start complete system")
    print("• python -m pytest tests/ - Run tests")
    print("• curl http://localhost:8000/test_payment - Test payment")
    print("="*60)

def main():
    """Main setup function"""
    print("🚀 Cardano-Arduino-AI Hackathon Setup")
    print("=====================================")
    print("This script will set up your development environment.\n")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check if we're in the right directory
    if not Path("requirements.txt").exists():
        print("❌ Error: Please run this script from the project root directory")
        print("   (where requirements.txt is located)")
        sys.exit(1)
    
    # Setup steps
    setup_steps = [
        ("Virtual Environment", setup_virtual_environment),
        ("Dependencies", install_dependencies),
        ("Environment File", setup_environment_file),
        ("Directories", create_directories),
        ("Logging", setup_logging),
        ("Basic Tests", run_basic_tests)
    ]
    
    failed_steps = []
    
    for step_name, step_function in setup_steps:
        if not step_function():
            failed_steps.append(step_name)
    
    # Check optional tools
    check_optional_tools()
    
    # Display results
    if failed_steps:
        print(f"\n❌ Setup completed with errors in: {', '.join(failed_steps)}")
        print("Please check the error messages above and retry.")
        sys.exit(1)
    else:
        print("\n✅ Setup completed successfully!")
        display_next_steps()

if __name__ == "__main__":
    main()