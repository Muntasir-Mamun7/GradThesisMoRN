import time
import json
import hashlib
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from crypto.poh import ProofOfHistory

class Block:
    """Represents a block in the blockchain"""
    
    def __init__(self, index, prev_hash, poh_tick, transactions, timestamp=None):
        self.index = index
        self.prev_hash = prev_hash
        self.poh_tick = poh_tick
        self.transactions = transactions
        self.timestamp = timestamp or int(time.time())
        self.hash = self.calculate_hash()
    
    def calculate_hash(self):
        """Calculate the hash of this block"""
        block_data = {
            'index': self.index,
            'prev_hash': self.prev_hash,
            'poh_tick': self.poh_tick,
            'transactions': self.transactions,
            'timestamp': self.timestamp
        }
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def to_dict(self):
        """Convert block to dictionary"""
        return {
            'index': self.index,
            'hash': self.hash,
            'prev_hash': self.prev_hash,
            'poh_tick': self.poh_tick,
            'transactions': self.transactions,
            'timestamp': self.timestamp
        }

class Blockchain:
    """UAV authentication blockchain with PoH consensus"""
    
    def __init__(self):
        """Initialize the blockchain with a genesis block"""
        self.chain = []
        self.poh = ProofOfHistory()
        self.pending_transactions = []
        self.registered_uavs = {}  # uav_id -> public_key
        self.used_nonces = {}  # nonce -> timestamp
        
        # Create genesis block
        genesis_tick = self.poh.tick("Genesis Block")
        genesis_block = Block(0, "0" * 64, genesis_tick, [], int(time.time()))
        self.chain.append(genesis_block)
    
    def get_latest_block(self):
        """Get the latest block in the chain"""
        return self.chain[-1]
    
    def add_transaction(self, transaction):
        """Add a transaction to pending transactions"""
        # Transaction validation would go here
        self.pending_transactions.append(transaction)
        return len(self.pending_transactions)
    
    def register_uav(self, uav_id, public_key, model, firmware_version):
        """Register a new UAV"""
        if uav_id in self.registered_uavs:
            return False, "UAV already registered"
        
        # Create registration transaction
        transaction = {
            'type': 'REGISTER',
            'uav_id': uav_id,
            'public_key': public_key,
            'model': model,
            'firmware_version': firmware_version,
            'timestamp': int(time.time())
        }
        
        self.add_transaction(transaction)
        self.registered_uavs[uav_id] = {
            'public_key': public_key,
            'model': model,
            'firmware_version': firmware_version,
            'last_auth': None
        }
        
        return True, "UAV registered successfully"
    
    def authenticate_uav(self, uav_id, nonce, timestamp, signature):
        """Authenticate a UAV"""
        # Check if UAV is registered
        if uav_id not in self.registered_uavs:
            return False, "UAV not registered"
        
        # Check for replay attacks
        nonce_key = f"{uav_id}:{nonce}"
        if nonce_key in self.used_nonces:
            return False, "Nonce already used (potential replay attack)"
        
        # In a real implementation, we would verify the signature here
        # using the UAV's public key
        
        # Create authentication transaction
        transaction = {
            'type': 'AUTHENTICATE',
            'uav_id': uav_id,
            'nonce': nonce,
            'timestamp': timestamp,
            'signature': signature
        }
        
        self.add_transaction(transaction)
        self.used_nonces[nonce_key] = timestamp
        self.registered_uavs[uav_id]['last_auth'] = timestamp
        
        return True, "UAV authenticated successfully"
    
    def mine_block(self):
        """Create a new block with pending transactions"""
        if not self.pending_transactions:
            return None
            
        latest_block = self.get_latest_block()
        
        # Create a PoH tick with the transaction data
        poh_tick = self.poh.tick(self.pending_transactions)
        
        # Create a new block
        new_block = Block(
            index=latest_block.index + 1,
            prev_hash=latest_block.hash,
            poh_tick=poh_tick,
            transactions=self.pending_transactions.copy(),
            timestamp=int(time.time())
        )
        
        # Reset pending transactions
        self.pending_transactions = []
        
        # Add the block to the chain
        self.chain.append(new_block)
        
        return new_block
    
    def is_chain_valid(self):
        """Verify the integrity of the blockchain"""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            
            # Check current block hash
            if current.hash != current.calculate_hash():
                return False
                
            # Check link to previous block
            if current.prev_hash != previous.hash:
                return False
        
        return True
    
    def get_uav_status(self, uav_id):
        """Get the status of a registered UAV"""
        if uav_id not in self.registered_uavs:
            return None
            
        return self.registered_uavs[uav_id]