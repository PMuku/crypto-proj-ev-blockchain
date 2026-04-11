from .block import Block

class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        # Genesis block has dummy data and '0' as previous hash
        genesis_data = {
            'uid': '0000000000000000',
            'fid': '0000000000000000',
            'amount': 0.0
        }
        genesis_block = Block(prev_hash="0" * 64, data=genesis_data, flag=False)
        self.chain.append(genesis_block)

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def add_block(self, data: dict, flag: bool = False):
        prev_block = self.get_latest_block()
        new_block = Block(prev_hash=prev_block.hash, data=data, flag=flag)
        self.chain.append(new_block)
        return new_block

    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            prev_block = self.chain[i - 1]

            # Validate current block hash
            if current_block.hash != current_block.compute_hash():
                return False

            # Validate chain link
            if current_block.prev_hash != prev_block.hash:
                return False
                
        return True

    def print_chain(self):
        for block in self.chain:
            print(block._print_block())
