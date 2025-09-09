from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import time
import uuid
import sys
import os

app = FastAPI(
    title="UAV Authentication System API",
    description="Blockchain-based authentication system for UAVs using Proof of History",
    version="1.0.0",
    contact={
        "name": "Muntasir-Mamun7",
        "email": "munmamun9@gmail.com"
    },
)
# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from blockchain.blockchain import Blockchain

app = FastAPI(title="UAV Authentication System")
blockchain = Blockchain()

class UavRegistration(BaseModel):
    uav_id: str
    public_key: str
    model: str
    firmware_version: str

class UavAuthentication(BaseModel):
    uav_id: str
    nonce: str
    timestamp: int
    signature: str

@app.get("/")
def read_root():
    return "UAV Authentication System API is running..."

@app.get("/api/v1/blockchain/stats")
def get_blockchain_stats():
    """Get blockchain statistics"""
    return {
        "success": True,
        "message": "Blockchain statistics",
        "data": {
            "blocks": len(blockchain.chain),
            "registered_uavs": len(blockchain.registered_uavs),
            "last_block_time": blockchain.get_latest_block().timestamp
        }
    }

@app.post("/api/v1/uav/register")
def register_uav(registration: UavRegistration):
    """Register a new UAV"""
    success, message = blockchain.register_uav(
        registration.uav_id,
        registration.public_key,
        registration.model,
        registration.firmware_version
    )
    
    if not success:
        return {
            "success": False,
            "message": message,
            "data": None
        }
    
    # Mine a new block with the registration transaction
    block = blockchain.mine_block()
    
    return {
        "success": True,
        "message": f"UAV {registration.uav_id} successfully registered",
        "data": {
            "block_number": block.index,
            "uav_id": registration.uav_id
        }
    }

@app.post("/api/v1/uav/authenticate")
def authenticate_uav(authentication: UavAuthentication):
    """Authenticate a UAV"""
    success, message = blockchain.authenticate_uav(
        authentication.uav_id,
        authentication.nonce,
        authentication.timestamp,
        authentication.signature
    )
    
    if not success:
        return {
            "success": False,
            "message": message,
            "data": None
        }
    
    # Mine a new block with the authentication transaction
    block = blockchain.mine_block()
    
    return {
        "success": True,
        "message": f"UAV {authentication.uav_id} successfully authenticated",
        "data": {
            "block_number": block.index,
            "uav_id": authentication.uav_id,
            "timestamp": authentication.timestamp
        }
    }

@app.get("/api/v1/uav/status/{uav_id}")
def get_uav_status(uav_id: str):
    """Get UAV status"""
    status = blockchain.get_uav_status(uav_id)
    
    if not status:
        return {
            "success": False,
            "message": f"UAV {uav_id} is not registered",
            "data": None
        }
    
    return {
        "success": True,
        "message": f"UAV {uav_id} status",
        "data": {
            "uav_id": uav_id,
            "last_authenticated": status["last_auth"],
            "firmware": status["firmware_version"]
        }
    }

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8080, reload=True)