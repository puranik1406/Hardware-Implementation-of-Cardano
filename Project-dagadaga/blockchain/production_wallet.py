"""
PRODUCTION-READY ADA WALLET & TRANSFER SYSTEM
This script creates a working wallet and handles ADA transfers reliably
"""

import json
from pycardano import *

def create_production_wallet():
    """Create a production-ready wallet with proper key files"""
    
    print("=== CREATING PRODUCTION WALLET ===")
    
    # Generate a new payment signing key
    payment_signing_key = PaymentSigningKey.generate()
    payment_verification_key = payment_signing_key.to_verification_key()
    
    # Create testnet address
    address = Address(payment_part=payment_verification_key.hash(), network=Network.TESTNET)
    
    print(f"✅ Wallet generated successfully!")
    print(f"Address: {address.encode()}")
    print(f"Key Hash: {payment_verification_key.hash().to_primitive().hex()}")
    print()
    
    # Save signing key in proper Cardano CLI format
    signing_key_data = {
        "type": "PaymentSigningKeyShelley_ed25519",
        "description": "Payment Signing Key",
        "cborHex": f"5820{payment_signing_key.to_primitive().hex()}"
    }
    
    # Save verification key in proper Cardano CLI format
    verification_key_data = {
        "type": "PaymentVerificationKeyShelley_ed25519", 
        "description": "Payment Verification Key",
        "cborHex": f"5820{payment_verification_key.to_primitive().hex()}"
    }
    
    # Write key files
    with open("wallet.skey", "w") as f:
        json.dump(signing_key_data, f, indent=2)
    
    with open("wallet.vkey", "w") as f:
        json.dump(verification_key_data, f, indent=2)
    
    print("✅ Key files saved:")
    print("- wallet.skey (signing key)")
    print("- wallet.vkey (verification key)")
    print()
    
    return payment_signing_key, address

def load_wallet_from_file():
    """Load wallet from saved key file"""
    
    try:
        with open("wallet.skey", "r") as f:
            key_data = json.load(f)
        
        # Extract private key from CBOR hex
        cbor_hex = key_data["cborHex"]
        if cbor_hex.startswith("5820"):
            private_key_bytes = bytes.fromhex(cbor_hex[4:])
        else:
            private_key_bytes = bytes.fromhex(cbor_hex)
        
        # Create signing key
        signing_key = PaymentSigningKey(private_key_bytes)
        verification_key = signing_key.to_verification_key()
        address = Address(payment_part=verification_key.hash(), network=Network.TESTNET)
        
        return signing_key, address
        
    except Exception as e:
        print(f"Error loading wallet: {e}")
        return None, None

def check_wallet_balance(address_str):
    """Check wallet balance using BlockFrost"""
    
    try:
        context = BlockFrostChainContext(
            project_id="preprod7EWE9EhYgcZ2SQxz9w4HafrCwtK7yTDm",
            network=Network.TESTNET
        )
        
        utxos = context.utxos(address_str)
        total_lovelace = sum([utxo.output.amount.coin for utxo in utxos])
        total_ada = total_lovelace / 1_000_000
        
        return total_ada, len(utxos), context
        
    except Exception as e:
        print(f"Error checking balance: {e}")
        return 0, 0, None

def execute_ada_transfer(signing_key, sender_address, recipient_address, amount_ada, context):
    """Execute ADA transfer and return transaction hash"""
    
    try:
        amount_lovelace = int(amount_ada * 1_000_000)
        
        print(f"Building transaction...")
        print(f"From: {sender_address}")
        print(f"To: {recipient_address}")
        print(f"Amount: {amount_ada} ADA ({amount_lovelace} lovelace)")
        
        # Create transaction builder
        builder = TransactionBuilder(context)
        
        # Add sender address as input source
        builder.add_input_address(Address.decode(sender_address))
        
        # Add output to recipient
        builder.add_output(TransactionOutput(
            address=Address.decode(recipient_address),
            amount=Value(coin=amount_lovelace)
        ))
        
        # Build and sign transaction
        signed_tx = builder.build_and_sign([signing_key], change_address=Address.decode(sender_address))
        
        print("Submitting transaction to blockchain...")
        tx_hash = context.submit_tx(signed_tx)
        
        return tx_hash
        
    except Exception as e:
        print(f"Transfer failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function - create wallet or use existing one"""
    
    # Check if wallet already exists
    signing_key, address = load_wallet_from_file()
    
    if signing_key is None:
        # Create new wallet
        signing_key, address = create_production_wallet()
    else:
        print("=== LOADING EXISTING WALLET ===")
        print(f"Address: {address.encode()}")
        print()
    
    # Check balance
    print("Checking wallet balance...")
    balance, utxo_count, context = check_wallet_balance(address.encode())
    print(f"Balance: {balance:.6f} ADA")
    print(f"UTXOs: {utxo_count}")
    print()
    
    if balance >= 2.0:
        print("✅ Wallet has sufficient funds!")
        
        # Execute transfer
        recipient = "addr_test1qpxuephf94vaxsw5fce26x78z8qms8qv4sykannc5m2szvelt7hxg6m564ncm4mc4qn6dykpf2ah85l77xwyldngeuvsv7nfdp"
        
        print("Executing ADA transfer...")
        tx_hash = execute_ada_transfer(
            signing_key=signing_key,
            sender_address=address.encode(),
            recipient_address=recipient,
            amount_ada=2.0,
            context=context
        )
        
        if tx_hash:
            print("🎉 SUCCESS!")
            print(f"Transaction Hash: {tx_hash}")
            print(f"Sender: {address.encode()}")
            print(f"Recipient: {recipient}")
            print(f"Amount: 2.0 ADA")
        else:
            print("❌ Transfer failed")
            
    else:
        print("❌ Wallet needs funding")
        print()
        print("TO FUND YOUR WALLET:")
        print("1. Go to: https://docs.cardano.org/cardano-testnet/tools/faucet/")
        print("2. Or: https://testnets.cardano.org/en/testnets/cardano/tools/faucet/")
        print(f"3. Send test ADA to: {address.encode()}")
        print()
        print("After funding, run this script again to execute the transfer!")

if __name__ == "__main__":
    main()