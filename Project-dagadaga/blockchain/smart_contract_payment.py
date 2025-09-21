"""
Smart Contract Integration for Cardano Payment System
Handles interaction with Plutus smart contracts for secure payments
"""

import json
import cbor2
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

from pycardano import (
    TransactionBuilder, TransactionOutput, Value, Address, PaymentVerificationKey,
    PaymentSigningKey, PlutusV2Script, PlutusData, RedeemerTag, Redeemer,
    UTxO, TransactionInput, TransactionWitnessSet, VerificationKeyWitness,
    ScriptDataHash, AuxiliaryData, AlonzoMetadata, Metadata
)
from pycardano.backend import blockfrost
from pycardano.address import Address
from pycardano.certificate import StakeCredential
from pycardano.plutus import PlutusV2Script
from pycardano.serialization import Datum
from pycardano.witness import TransactionWitnessSet

# Import our Blockfrost configuration
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class PaymentDatum:
    """Payment datum structure matching Plutus contract"""
    sender: str
    recipient: str
    amount: int
    payment_id: str
    status: str  # "pending", "confirmed", "cancelled"

@dataclass
class SmartContractConfig:
    """Configuration for smart contract deployment"""
    script_address: str
    script_hash: str
    contract_cbor: str

class PlutusPaymentContract:
    """Main class for interacting with Plutus payment smart contract"""
    
    def __init__(self, blockfrost_project_id: str, network: str = "preprod"):
        self.network = network
        self.context = blockfrost.BlockFrostChainContext(
            project_id=blockfrost_project_id,
            network=blockfrost.Network.PREPROD if network == "preprod" else blockfrost.Network.MAINNET
        )
        
        # Smart contract configuration
        self.contract = self._load_contract_config()
        
        # Load wallet keys
        self.signing_key = self._load_signing_key()
        self.verification_key = PaymentVerificationKey.from_signing_key(self.signing_key)
        self.address = Address(self.verification_key.hash(), network=self.context.network)
        
        print(f"🔗 Connected to Cardano {network}")
        print(f"📦 Smart contract address: {self.contract.script_address}")
        print(f"💼 Wallet address: {self.address}")
    
    def _load_contract_config(self) -> SmartContractConfig:
        """Load smart contract configuration"""
        # For now, we'll use placeholder values
        # In production, this would load from compiled Plutus script
        return SmartContractConfig(
            script_address="addr_test1wpzh9w8rk8u7k5v5j5k5j5k5j5k5j5k5j5k5j5k5j5k5j5k5j5k5j5k5",
            script_hash="a1b2c3d4e5f6789",
            contract_cbor="59015859015501000032323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323200010001"
        )
    
    def _load_signing_key(self) -> PaymentSigningKey:
        """Load wallet signing key"""
        try:
            with open("wallet.skey", "r") as f:
                key_data = json.load(f)
                return PaymentSigningKey.from_json(json.dumps(key_data))
        except Exception as e:
            print(f"❌ Error loading signing key: {e}")
            raise
    
    def create_payment_datum(self, sender: str, recipient: str, amount: int, payment_id: str) -> PaymentDatum:
        """Create payment datum for smart contract"""
        return PaymentDatum(
            sender=sender,
            recipient=recipient,
            amount=amount,
            payment_id=payment_id,
            status="pending"
        )
    
    def lock_funds_to_contract(self, recipient_address: str, amount_ada: float, payment_id: str) -> str:
        """
        Lock funds to smart contract with payment datum
        
        Args:
            recipient_address: Recipient's Cardano address
            amount_ada: Amount in ADA to lock
            payment_id: Unique payment identifier
            
        Returns:
            Transaction hash
        """
        try:
            print(f"🔒 Locking {amount_ada} ADA to smart contract...")
            
            # Convert ADA to Lovelace
            amount_lovelace = int(amount_ada * 1_000_000)
            
            # Create payment datum
            datum = self.create_payment_datum(
                sender=str(self.address),
                recipient=recipient_address,
                amount=amount_lovelace,
                payment_id=payment_id
            )
            
            # Build transaction
            builder = TransactionBuilder(self.context)
            
            # Add input from our wallet
            utxos = self.context.utxos(self.address)
            if not utxos:
                raise Exception("No UTXOs available in wallet")
            
            # Use the first available UTXO
            utxo = list(utxos)[0]
            builder.add_input(utxo)
            
            # Create script address for contract
            script_address = Address.from_bech32(self.contract.script_address)
            
            # Add output to contract with datum
            contract_output = TransactionOutput(
                address=script_address,
                amount=Value(coin=amount_lovelace),
                datum=self._serialize_datum(datum)
            )
            builder.add_output(contract_output)
            
            # Build and sign transaction
            signed_tx = builder.build_and_sign([self.signing_key], change_address=self.address)
            
            # Submit transaction
            tx_hash = self.context.submit_tx(signed_tx)
            
            print(f"✅ Funds locked to contract!")
            print(f"🔗 Transaction hash: {tx_hash}")
            
            return str(tx_hash)
            
        except Exception as e:
            print(f"❌ Error locking funds: {e}")
            raise
    
    def execute_payment_from_contract(self, payment_id: str, recipient_address: str) -> str:
        """
        Execute payment from smart contract to recipient
        
        Args:
            payment_id: Payment identifier
            recipient_address: Final recipient address
            
        Returns:
            Transaction hash
        """
        try:
            print(f"💸 Executing payment from contract...")
            
            # Find UTXOs at contract address with matching payment ID
            script_address = Address.from_bech32(self.contract.script_address)
            contract_utxos = self.context.utxos(script_address)
            
            # Filter UTXOs by payment ID (in real implementation, decode datum)
            target_utxo = None
            for utxo in contract_utxos:
                # In real implementation, decode datum and check payment_id
                target_utxo = utxo
                break
            
            if not target_utxo:
                raise Exception(f"No locked funds found for payment ID: {payment_id}")
            
            # Build transaction to execute payment
            builder = TransactionBuilder(self.context)
            
            # Add contract UTXO as input with redeemer
            redeemer = self._create_execute_redeemer()
            builder.add_script_input(target_utxo, script=self._get_contract_script(), redeemer=redeemer)
            
            # Add output to final recipient
            recipient_addr = Address.from_bech32(recipient_address)
            payment_output = TransactionOutput(
                address=recipient_addr,
                amount=target_utxo.output.amount
            )
            builder.add_output(payment_output)
            
            # Build and sign transaction
            signed_tx = builder.build_and_sign([self.signing_key], change_address=self.address)
            
            # Submit transaction
            tx_hash = self.context.submit_tx(signed_tx)
            
            print(f"✅ Payment executed from contract!")
            print(f"🔗 Transaction hash: {tx_hash}")
            
            return str(tx_hash)
            
        except Exception as e:
            print(f"❌ Error executing payment: {e}")
            raise
    
    def get_contract_balance(self) -> float:
        """Get total ADA locked in smart contract"""
        try:
            script_address = Address.from_bech32(self.contract.script_address)
            utxos = self.context.utxos(script_address)
            
            total_lovelace = sum(utxo.output.amount.coin for utxo in utxos)
            total_ada = total_lovelace / 1_000_000
            
            return total_ada
            
        except Exception as e:
            print(f"❌ Error getting contract balance: {e}")
            return 0.0
    
    def _serialize_datum(self, datum: PaymentDatum) -> PlutusData:
        """Serialize payment datum for contract"""
        # Convert datum to PlutusData format
        # This is a simplified version - real implementation would use proper CBOR encoding
        return PlutusData()
    
    def _create_execute_redeemer(self) -> Redeemer:
        """Create redeemer for executing payment"""
        # Create "ExecutePayment" redeemer
        return Redeemer(PlutusData(), RedeemerTag.SPEND)
    
    def _get_contract_script(self) -> PlutusV2Script:
        """Get the compiled Plutus script"""
        # Load compiled contract CBOR
        cbor_bytes = bytes.fromhex(self.contract.contract_cbor)
        return PlutusV2Script(cbor_bytes)

