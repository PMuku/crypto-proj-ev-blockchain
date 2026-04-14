import hashlib
import time
from blockchain.blockchain import Blockchain

def sha3_hash(data: str) -> str:
    return hashlib.sha3_256(data.encode()).hexdigest()

# 3 central energy providers, each with 3 regional zones (spec §2)
PROVIDERS = {
    "TATA":        ["TATA-NORTH", "TATA-SOUTH", "TATA-WEST"],
    "ADANI":       ["ADANI-NORTH", "ADANI-SOUTH", "ADANI-EAST"],
    "CHARGEPOINT": ["CP-NORTH",   "CP-SOUTH",    "CP-CENTRAL"],
}
VALID_ZONE_CODES = {zone for zones in PROVIDERS.values() for zone in zones}

blockchain = Blockchain()

stored_users = {}

def register_user(name: str, pin: str, bal: float, mobile: str, zone_code: str) -> tuple[str, str]:
    if zone_code not in VALID_ZONE_CODES:
        raise ValueError(f"Invalid zone code '{zone_code}'. Valid zones: {sorted(VALID_ZONE_CODES)}")

    raw = name + str(time.time()) + pin
    uid = sha3_hash(raw)[:16]
    if len(pin) != 4:
        raise ValueError("Pin is not of length 4")

    hashed_pin = sha3_hash(pin)
    vmid = mobile + uid[:6]
    stored_users[uid] = {
        "name": name,
        "zone_code": zone_code,
        "hashed_pin": hashed_pin,
        "balance": bal,
        "vmid": vmid
    }

    print(f"[Grid] User '{name}' registered  UID={uid}  VMID={vmid}  Zone={zone_code}")
    return uid, vmid

def get_vmid(uid: str) -> str:
    return stored_users[uid]["vmid"] if uid in stored_users else None

stored_franchises = {}

def register_franchise(name: str, zone_code: str, pwd: str, bal: float) -> str:
    if zone_code not in VALID_ZONE_CODES:
        raise ValueError(f"Invalid zone code '{zone_code}'. Valid zones: {sorted(VALID_ZONE_CODES)}")

    # FID = SHA-3 hash of (name + time_of_creation + password) truncated to 16 hex chars (spec §2)
    raw = name + str(time.time()) + pwd
    fid = sha3_hash(raw)[:16]

    stored_franchises[fid] = {
        "name": name,
        "zone_code": zone_code,
        "hashed_pwd": sha3_hash(pwd),
        "balance": bal,
    }

    print(f"[Grid] Franchise '{name}' registered  FID={fid}  Zone={zone_code}")
    return fid

def process_transaction(request: dict) -> dict:
    vmid      = request["vmid"]
    input_pin = request["pin"]
    amount    = request["amount"]
    fid       = request["fid"]

    # 1. Resolve VMID → UID
    uid = next((u for u, info in stored_users.items() if info["vmid"] == vmid), None)
    if not uid:
        return {"status": "error", "message": "Invalid VMID"}

    # 2. Verify PIN
    if stored_users[uid]["hashed_pin"] != sha3_hash(input_pin):
        return {"status": "error", "message": "Invalid PIN"}

    # 3. Verify FID exists
    if fid not in stored_franchises:
        return {"status": "error", "message": "Unknown franchise FID"}

    # 4. Check balance
    if stored_users[uid]["balance"] < amount:
        return {"status": "error", "message": "Insufficient balance"}

    # 5. Record on blockchain
    try:
        block = add_to_blockchain(uid, fid, amount)
    except Exception as e:
        return {"status": "error", "message": f"Blockchain error: {e}"}

    # 6. Transfer funds
    stored_users[uid]["balance"]      -= amount
    stored_franchises[fid]["balance"] += amount

    return {
        "status":     "success",
        "message":    "Transaction processed successfully",
        "uid":        uid,   # returned so kiosk can pass to process_refund if needed
        "txn_id":     block.txn_id,
        "block_hash": block.hash
    }

def process_refund(uid: str, fid: str, amount: float) -> dict:
    """Reverse a successful transaction when hardware fails to dispense power (spec §6)."""
    stored_users[uid]["balance"]      += amount
    stored_franchises[fid]["balance"] -= amount
    block = add_to_blockchain(uid, fid, amount, flag=True)  # dispute_flag=True, negative amount
    print(f"[Grid] Refund processed  UID={uid}  FID={fid}  Amount={amount}")
    return {"status": "refunded", "txn_id": block.txn_id}

def add_to_blockchain(uid: str, fid: str, amount: float, flag: bool = False):
    return blockchain.add_block(
        data={"uid": uid, "fid": fid, "amount": amount},
        flag=flag
    )
