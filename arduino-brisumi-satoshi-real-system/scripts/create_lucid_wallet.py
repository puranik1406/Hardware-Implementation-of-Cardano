import os
import sys
from pathlib import Path

try:
    from pycardano import PaymentSigningKey, PaymentVerificationKey, Address, Network
    import binascii
except ImportError:
    print("Missing dependency: pycardano. Install with: pip install pycardano", file=sys.stderr)
    sys.exit(1)

# Generate a fresh signing key
sk = PaymentSigningKey.generate()
vk = PaymentVerificationKey.from_signing_key(sk)

# Create testnet address
addr = Address(vk.hash(), None, network=Network.TESTNET).encode()

# Get the raw private key bytes (32 bytes)
private_key_bytes = sk.to_primitive()
private_key_hex = private_key_bytes.hex()

# Get CBOR hex
cbor_hex = sk.to_cbor_hex()

# Create output directory
OUT_DIR = Path("keys/new-wallet")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Save all formats
(OUT_DIR / "address.txt").write_text(addr, encoding="ascii")
(OUT_DIR / "private_key_hex.txt").write_text(private_key_hex, encoding="ascii")
(OUT_DIR / "cbor_hex.txt").write_text(cbor_hex, encoding="ascii")

# Also save in JSON format for compatibility
import json
wallet_info = {
    "address": addr,
    "private_key_hex": private_key_hex,
    "cbor_hex": cbor_hex,
    "network": "testnet"
}

(OUT_DIR / "wallet_info.json").write_text(json.dumps(wallet_info, indent=2), encoding="ascii")

print("🎯 NEW CARDANO TESTNET WALLET GENERATED!")
print(f"📍 Address: {addr}")
print(f"🔐 Private Key (hex): {private_key_hex}")
print(f"📦 CBOR Hex: {cbor_hex}")
print(f"📁 Files saved in: {OUT_DIR}")
print("")
print("IMPORTANT: This wallet is ready for lucid-cardano!")