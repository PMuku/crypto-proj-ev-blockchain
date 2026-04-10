import unittest
from blockchain.block import Block
from blockchain.blockchain import Blockchain
import time

class TestBlockchain(unittest.TestCase):
    def setUp(self):
        self.blockchain = Blockchain()

    def test_genesis_block(self):
        self.assertEqual(len(self.blockchain.chain), 1)
        genesis_block = self.blockchain.get_latest_block()
        self.assertEqual(genesis_block.prev_hash, "0" * 64)
        self.assertEqual(genesis_block.data['amount'], 0.0)

    def test_add_block(self):
        data = {'uid': 'user123', 'fid': 'franchise456', 'amount': 50.0}
        new_block = self.blockchain.add_block(data)
        
        self.assertEqual(len(self.blockchain.chain), 2)
        self.assertEqual(new_block.data, data)
        self.assertEqual(new_block.prev_hash, self.blockchain.chain[0].hash)

    def test_chain_validity(self):
        data1 = {'uid': 'user123', 'fid': 'franchise456', 'amount': 50.0}
        self.blockchain.add_block(data1)
        
        data2 = {'uid': 'user999', 'fid': 'franchise777', 'amount': 25.0}
        self.blockchain.add_block(data2)

        self.assertTrue(self.blockchain.is_chain_valid())

    def test_chain_tampering(self):
        data = {'uid': 'user123', 'fid': 'franchise456', 'amount': 50.0}
        self.blockchain.add_block(data)

        # Tampering with data
        self.blockchain.chain[1].data['amount'] = 1000.0
        
        # The chain should detect it's invalid since hash won't match data
        self.assertFalse(self.blockchain.is_chain_valid())
        
        # Even if we recompute the hash for the tampered block, the next block (if exists) would break
        self.blockchain.chain[1].hash = self.blockchain.chain[1].compute_hash()
        
        data2 = {'uid': 'user999', 'fid': 'franchise777', 'amount': 25.0}
        self.blockchain.add_block(data2)
        
        # Now if we tamper the middle block AND its hash, the third block's prev_hash won't match
        self.blockchain.chain[1].data['amount'] = 5000.0
        self.blockchain.chain[1].hash = self.blockchain.chain[1].compute_hash()
        
        self.assertFalse(self.blockchain.is_chain_valid())

if __name__ == '__main__':
    unittest.main()
