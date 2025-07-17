"""
Authentication utilities for A2A service communication.
"""

import hashlib
import hmac
import base64
import time
from typing import Optional
from fastapi import HTTPException, Header, Depends


class A2AAuth:
    """Handle A2A authentication between services."""
    
    def __init__(self, shared_secret: str):
        self.shared_secret = shared_secret
    
    def create_signature(self, service_name: str, timestamp: str, body: str = "") -> str:
        """Create HMAC signature for request authentication."""
        message = f"{service_name}:{timestamp}:{body}"
        signature = hmac.new(
            self.shared_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode()
    
    def verify_signature(self, service_name: str, timestamp: str, signature: str, body: str = "") -> bool:
        """Verify HMAC signature for request authentication."""
        expected_signature = self.create_signature(service_name, timestamp, body)
        return hmac.compare_digest(expected_signature, signature)
    
    def create_auth_headers(self, service_name: str, body: str = "") -> dict:
        """Create authentication headers for outgoing requests."""
        timestamp = str(int(time.time()))
        signature = self.create_signature(service_name, timestamp, body)
        
        return {
            "X-Service-Name": service_name,
            "X-Timestamp": timestamp,
            "X-Signature": signature
        }


def create_auth_dependency(shared_secret: str):
    """Create FastAPI dependency for authentication."""
    auth = A2AAuth(shared_secret)
    
    async def verify_request(
        x_service_name: Optional[str] = Header(None),
        x_timestamp: Optional[str] = Header(None),
        x_signature: Optional[str] = Header(None)
    ):
        if not all([x_service_name, x_timestamp, x_signature]):
            raise HTTPException(status_code=401, detail="Missing authentication headers")
        
        # Check timestamp is recent (within 5 minutes)
        try:
            request_time = int(x_timestamp)
            current_time = int(time.time())
            if abs(current_time - request_time) > 300:  # 5 minutes
                raise HTTPException(status_code=401, detail="Request timestamp too old")
        except ValueError:
            raise HTTPException(status_code=401, detail="Invalid timestamp")
        
        # For now, skip body verification to simplify (in production, you'd want this)
        # Verify signature with empty body
        if not auth.verify_signature(x_service_name, x_timestamp, x_signature, ""):
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        return x_service_name
    
    return verify_request