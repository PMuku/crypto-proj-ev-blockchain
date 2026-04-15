import hashlib
import time

class Block:
    def __init__(self, prev_hash: str, data: dict, flag: bool):
        
        self.data = data # (uid, fid, amount)
        self.timestamp = time.time()
        self.prev_hash = prev_hash
        self.dispute_flag = flag

        self.txn_id = self.generate_txn_id()
        self.hash = self.compute_hash() # content hashed

    def generate_txn_id(self) -> str:
        # sha3 hash of the transaction components
        txn_str = (
            self.data['uid'] + 
            self.data['fid'] + 
            str(self.timestamp) + 
            str(self.data['amount'])
        )
        return hashlib.sha3_256(txn_str.encode()).hexdigest()

    def compute_hash(self) -> str:
        import json

        block_str = json.dumps({
            "prev_hash": self.prev_hash,
            "txn_id": self.txn_id,
            "timestamp": self.timestamp,
            "dispute_flag": self.dispute_flag,
            "data": self.data
        }, sort_keys=True)
        return hashlib.sha3_256(block_str.encode()).hexdigest()
    
    def _print_block(self):
        return f"""
Block:
Transaction ID : {self.txn_id}
Previous Hash  : {self.prev_hash}
Hash           : {self.hash}
Timestamp      : {self.timestamp}
Data           : {self.data}
Dispute Flag   : {self.dispute_flag}
"""