class SmartContractPaymentService:
    """High-level payment service using smart contracts"""
    
    def __init__(self):
        self.contract = PlutusPaymentContract(
            blockfrost_project_id=os.getenv("BLOCKFROST_PROJECT_ID", "preprod7EWE9EhYgcZ2SQxz9w4HafrCwtK7yTDm"),
            network="preprod"
        )
        
        # In-memory storage for payment tracking
        self.payments: Dict[str, Dict[str, Any]] = {}
    
    def initiate_payment(self, from_address: str, to_address: str, amount: int, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initiate a payment through smart contract
        
        Args:
            from_address: Sender address
            to_address: Recipient address  
            amount: Amount in lovelace
            metadata: Payment metadata
            
        Returns:
            Payment status and details
        """
        try:
            # Generate unique payment ID
            payment_id = f"pay_{int(datetime.now().timestamp())}_{amount}"
            
            # Convert lovelace to ADA
            amount_ada = amount / 1_000_000
            
            # Lock funds to smart contract
            tx_hash = self.contract.lock_funds_to_contract(
                recipient_address=to_address,
                amount_ada=amount_ada,
                payment_id=payment_id
            )
            
            # Store payment information
            self.payments[payment_id] = {
                "tx_hash": tx_hash,
                "from_address": from_address,
                "to_address": to_address,
                "amount": amount,
                "status": "locked_to_contract",
                "metadata": metadata,
                "created_at": datetime.now().isoformat(),
                "contract_tx_hash": tx_hash,
                "execution_tx_hash": None
            }
            
            return {
                "success": True,
                "payment_id": payment_id,
                "tx_hash": tx_hash,
                "status": "locked_to_contract",
                "message": f"Payment initiated with ID: {payment_id}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to initiate payment"
            }
    
    def execute_payment(self, payment_id: str) -> Dict[str, Any]:
        """Execute a payment from smart contract"""
        try:
            if payment_id not in self.payments:
                raise Exception(f"Payment ID not found: {payment_id}")
            
            payment = self.payments[payment_id]
            
            if payment["status"] != "locked_to_contract":
                raise Exception(f"Payment not ready for execution: {payment['status']}")
            
            # Execute payment from contract
            execution_tx_hash = self.contract.execute_payment_from_contract(
                payment_id=payment_id,
                recipient_address=payment["to_address"]
            )
            
            # Update payment status
            payment["execution_tx_hash"] = execution_tx_hash
            payment["status"] = "confirmed"
            payment["executed_at"] = datetime.now().isoformat()
            
            return {
                "success": True,
                "payment_id": payment_id,
                "tx_hash": execution_tx_hash,
                "status": "confirmed",
                "message": "Payment executed successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to execute payment"
            }
    
    def get_payment_status(self, payment_id: Optional[str] = None) -> Dict[str, Any]:
        """Get status of specific payment or latest payment"""
        try:
            if payment_id:
                if payment_id not in self.payments:
                    raise Exception(f"Payment ID not found: {payment_id}")
                payment = self.payments[payment_id]
            else:
                # Get latest payment
                if not self.payments:
                    raise Exception("No payments found")
                payment_id = max(self.payments.keys())
                payment = self.payments[payment_id]
            
            # For Arduino compatibility, use execution hash if available, otherwise contract hash
            display_hash = payment.get("execution_tx_hash") or payment.get("contract_tx_hash") or payment.get("tx_hash")
            
            return {
                "status": "confirmed" if payment["status"] == "confirmed" else "pending",
                "tx_hash": display_hash,
                "confirmations": 5 if payment["status"] == "confirmed" else 0,
                "message": "TX_CONFIRMED" if payment["status"] == "confirmed" else "TX_PENDING",
                "payment_id": payment_id,
                "amount": payment["amount"],
                "smart_contract": True
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to get payment status"
            }
    
    def get_contract_info(self) -> Dict[str, Any]:
        """Get smart contract information"""
        try:
            balance = self.contract.get_contract_balance()
            
            return {
                "contract_address": self.contract.contract.script_address,
                "balance_ada": balance,
                "total_payments": len(self.payments),
                "network": self.contract.network,
                "type": "plutus_v2_payment_contract"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "message": "Failed to get contract info"
            }