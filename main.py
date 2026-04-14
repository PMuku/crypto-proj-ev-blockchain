"""
main.py — End-to-end demo of the Secure Centralized EV Charging Payment Gateway

Flow:
  1. Generate RSA key pair (if not present)
  2. Display available providers and zones
  3. Register franchise and user with the Grid Authority
  4. Franchise enters FID into kiosk → kiosk generates vFID + QR code
  5. Scenario A: Successful transaction
  6. Scenario B: Failed transaction (wrong PIN)
  7. Scenario C: Hardware failure → automatic refund
  8. Print blockchain ledger
  9. Quantum attack simulation (Shor's Algorithm)
"""

import os
import sys

# ── 0. RSA key generation ────────────────────────────────────────────────────
if not (os.path.exists("private.pem") and os.path.exists("public.pem")):
    print("[Setup] Generating 2048-bit RSA key pair...")
    from Crypto.PublicKey import RSA
    key = RSA.generate(2048)
    with open("private.pem", "wb") as f:
        f.write(key.export_key())
    with open("public.pem", "wb") as f:
        f.write(key.publickey().export_key())
    print("[Setup] Keys written to private.pem and public.pem\n")
else:
    print("[Setup] RSA keys already present.\n")

# ── Imports (after key generation so PEM files exist) ────────────────────────
import grid_authority as ga
from charging_kiosk import Kiosk
from franchise import Franchise
from user_device import UserDevice
from blockchain.blockchain import Blockchain
from shor_simulation import demonstrate_shor_attack

SEP = "\n" + "-" * 64 + "\n"

# ── 1. Show available providers and zones ────────────────────────────────────
print("=" * 64)
print("  SECURE EV CHARGING PAYMENT GATEWAY — DEMO")
print("=" * 64)
print("\n[Grid] Registered energy providers and zones:")
for provider, zones in ga.PROVIDERS.items():
    print(f"  {provider:12s} → {', '.join(zones)}")

# ── 2. Register franchise ────────────────────────────────────────────────────
print(SEP + "STEP 1: Franchise Registration")
fid = ga.register_franchise(
    name="PowerStop-MG",
    zone_code="TATA-SOUTH",
    pwd="franchise_secret",
    bal=0.0
)

franchise = Franchise(
    name="PowerStop-MG",
    zone_code="TATA-SOUTH",
    fid=fid,
    account_number="ACC-9876",
    balance=0.0
)

# ── 3. Register user ─────────────────────────────────────────────────────────
print(SEP + "STEP 2: User Registration")
uid, vmid = ga.register_user(
    name="Arjun Sharma",
    pin="4567",
    bal=500.0,
    mobile="9876543210",
    zone_code="TATA-SOUTH"
)

# ── 4. Franchise enters FID into kiosk ───────────────────────────────────────
print(SEP + "STEP 3: Kiosk Setup — Franchise Enters FID")
kiosk = Kiosk(grid_authority=ga)
franchise.enter_fid_to_kiosk(kiosk)
print(f"[Kiosk] vFID generated  (LWC-Ascon-128 encrypted FID)")
print(f"[Kiosk] QR code ready for scanning")

# ── 5. Scenario A: Successful transaction ────────────────────────────────────
print(SEP + "SCENARIO A: Successful Transaction")
print(f"[Grid] User balance before: ₹{ga.stored_users[uid]['balance']:.2f}")
print(f"[Grid] Franchise balance before: ₹{ga.stored_franchises[fid]['balance']:.2f}")

user = UserDevice()
response = user.make_transaction(
    kiosk,
    vfid=kiosk.current_vfid,
    vmid=vmid,
    pin="4567",
    amount=150.0
)
print(f"[Grid] User balance after:    ₹{ga.stored_users[uid]['balance']:.2f}")
print(f"[Grid] Franchise balance after: ₹{ga.stored_franchises[fid]['balance']:.2f}")

# ── 6. Scenario B: Wrong PIN ─────────────────────────────────────────────────
print(SEP + "SCENARIO B: Wrong PIN")
response_b = user.make_transaction(
    kiosk,
    vfid=kiosk.current_vfid,
    vmid=vmid,
    pin="0000",
    amount=50.0
)

# ── 7. Scenario C: Hardware failure → refund ─────────────────────────────────
print(SEP + "SCENARIO C: Hardware Failure → Automatic Refund")
print(f"[Grid] User balance before: ₹{ga.stored_users[uid]['balance']:.2f}")

# Register a second franchise that simulates hardware failure
fid2 = ga.register_franchise(
    name="FaultyStation",
    zone_code="ADANI-NORTH",
    pwd="faulty_pwd",
    bal=0.0
)
faulty_franchise = Franchise(
    name="FaultyStation",
    zone_code="ADANI-NORTH",
    fid=fid2,
    account_number="ACC-0001",
    balance=0.0,
    simulate_hardware_failure=True     # cable fails to unlock after payment
)
kiosk2 = Kiosk(grid_authority=ga)
faulty_franchise.enter_fid_to_kiosk(kiosk2)

response_c = user.make_transaction(
    kiosk2,
    vfid=kiosk2.current_vfid,
    vmid=vmid,
    pin="4567",
    amount=100.0
)
print(f"[Grid] User balance after refund: ₹{ga.stored_users[uid]['balance']:.2f}  (should be unchanged)")

# ── 8. Blockchain ledger ─────────────────────────────────────────────────────
print(SEP + "BLOCKCHAIN LEDGER")
ga.blockchain.print_chain()
print(f"[Blockchain] Chain valid: {ga.blockchain.is_chain_valid()}")

# ── 9. Shor's Algorithm simulation ───────────────────────────────────────────
print(SEP + "QUANTUM ATTACK SIMULATION")
demonstrate_shor_attack(vmid=vmid, pin="4567")
