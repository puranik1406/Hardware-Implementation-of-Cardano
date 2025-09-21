#!/usr/bin/env python3
"""
Final Test - Simple and Clean
"""

import requests

def test_final_agent():
    print("🎯 FINAL TEST - SIMPLE WALLET AGENT")
    print("=" * 40)
    
    # Health check
    response = requests.get("http://localhost:8002/")
    print(f"Health: {response.json()}")
    
    # Get wallet
    data = {"amount": 2500000}  # 2.5 ADA
    response = requests.post("http://localhost:8002/wallet", json=data)
    result = response.json()
    
    print(f"\n✅ FINAL OUTPUT:")
    print(f"   Wallet: {result['wallet_address']}")
    print(f"   Amount: {result['amount_ada']} ADA")
    print(f"   Action: {result['action']}")
    
    print(f"\n🔗 This goes to Router/Blockchain:")
    print(f"   Send {result['amount_ada']} ADA")
    print(f"   To: {result['wallet_address']}")

if __name__ == "__main__":
    test_final_agent()
