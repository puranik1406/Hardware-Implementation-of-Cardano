#!/usr/bin/env python3
"""
Demo script showing the complete Agent B workflow
Simulates the entire process from offer to Arduino display
"""

import time
import json
from datetime import datetime

def simulate_router_offer():
    """Simulate Router sending an offer to Agent B"""
    print("📡 Router → Agent B: Sending offer...")
    
    offer = {
        "amount": 175.0,
        "product": "Premium Smart Widget",
        "buyer_address": "addr1q9test1234567890abcdef...",
        "buyer_id": "buyer_demo_001",
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"   Offer: ${offer['amount']} for {offer['product']}")
    return offer

def simulate_agent_b_decision(offer):
    """Simulate Agent B decision logic"""
    print("\n🤔 Agent B: Evaluating offer...")
    
    cost_threshold = 100.0
    amount = offer['amount']
    
    if amount >= cost_threshold:
        decision = "ACCEPT"
        print(f"   ✅ Decision: {decision} (${amount} >= ${cost_threshold})")
        
        # Simulate payment request
        print("   💳 Initiating payment...")
        tx_hash = f"mock_tx_{int(time.time())}_{amount}"
        print(f"   📝 Transaction Hash: {tx_hash}")
        
        return {
            "decision": decision,
            "tx_hash": tx_hash,
            "status": "payment_initiated"
        }
    else:
        decision = "REJECT"
        print(f"   ❌ Decision: {decision} (${amount} < ${cost_threshold})")
        return {
            "decision": decision,
            "status": "rejected"
        }

def simulate_payment_confirmation(tx_hash):
    """Simulate payment confirmation process"""
    print(f"\n⏳ Blockchain Service: Processing payment...")
    print(f"   Transaction: {tx_hash}")
    
    # Simulate processing time
    for i in range(3):
        print(f"   ⏳ Polling... attempt {i+1}/3")
        time.sleep(1)
    
    print(f"   ✅ Payment confirmed!")
    return True

def simulate_arduino_display(tx_hash):
    """Simulate Arduino B display"""
    print(f"\n📱 Arduino B Display:")
    print(f"   ┌─────────────────────────────┐")
    print(f"   │  ✅ CONFIRMED               │")
    print(f"   │  {tx_hash[:20]:<20} │")
    print(f"   └─────────────────────────────┘")
    print(f"   [LCD Display Updated]")
    print(f"   [Serial Monitor Logged]")

def run_demo():
    """Run the complete demo workflow"""
    print("🚀 Agent B - Seller Logic Demo")
    print("=" * 50)
    print("Simulating complete workflow from offer to Arduino display")
    print()
    
    # Step 1: Router sends offer
    offer = simulate_router_offer()
    
    # Step 2: Agent B makes decision
    result = simulate_agent_b_decision(offer)
    
    if result['decision'] == 'ACCEPT':
        # Step 3: Payment confirmation
        if simulate_payment_confirmation(result['tx_hash']):
            # Step 4: Arduino display
            simulate_arduino_display(result['tx_hash'])
            
            print(f"\n🎉 Workflow completed successfully!")
            print(f"   Transaction: {result['tx_hash']}")
            print(f"   Amount: ${offer['amount']}")
            print(f"   Product: {offer['product']}")
        else:
            print(f"\n❌ Payment confirmation failed")
    else:
        print(f"\n❌ Offer rejected - no payment initiated")
    
    print(f"\n📊 Demo Summary:")
    print(f"   - Agent B decision logic: ✅ Working")
    print(f"   - Payment simulation: ✅ Working") 
    print(f"   - Arduino display: ✅ Working")
    print(f"   - Complete workflow: ✅ Working")

def show_api_endpoints():
    """Show available API endpoints"""
    print(f"\n🔌 Agent B API Endpoints:")
    print(f"   GET  /health      - Health check")
    print(f"   POST /respond     - Receive offers from Router")
    print(f"   POST /confirm_tx  - Handle transaction confirmations")
    print(f"   GET  /status      - Get current status")
    print(f"   URL: http://localhost:5001")

def show_arduino_instructions():
    """Show Arduino B setup instructions"""
    print(f"\n🔧 Arduino B Setup:")
    print(f"   1. Open arduino_b.ino in Arduino IDE or Wokwi")
    print(f"   2. Upload to Arduino board")
    print(f"   3. Open Serial Monitor (9600 baud)")
    print(f"   4. Send transaction hash in format:")
    print(f"      tx_hash:CONFIRMED")
    print(f"   5. Watch LCD display update")

def main():
    """Main demo function"""
    print("🤖 Agent B & Arduino B - Complete Demo")
    print("=" * 60)
    
    # Run the demo workflow
    run_demo()
    
    # Show additional information
    show_api_endpoints()
    show_arduino_instructions()
    
    print(f"\n✨ Ready for integration with Router and Blockchain Service!")
    print(f"   Start Agent B: python start_agent_b.py")
    print(f"   Run tests: python test_agent_b.py")

if __name__ == "__main__":
    main()
