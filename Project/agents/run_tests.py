#!/usr/bin/env python3
"""
Test runner for Agent A service
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def start_service():
    """Start the Agent A service in background"""
    print("Starting Agent A service...")
    
    # Start service in background
    process = subprocess.Popen([
        sys.executable, "start_agent_a.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for service to start
    time.sleep(3)
    
    return process

def run_tests():
    """Run the test suite"""
    print("Running Agent A tests...")
    
    try:
        result = subprocess.run([
            sys.executable, "test_agent_a.py"
        ], capture_output=True, text=True)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"Test execution failed: {e}")
        return False

def main():
    """Main test runner"""
    print("Agent A Test Runner")
    print("=" * 50)
    
    # Change to agents directory
    agents_dir = Path(__file__).parent
    os.chdir(agents_dir)
    
    service_process = None
    
    try:
        # Start service
        service_process = start_service()
        
        # Run tests
        success = run_tests()
        
        if success:
            print("\n✅ All tests passed!")
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test runner failed: {e}")
        sys.exit(1)
    finally:
        # Clean up service
        if service_process:
            print("\nStopping service...")
            service_process.terminate()
            service_process.wait()

if __name__ == "__main__":
    main()

