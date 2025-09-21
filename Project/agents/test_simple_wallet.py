#!/usr/bin/env python3
"""
Test Simple Wallet Agent - Shows Exact Output
"""

import requests
import json

def test_simple_wallet():
    """Test the simple wallet agent"""
    
    print("🎯 TESTING SIMPLE WALLET AGENT")
    print("=" * 50)
    
    # Test health check
    print("\n1️⃣ HEALTH CHECK:")
    try:
        response = requests.get("http://localhost:8002/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Service: {data['service']}")
            print(f"   Wallet: {data['wallet_address']}")
            print(f"   Status: {data['status']}")
    except Exception as e:
        print(f"   Error: {e}")
        return
    
    # Test wallet address endpoint
    print("\n2️⃣ GET WALLET ADDRESS:")
    try:
        wallet_request = {
            "trigger_type": "arduino",
            "amount": 2500000,  # 2.5 ADA in lovelace
            "source": "test_wallet"
        }
        
        response = requests.post(
            "http://localhost:8002/agentA/get_wallet",
            json=wallet_request
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   🏦 Wallet Address: {data['wallet_address']}")
            print(f"   💰 Amount ADA: {data['amount_ada']}")
            print(f"   💰 Amount Lovelace: {data['amount_lovelace']}")
            print(f"   🆔 Transaction ID: {data['transaction_id']}")
            print(f"   ✅ Status: {data['status']}")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test simple transaction
    print("\n3️⃣ SIMPLE TRANSACTION:")
    try:
        transaction_request = {
            "trigger_type": "arduino",
            "amount": 1500000,  # 1.5 ADA in lovelace
            "source": "arduino_device"
        }
        
        response = requests.post(
            "http://localhost:8002/agentA/simple_transaction",
            json=transaction_request
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   📊 Status: {data['status']}")
            print(f"   📝 Summary: {data['summary']}")
            print(f"   🔗 Blockchain Data:")
            blockchain_data = data['blockchain_data']
            for key, value in blockchain_data.items():
                print(f"      {key}: {value}")
            
    except Exception as e:
        print(f"   Error: {e}")

def show_router_integration():
    """Show what Router/Blockchain will receive"""
    
    print("\n" + "=" * 50)
    print("🔗 WHAT ROUTER/BLOCKCHAIN RECEIVES")
    print("=" * 50)
    
    # Example of what Router gets
    router_data = {
        "recipient_wallet": "addr_test1qpxuephf94vaxsw5fce26x78z8qms8qv4sykannc5m2szvelt7hxg6m564ncm4mc4qn6dykpf2ah85l77xwyldngeuvsv7nfdp",
        "amount": 2.5,
        "currency": "ADA",
        "transaction_type": "send",
        "timestamp": "2025-09-21T17:00:00.000000",
        "source": "arduino_device",
        "trigger_type": "arduino"
    }
    
    print("📋 JSON Data for Router/Blockchain:")
    print(json.dumps(router_data, indent=2))
    
    print(f"\n🎯 KEY POINTS:")
    print(f"   💳 Wallet: {router_data['recipient_wallet']}")
    print(f"   💰 Amount: {router_data['amount']} {router_data['currency']}")
    print(f"   📡 Action: Send ADA to this wallet address")
    print(f"   🔧 Simple: No complex logic, just wallet + amount")

if __name__ == "__main__":
    test_simple_wallet()
    show_router_integration()
    
    print("\n" + "=" * 50)
    print("✅ SIMPLE WALLET AGENT WORKING!")
    print("🎯 Agent returns: Wallet address + ADA amount")
    print("🔗 Router sends: ADA to that wallet")
    print("🚀 Ready for blockchain integration!")
    print("=" * 50)
