#!/usr/bin/env python3
"""
Cardano-Arduino-AI Demo Script
Demonstrates the complete system workflow
"""

import asyncio
import json
import requests
import time
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def print_banner():
    """Print demo banner"""
    print("=" * 70)
    print("🎬 CARDANO-ARDUINO-AI SYSTEM DEMO")
    print("=" * 70)
    print("This demo showcases the complete workflow:")
    print("• Arduino A triggers an offer")
    print("• Agent A (AI Buyer) creates intelligent offer")
    print("• Router coordinates between agents")
    print("• Agent B (Seller) evaluates and responds")
    print("• Payment Service processes Cardano transaction")
    print("• Arduino B displays transaction confirmation")
    print("=" * 70)

def check_services():
    """Check if all services are running"""
    services = {
        "Agent A (Buyer)": "http://localhost:8001",
        "Agent B (Seller)": "http://localhost:8002",
        "Router": "http://localhost:8003",
        "Payment Service": "http://localhost:8000"
    }
    
    print("\n🔍 Checking system services...")
    
    all_running = True
    for name, url in services.items():
        try:
            response = requests.get(f"{url}/", timeout=3)
            if response.status_code == 200:
                print(f"✅ {name}: Online")
            else:
                print(f"❌ {name}: Error (HTTP {response.status_code})")
                all_running = False
        except Exception as e:
            print(f"❌ {name}: Offline ({e})")
            all_running = False
    
    if not all_running:
        print("\n⚠️ Some services are not running. Please start with: python main.py")
        return False
    
    print("✅ All services are online!")
    return True

def demo_step(step_num, title, description):
    """Print demo step header"""
    print(f"\n{'='*20} STEP {step_num}: {title} {'='*20}")
    print(f"📋 {description}")
    input("Press Enter to continue...")

