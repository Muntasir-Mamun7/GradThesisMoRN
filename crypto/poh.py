import hashlib
import time
import json

class ProofOfHistory:
    """Implements a simplified Proof of History mechanism"""
    
    def __init__(self):
        """Initialize with a genesis hash"""
        self.current_hash = hashlib.sha256("UAV Authentication System Genesis".encode()).hexdigest()
        self.ticks = []
        self.tick_count = 0
        
    def tick(self, data=None):
        """Generate a new tick in the PoH sequence"""
        prev_hash = self.current_hash
        timestamp = int(time.time())
        
        # Combine previous hash with data (if any)
        message = prev_hash
        if data:
            if isinstance(data, dict) or isinstance(data, list):
                message += json.dumps(data, sort_keys=True)
            else:
                message += str(data)
        
        # Generate new hash
        new_hash = hashlib.sha256(message.encode()).hexdigest()
        self.current_hash = new_hash
        self.tick_count += 1
        
        # Create tick record
        tick = {
            'sequence': self.tick_count,
            'prev_hash': prev_hash,
            'hash': new_hash,
            'data': data,
            'timestamp': timestamp
        }
        
        self.ticks.append(tick)
        return tick
    
    def verify_sequence(self, start_idx=0, end_idx=None):
        """Verify that a sequence of ticks is valid"""
        if end_idx is None:
            end_idx = len(self.ticks)
        
        if start_idx >= end_idx or start_idx < 0 or end_idx > len(self.ticks):
            return False
        
        for i in range(start_idx + 1, end_idx):
            prev_tick = self.ticks[i-1]
            curr_tick = self.ticks[i]
            
            # Verify prev_hash matches
            if curr_tick['prev_hash'] != prev_tick['hash']:
                return False
                
            # Verify sequence number
            if curr_tick['sequence'] != prev_tick['sequence'] + 1:
                return False
                
            # Verify hash calculation
            message = prev_tick['hash']
            if curr_tick['data']:
                if isinstance(curr_tick['data'], dict) or isinstance(curr_tick['data'], list):
                    message += json.dumps(curr_tick['data'], sort_keys=True)
                else:
                    message += str(curr_tick['data'])
            
            expected_hash = hashlib.sha256(message.encode()).hexdigest()
            if curr_tick['hash'] != expected_hash:
                return False
                
        return True