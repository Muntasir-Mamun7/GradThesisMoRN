import requests
import json
import time
import hashlib
import uuid
import base64
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

class UAVClient:
    """Client for the UAV authentication system"""
    
    def __init__(self, server_url, uav_id=None, private_key=None):
        """Initialize the UAV client"""
        self.server_url = server_url
        self.uav_id = uav_id or f"uav-{uuid.uuid4()}"
        
        # Generate or use provided key
        if private_key:
            if isinstance(private_key, str):
                private_key = bytes.fromhex(private_key)
            self.private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key)
        else:
            self.private_key = ed25519.Ed25519PrivateKey.generate()
            
        # Get public key
        self.public_key = self.private_key.public_key()
    
    def get_public_key_hex(self):
        """Get the public key as hex string"""
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        ).hex()
    
    def sign_message(self, message):
        """Sign a message with the private key"""
        if isinstance(message, str):
            message = message.encode('utf-8')
        signature = self.private_key.sign(message)
        return signature.hex()
    
    def register(self, model, firmware_version):
        """Register this UAV with the system"""
        registration_data = {
            "uav_id": self.uav_id,
            "public_key": self.get_public_key_hex(),
            "model": model,
            "firmware_version": firmware_version
        }
        
        try:
            response = requests.post(
                f"{self.server_url}/api/v1/uav/register",
                json=registration_data
            )
            return response.json()
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to register UAV: {str(e)}",
                "data": None
            }
    
    def authenticate(self):
        """Authenticate this UAV with the system"""
        # Generate a unique nonce
        nonce = uuid.uuid4().hex
        timestamp = int(time.time())
        
        # Create message to sign
        message = f"{self.uav_id}{nonce}{timestamp}"
        signature = self.sign_message(message)
        
        authentication_data = {
            "uav_id": self.uav_id,
            "nonce": nonce,
            "timestamp": timestamp,
            "signature": signature
        }
        
        try:
            response = requests.post(
                f"{self.server_url}/api/v1/uav/authenticate",
                json=authentication_data
            )
            return response.json()
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to authenticate UAV: {str(e)}",
                "data": None
            }
    
    def get_status(self):
        """Get this UAV's status"""
        try:
            response = requests.get(
                f"{self.server_url}/api/v1/uav/status/{self.uav_id}"
            )
            return response.json()
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to get UAV status: {str(e)}",
                "data": None
            }
    
    def save_keys(self, filename):
        """Save keys to a file for later use"""
        private_bytes = self.private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        key_data = {
            "uav_id": self.uav_id,
            "private_key": private_bytes.hex(),
            "public_key": self.get_public_key_hex()
        }
        
        with open(filename, 'w') as f:
            json.dump(key_data, f, indent=2)
    
    @classmethod
    def load_from_file(cls, filename, server_url):
        """Load a client from saved keys"""
        with open(filename, 'r') as f:
            key_data = json.load(f)
        
        return cls(
            server_url=server_url,
            uav_id=key_data["uav_id"],
            private_key=key_data["private_key"]
        )