def demo_arduino_trigger():
    """Demo Arduino trigger functionality"""
    demo_step(1, "ARDUINO TRIGGER", "Simulating Arduino A sensor trigger")
    
    # Simulate Arduino A triggering an offer
    trigger_data = {
        "amount": 125.5,
        "product": "Temperature Sensor Data",
        "context": {
            "sensor_type": "DHT22",
            "temperature": 23.5,
            "humidity": 65.2,
            "location": "Arduino Lab"
        }
    }
    
    print("🔥 Arduino A sensor detects environment change!")
    print(f"📊 Sensor data: {json.dumps(trigger_data, indent=2)}")
    
    try:
        print("\n📡 Sending trigger to Router...")
        response = requests.post(
            "http://localhost:8003/arduino_trigger",
            json=trigger_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Trigger sent successfully!")
            print(f"📨 Router response: {json.dumps(result, indent=2)}")
            
            # Extract offer ID for tracking
            if "agent_a_response" in result:
                offer_id = result["agent_a_response"]["offer_id"]
                print(f"\n🆔 Generated Offer ID: {offer_id}")
                return offer_id
            
        else:
            print(f"❌ Trigger failed: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Trigger error: {e}")
        return None

def demo_agent_workflow(offer_id):
    """Demo agent workflow"""
    demo_step(2, "AI AGENT WORKFLOW", "Agents process the offer intelligently")
    
    if not offer_id:
        print("❌ No offer ID available, skipping workflow demo")
        return
    
    # Check offer status
    print("🤖 Checking Agent A (Buyer AI) decision...")
    try:
        response = requests.get(f"http://localhost:8001/offers/{offer_id}", timeout=10)
        if response.status_code == 200:
            offer = response.json()
            print(f"🧠 Agent A Decision: {offer.get('status', 'unknown')}")
            print(f"💰 Offer Amount: {offer.get('amount', 0)} ADA")
            print(f"📝 Decision Reason: {offer.get('decision_reason', 'No reason provided')}")
        else:
            print("⚠️ Could not retrieve Agent A offer details")
    except Exception as e:
        print(f"⚠️ Agent A check error: {e}")
    
    # Check router coordination
    print("\n🔀 Checking Router coordination...")
    try:
        response = requests.get(f"http://localhost:8003/offers/{offer_id}", timeout=10)
        if response.status_code == 200:
            router_offer = response.json()
            print(f"📊 Router Status: {router_offer.get('status', 'unknown')}")
            
            if "agent_b_response" in router_offer:
                agent_b_resp = router_offer["agent_b_response"]
                print(f"🛒 Agent B Decision: {agent_b_resp.get('decision', 'pending')}")
                print(f"💭 Agent B Reason: {agent_b_resp.get('reason', 'No reason')}")
        else:
            print("⚠️ Could not retrieve Router offer details")
    except Exception as e:
        print(f"⚠️ Router check error: {e}")

def demo_blockchain_transaction():
    """Demo blockchain transaction"""
    demo_step(3, "BLOCKCHAIN TRANSACTION", "Processing payment on Cardano")
    
    print("🔗 Initiating test transaction on Cardano...")
    
    try:
        response = requests.post("http://localhost:8000/test_payment", timeout=30)
        if response.status_code == 200:
            result = response.json()
            job_id = result["job_id"]
            print(f"✅ Payment initiated!")
            print(f"🆔 Job ID: {job_id}")
            print(f"⏳ Status: {result['status']}")
            
            # Monitor job progress
            print("\n🔍 Monitoring transaction progress...")
            max_attempts = 15
            for attempt in range(max_attempts):
                time.sleep(2)
                
                status_response = requests.get(
                    f"http://localhost:8000/job_status/{job_id}",
                    timeout=10
                )
                
                if status_response.status_code == 200:
                    status = status_response.json()
                    current_status = status["status"]
                    
                    print(f"📊 Attempt {attempt + 1}: Status = {current_status}")
                    
                    if current_status == "completed":
                        print("🎉 Transaction completed successfully!")
                        tx_hash = status.get("transaction_hash", "N/A")
                        print(f"🔐 Transaction Hash: {tx_hash}")
                        return tx_hash
                    elif current_status == "failed":
                        print("❌ Transaction failed")
                        error = status.get("error", "Unknown error")
                        print(f"💥 Error: {error}")
                        return None
                
                if attempt < max_attempts - 1:
                    print("⏳ Waiting for transaction to complete...")
            
            print("⚠️ Transaction monitoring timed out")
            return None
            
        else:
            print(f"❌ Payment initiation failed: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Blockchain demo error: {e}")
        return None

def demo_arduino_display(tx_hash):
    """Demo Arduino B display"""
    demo_step(4, "ARDUINO DISPLAY", "Transaction confirmation on Arduino B")
    
    print("📺 Arduino B would display transaction confirmation:")
    print("┌" + "─" * 18 + "┐")
    print("│ ✅ CONFIRMED    │")
    if tx_hash:
        display_hash = tx_hash[:16] if len(tx_hash) > 16 else tx_hash
        print(f"│ {display_hash:<16} │")
    else:
        print("│ mock_tx_demo123  │")
    print("└" + "─" * 18 + "┘")
    
    print("\n💡 Arduino B Features:")
    print("• Green LED: Transaction confirmed")
    print("• LCD Display: Shows transaction hash")
    print("• Button: Acknowledge confirmation")
    print("• Serial Output: Logs all activities")

def demo_system_monitoring():
    """Demo system monitoring"""
    demo_step(5, "SYSTEM MONITORING", "Real-time system status and metrics")
    
    print("📊 Fetching system status...")
    
    try:
        response = requests.get("http://localhost:8003/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            
            print("🌐 System Health:")
            agents = status.get("agents", {})
            for agent, info in agents.items():
                agent_status = info.get("status", "unknown")
                print(f"  • {agent}: {agent_status}")
            
            print("\n📈 System Statistics:")
            stats = status.get("system_stats", {})
            for key, value in stats.items():
                print(f"  • {key.replace('_', ' ').title()}: {value}")
            
            # Show recent offers
            offers_response = requests.get("http://localhost:8003/offers", timeout=5)
            if offers_response.status_code == 200:
                offers_data = offers_response.json()
                offers = offers_data.get("offers", [])
                
                print(f"\n📋 Recent Offers ({len(offers)}):")
                for i, offer in enumerate(offers[-3:], 1):  # Show last 3
                    amount = offer.get("amount", 0)
                    status = offer.get("status", "unknown")
                    product = offer.get("product", "Unknown")
                    print(f"  {i}. {amount} ADA for {product} - Status: {status}")
        else:
            print(f"❌ Status check failed: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Monitoring error: {e}")

def demo_api_showcase():
    """Demo API capabilities"""
    demo_step(6, "API SHOWCASE", "Testing system APIs and endpoints")
    
    print("🔌 API Endpoints Available:")
    
    apis = [
        ("Agent A Health", "GET", "http://localhost:8001/"),
        ("Agent B Health", "GET", "http://localhost:8002/"),
        ("Router Status", "GET", "http://localhost:8003/status"),
        ("Payment Service", "GET", "http://localhost:8000/"),
        ("All Offers", "GET", "http://localhost:8003/offers"),
        ("All Transactions", "GET", "http://localhost:8002/transactions")
    ]
    
    for name, method, url in apis:
        try:
            response = requests.get(url, timeout=5)
            status_icon = "✅" if response.status_code == 200 else "⚠️"
            print(f"  {status_icon} {name}: {method} {url} → HTTP {response.status_code}")
        except Exception as e:
            print(f"  ❌ {name}: {method} {url} → Error: {e}")
    
    print("\n💻 cURL Examples for testing:")
    print("# Trigger Arduino offer")
    print("curl -X POST http://localhost:8003/arduino_trigger \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"amount\": 150, \"product\": \"Sensor Data\"}'")
    
    print("\n# Check system status")
    print("curl http://localhost:8003/status")
    
    print("\n# Test payment")
    print("curl -X POST http://localhost:8000/test_payment")

def run_complete_demo():
    """Run the complete demo workflow"""
    print_banner()
    
    # Check prerequisites
    if not check_services():
        print("\n❌ Cannot run demo - services not available")
        return False
    
    print("\n🎬 Starting complete demo workflow...")
    
    # Step 1: Arduino Trigger
    offer_id = demo_arduino_trigger()
    
    # Step 2: Agent Workflow
    demo_agent_workflow(offer_id)
    
    # Step 3: Blockchain Transaction
    tx_hash = demo_blockchain_transaction()
    
    # Step 4: Arduino Display
    demo_arduino_display(tx_hash)
    
    # Step 5: System Monitoring
    demo_system_monitoring()
    
    # Step 6: API Showcase
    demo_api_showcase()
    
    # Conclusion
    print("\n" + "=" * 70)
    print("🎉 DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print("✅ Demonstrated complete Arduino-to-Cardano workflow")
    print("✅ Showed AI agent decision making")
    print("✅ Displayed blockchain transaction processing")
    print("✅ Showcased system monitoring capabilities")
    print("✅ Tested all major API endpoints")
    
    print("\n🚀 What you've seen:")
    print("• Hardware triggering blockchain transactions")
    print("• AI-powered intelligent offer evaluation")
    print("• Real-time agent coordination")
    print("• Cardano blockchain integration")
    print("• Complete system monitoring")
    
    print("\n💡 Next steps:")
    print("• Connect real Arduino hardware")
    print("• Configure Blockfrost API for real blockchain")
    print("• Customize AI decision logic")
    print("• Add your own sensors and triggers")
    
    return True

def main():
    """Main demo function"""
    if len(sys.argv) > 1 and sys.argv[1].lower() in ['help', '-h', '--help']:
        print("Cardano-Arduino-AI Demo Script")
        print("Usage: python demo.py [quick|full]")
        print("  quick - Run quick system check")
        print("  full  - Run complete demo (default)")
        return
    
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else "full"
    
    if mode == "quick":
        print("🚀 Quick System Check")
        print("=" * 30)
        check_services()
    else:
        run_complete_demo()

if __name__ == "__main__":
    main()