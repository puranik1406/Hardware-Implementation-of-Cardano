import os
import sys
from pathlib import Path

try:
    from pycardano import PaymentSigningKey, PaymentVerificationKey, Address, Network
except ImportError:
    print("Missing dependency: pycardano. Install with: pip install pycardano", file=sys.stderr)
    sys.exit(1)

OUT_DIR = Path(os.environ.get("OUT_DIR", "keys")).resolve()
NETWORK = os.environ.get("CARDANO_NETWORK", "preprod").lower()

if NETWORK not in ("preprod", "preview", "testnet"):
    print(f"Unsupported network '{NETWORK}'. Use preprod/preview/testnet.", file=sys.stderr)
    sys.exit(1)

OUT_DIR.mkdir(parents=True, exist_ok=True)

# Generate a fresh signing key and corresponding enterprise address on testnet
sk = PaymentSigningKey.generate()
vk = PaymentVerificationKey.from_signing_key(sk)
addr = Address(vk.hash(), None, network=Network.TESTNET).encode()  # addr_test1...

# Persist artifacts
prefix = "preprod"
addr_path = OUT_DIR / f"{prefix}.payment.addr"
sk_cbor_path = OUT_DIR / f"{prefix}.payment.cborHex.txt"

addr_path.write_text(addr, encoding="ascii")
sk_cbor_path.write_text(sk.to_cbor_hex(), encoding="ascii")

print("Generated preprod wallet artifacts:")
print(f"  Address: {addr}")
print(f"  Address file: {addr_path}")
print(f"  Signing key cborHex file: {sk_cbor_path}")
print("IMPORTANT: Keep the signing key file private. Do NOT commit it to git.")
