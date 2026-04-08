import hashlib
import time

def sha3_hash(data: str) -> str:
    return hashlib.sha3_256(data.encode()).hexdigest()

stored_users = {}

def register_user(name: str, pin: str, bal: float, mobile: str) -> tuple[str, str]:
    # make uid -> name, time, pin hashed

    raw = name + str(time.time()) + pin
    hashed = sha3_hash(raw)
    uid = hashed[:16]  # take first 16 chars for UID
    
    hashed_pin = sha3_hash(pin)
    vmid = mobile + uid[:6]  # VMID = mobile + UID
    stored_users[uid] = {
        "name": name,
        "hashed_pin": hashed_pin,
        "balance": bal,
        "vmid": vmid
    }

    print(f"User registered with UID: {uid} and VMID: {vmid}")
    return uid, vmid

def get_vmid(uid: str) -> str:
    return stored_users[uid]["vmid"] if uid in stored_users else None

stored_franchises = {}

def register_franchise(name: str, zone_code: str, pwd: str, bal: float) -> str:
    # make fid -> name, time, pwd hashed
    
    raw = name + zone_code + pwd
    hashed = sha3_hash(raw)
    fid = hashed[:16]  # take first 16 chars for FID

    hashed_pwd = sha3_hash(pwd)
    stored_franchises[fid] = {
        "name": name,
        "zone_code": zone_code,
        "hashed_pwd": hashed_pwd,
        "balance": bal,
    }

    print(f"Franchise registered with FID: {fid}")
    return fid

# TODO: Implement LWC algo - ASCON for VFID generation or use existing library if available
def make_vfid(fid: str) -> str:
    # vfid = fid + timestamp
    # Placeholder for LWC algo - ASCON
    return "a5df" * 16

def process_transaction(request: dict) -> dict:
    # request = { vmid, pin, amount, fid }

    # 1. Check VMID <-> UID exists
    vmid, input_pin, amount, fid = request["vmid"], request["pin"], request["amount"], request["fid"]

    get_uid = lambda vmid: next((uid for uid, info in stored_users.items() if info["vmid"] == vmid), None)
    uid = get_uid(request["vmid"])
    if not uid:
        return {
            'status': 'error',
            'message': 'Invalid VMID'
        }

    # 2. Verify PIN
    pin_hash = sha3_hash(input_pin)
    if stored_users[uid]["hashed_pin"] != pin_hash:
        return {
            'status': 'error',
            'message': 'Invalid PIN'
        }
    
    # 3. Check balance
    if stored_users[uid]["balance"] < amount:
        return {
            'status': 'error',
            'message': 'Insufficient balance'
        }

    # 4. Create and write block to blockchain
    try:
        block = add_to_blockchain()
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Blockchain error: {str(e)}'
        }

    # 5. Update balances
    stored_users[uid]["balance"] -= amount
    stored_franchises[fid]["balance"] += amount
    
    return {
        'status': 'success',
        'message': 'Transaction processed successfully',
        'txn_id': block.txn_id,
        'block_hash': block.hash
    }

# TODO: Write to blockchain to store transactions and maintain integrity
def add_to_blockchain():
    pass
