# UAV Authentication System API Integration Guide

This guide explains how UAV manufacturers and operators can integrate with our blockchain-based authentication system.

## API Endpoints

### UAV Registration
**Endpoint**: `POST /api/v1/uav/register`

Register a new UAV with the authentication system.

**Request Body**:
```json
{
  "uav_id": "uav-model-serial-123",
  "public_key": "ed25519-public-key-in-hex",
  "model": "Quadcopter X500",
  "firmware_version": "1.0.0"
}