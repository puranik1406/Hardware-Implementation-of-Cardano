#!/usr/bin/env python3
"""
Show Exact Blockchain Output Format
Demonstrates what Agent A sends to Router/Blockchain
"""

import json
from datetime import datetime

def show_blockchain_output():
    """Show exact format sent to blockchain"""
    
    print("🔗 BLOCKCHAIN OUTPUT FORMAT")
    print("=" * 60)
    
    # 1. INPUT TO AGENT A (from Arduino/User)
    print("\n1️⃣ INPUT TO AGENT A:")
    print("   📡 Endpoint: POST http://localhost:8002/agentA/send_to_router")
    print("   📝 Content-Type: application/json")
    
    input_data = {
        "trigger_type": "arduino",
        "amount": 2500000,  # lovelace (2.5 ADA)
        "context": {
            "button_type": "button_1",
            "priority": "high",
            "device_id": "arduino_001"
        },
        "source": "arduino_device",
        "timestamp": datetime.now().isoformat()
    }
    
    print("   📋 JSON Payload:")
    print(json.dumps(input_data, indent=4))
    
    # 2. AGENT A PROCESSING
    print("\n2️⃣ AGENT A PROCESSING:")
    print("   🤖 Bedrock Agent ID: FTQPCW1EV3")
    print("   🧠 AI Decision: Analyze trigger → Accept/Reject")
    print("   💱 Currency Conversion: 2500000 lovelace → 2.5 ADA")
    
    # 3. OUTPUT TO ROUTER/BLOCKCHAIN
    print("\n3️⃣ OUTPUT TO ROUTER/BLOCKCHAIN:")
    print("   📡 Endpoint: POST http://localhost:5000/send_offer")
    print("   📝 Content-Type: application/json")
    print("   🎯 Destination: Vansh's Router → Dhanush's Blockchain")
    
    blockchain_output = {
        "from_agent": "agent_a",
        "to_agent": "agent_b",
        "amount": 2.5,  # ADA (converted from lovelace)
        "currency": "ADA",
        "description": "Agent A offer from arduino",
        "timestamp": datetime.now().isoformat() + "Z",
        "metadata": {
            "arduino_trigger": True,
            "button_type": "button_1",
            "priority": "high",
            "source": "arduino_device",
            "original_amount_lovelace": 2500000,
            "agent_decision": "accepted",
            "bedrock_agent_id": "FTQPCW1EV3"
        }
    }
    
    print("   📋 JSON Payload to Blockchain:")
    print(json.dumps(blockchain_output, indent=4))
    
    # 4. EXPECTED BLOCKCHAIN RESPONSE
    print("\n4️⃣ EXPECTED BLOCKCHAIN RESPONSE:")
    print("   📡 From: Dhanush's Blockchain Implementation")
    print("   📝 Content-Type: application/json")
    
    blockchain_response = {
        "success": True,
        "transaction_id": "tx_1a2b3c4d5e6f7g8h9i0j",
        "block_hash": "block_abc123def456",
        "amount_processed": 2.5,
        "currency": "ADA",
        "fee": 0.17,  # ADA
        "confirmation_time": "2025-09-21T16:45:30Z",
        "network": "cardano_testnet",
        "from_address": "addr1_agent_a_wallet",
        "to_address": "addr1_agent_b_wallet"
    }
    
    print("   📋 Expected JSON Response:")
    print(json.dumps(blockchain_response, indent=4))
    
    # 5. FINAL RESPONSE TO USER
    print("\n5️⃣ FINAL RESPONSE TO USER:")
    print("   📡 From: Agent A back to User/Arduino")
    print("   📝 Content-Type: application/json")
    
    final_response = {
        "status": "sent_to_router",
        "agent_decision": "accepted",
        "amount_ada": 2.5,
        "amount_lovelace": 2500000,
        "router_response": blockchain_response,
        "timestamp": datetime.now().isoformat(),
        "flow_summary": {
            "step_1": "Arduino trigger received",
            "step_2": "Bedrock AI decision made",
            "step_3": "Sent to Router for blockchain processing",
            "step_4": "Blockchain transaction completed"
        }
    }
    
    print("   📋 Final JSON Response:")
    print(json.dumps(final_response, indent=4))

def show_server_details():
    """Show server technical details"""
    
    print("\n" + "=" * 60)
    print("🖥️ SERVER TECHNICAL DETAILS")
    print("=" * 60)
    
    print("\n📡 AGENT A SERVER:")
    print("   🔗 URL: http://localhost:8002")
    print("   🐍 Framework: FastAPI with Uvicorn")
    print("   🚀 Status: ASGI Server")
    print("   📝 Logs: Console + File logging")
    print("   🔧 Config: Production ready")
    
    print("\n📡 ROUTER SERVER (Vansh):")
    print("   🔗 URL: http://localhost:5000/send_offer")
    print("   🎯 Purpose: Payment processing gateway")
    print("   🔗 Connects to: Dhanush's blockchain")
    
    print("\n⛓️ BLOCKCHAIN (Dhanush):")
    print("   🌐 Network: Cardano (testnet/mainnet)")
    print("   💰 Currency: ADA")
    print("   🔗 Integration: Via Router service")
    print("   📊 Returns: Transaction ID, block hash, fees")

def show_call_parameters():
    """Show exact call parameters"""
    
    print("\n" + "=" * 60)
    print("📞 EXACT CALL PARAMETERS")
    print("=" * 60)
    
    print("\n🔥 CURL COMMAND TO TEST:")
    curl_command = '''curl -X POST http://localhost:8002/agentA/send_to_router \\
  -H "Content-Type: application/json" \\
  -d '{
    "trigger_type": "arduino",
    "amount": 2500000,
    "context": {
      "button_type": "button_1",
      "priority": "high"
    },
    "source": "test_blockchain"
  }'
'''
    print(curl_command)
    
    print("\n💻 POWERSHELL COMMAND:")
    ps_command = '''$data = @{
    trigger_type = "arduino"
    amount = 2500000
    context = @{
        button_type = "button_1"
        priority = "high"
    }
    source = "test_blockchain"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8002/agentA/send_to_router" -Method POST -ContentType "application/json" -Body $data
'''
    print(ps_command)
    
    print("\n🐍 PYTHON REQUEST:")
    python_code = '''import requests

data = {
    "trigger_type": "arduino",
    "amount": 2500000,
    "context": {
        "button_type": "button_1", 
        "priority": "high"
    },
    "source": "test_blockchain"
}

response = requests.post(
    "http://localhost:8002/agentA/send_to_router",
    json=data
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
'''
    print(python_code)

if __name__ == "__main__":
    show_blockchain_output()
    show_server_details()
    show_call_parameters()
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY")
    print("=" * 60)
    print("✅ Agent A converts lovelace → ADA")
    print("✅ Sends structured JSON to Router")
    print("✅ Router processes via Dhanush's blockchain")
    print("✅ Returns transaction details")
    print("✅ Complete audit trail maintained")
    print("\n🚀 Ready for blockchain integration!")
