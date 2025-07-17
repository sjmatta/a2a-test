"""
Base A2A service implementation with authentication and message handling.
"""

import asyncio
import json
import hashlib
import hmac
import base64
from datetime import datetime
from typing import Dict, Any

from .models import A2AMessage


class A2AService:
    """Base class for A2A services with authentication and message handling."""
    
    def __init__(self, service_name: str, shared_secret: str):
        self.service_name = service_name
        self.shared_secret = shared_secret
        self.message_handlers = {}
        self.message_queue = asyncio.Queue()
        
    def sign_message(self, message: A2AMessage) -> str:
        """Create HMAC signature for message authentication."""
        message_data = {
            'id': message.id,
            'sender': message.sender,
            'recipient': message.recipient,
            'payload': message.payload,
            'timestamp': message.timestamp
        }
        message_bytes = json.dumps(message_data, sort_keys=True).encode()
        signature = hmac.new(
            self.shared_secret.encode(),
            message_bytes,
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode()
    
    def verify_message(self, message: A2AMessage) -> bool:
        """Verify message signature for authentication."""
        if not message.signature:
            return False
        
        expected_signature = self.sign_message(message)
        return hmac.compare_digest(expected_signature, message.signature)
    
    def create_message(self, recipient: str, payload: Dict[str, Any]) -> A2AMessage:
        """Create a new authenticated message."""
        message = A2AMessage(
            id=self._generate_message_id(),
            sender=self.service_name,
            recipient=recipient,
            payload=payload,
            timestamp=datetime.utcnow().isoformat()
        )
        message.signature = self.sign_message(message)
        return message
    
    def register_handler(self, message_type: str, handler):
        """Register a handler for specific message types."""
        self.message_handlers[message_type] = handler
    
    async def send_message(self, recipient_service: 'A2AService', payload: Dict[str, Any]):
        """Send a message to another service."""
        message = self.create_message(recipient_service.service_name, payload)
        await recipient_service.receive_message(message)
    
    async def receive_message(self, message: A2AMessage):
        """Receive and process a message."""
        if not self.verify_message(message):
            print(f"[{self.service_name}] SECURITY: Invalid signature from {message.sender}")
            return
        
        await self.message_queue.put(message)
        print(f"[{self.service_name}] Received authenticated message from {message.sender}")
    
    async def process_messages(self):
        """Process incoming messages."""
        while True:
            try:
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                message_type = message.payload.get('type', 'unknown')
                
                if message_type in self.message_handlers:
                    await self.message_handlers[message_type](message)
                else:
                    print(f"[{self.service_name}] No handler for message type: {message_type}")
                    
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"[{self.service_name}] Error processing message: {e}")
    
    def _generate_message_id(self) -> str:
        """Generate a unique message ID."""
        import uuid
        return str(uuid.uuid4())