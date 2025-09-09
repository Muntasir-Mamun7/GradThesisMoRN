import requests
import sys
import os
import time
import argparse

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.uav_client import UAVClient

# Default settings
DEFAULT_SERVER = "http://localhost:8080"
DEFAULT_UAV_ID = "test-uav-1"

def check_server_reachable(server_url):
    """Check if the server is reachable"""
    try:
        response = requests.get(server_url)
        print(f"Server is reachable! Response: {response.status_code}")
        print(f"Content: {response.text}")
        return True
    except Exception as e:
        print(f"Server is not reachable: {e}")
        return False

def test_blockchain_stats(server_url):
    """Test getting blockchain statistics"""
    print("\nTesting Blockchain Stats...")
    try:
        response = requests.get(f"{server_url}/api/v1/blockchain/stats")
        result = response.json()
        
        print(f"Stats result: {result['success']}")
        if result['success']:
            print(f"Total Blocks: {result['data']['blocks']}")
            print(f"Registered UAVs: {result['data']['registered_uavs']}")
        else:
            print(f"Error: {result['message']}")
        
        return result['success']
    except Exception as e:
        print(f"Error getting blockchain stats: {e}")
        return False

def test_uav_registration(client, model, firmware):
    """Test UAV registration"""
    print("\nTesting UAV Registration...")
    result = client.register(model, firmware)
    
    print(f"Registration result: {result['success']}")
    if result['success']:
        print(f"Message: {result['message']}")
        print(f"Block: #{result['data']['block_number']}")
    else:
        print(f"Error: {result['message']}")
    
    return result['success']

def test_uav_status(client):
    """Test getting UAV status"""
    print("\nTesting UAV Status...")
    result = client.get_status()
    
    print(f"Status result: {result['success']}")
    if result['success']:
        print(f"UAV ID: {result['data']['uav_id']}")
        print(f"Last Authenticated: {result['data']['last_authenticated']}")
        print(f"Firmware: {result['data']['firmware']}")
    else:
        print(f"Error: {result['message']}")
    
    return result['success']

def test_uav_authentication(client):
    """Test UAV authentication"""
    print("\nTesting UAV Authentication...")
    result = client.authenticate()
    
    print(f"Authentication result: {result['success']}")
    if result['success']:
        print(f"Message: {result['message']}")
        print(f"Block: #{result['data']['block_number']}")
    else:
        print(f"Error: {result['message']}")
    
    return result['success']

def main():
    parser = argparse.ArgumentParser(description="UAV Authentication System Test Client")
    parser.add_argument("--server", default=DEFAULT_SERVER, help=f"Authentication server URL (default: {DEFAULT_SERVER})")
    parser.add_argument("--uav-id", default=DEFAULT_UAV_ID, help=f"UAV ID (default: {DEFAULT_UAV_ID})")
    parser.add_argument("--model", default="Quadcopter X500", help="UAV model (default: Quadcopter X500)")
    parser.add_argument("--firmware", default="1.0.0", help="UAV firmware version (default: 1.0.0)")
    parser.add_argument("--key-file", help="Key file for the UAV (if not provided, new keys will be generated)")
    
    args = parser.parse_args()
    
    # Check if the server is reachable
    if not check_server_reachable(args.server):
        print("Cannot continue testing without a reachable server.")
        sys.exit(1)
    
    # Create or load the UAV client
    if args.key_file and os.path.exists(args.key_file):
        client = UAVClient.load_from_file(args.key_file, args.server)
        print(f"Loaded UAV client from {args.key_file}")
    else:
        client = UAVClient(args.server, args.uav_id)
        print(f"Created new UAV client with ID {args.uav_id}")
        
        if args.key_file:
            client.save_keys(args.key_file)
            print(f"Saved UAV keys to {args.key_file}")
    
    # Test blockchain stats
    test_blockchain_stats(args.server)
    
    # Test UAV registration
    test_uav_registration(client, args.model, args.firmware)
    
    # Test UAV status
    test_uav_status(client)
    
    # Test UAV authentication
    test_uav_authentication(client)
    
    # Test UAV status again (should show last authentication time)
    test_uav_status(client)

if __name__ == "__main__":
    main()