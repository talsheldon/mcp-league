"""Message handling for league protocol."""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
import uuid
import json


class MessageError(Exception):
    """Message validation error."""
    pass


class Message:
    """League protocol message."""
    
    PROTOCOL_VERSION = "league.v2"
    
    REQUIRED_FIELDS = {
        "protocol",
        "message_type",
        "sender",
        "timestamp",
        "conversation_id",
    }
    
    def __init__(self, message_type: str, sender: str, **kwargs):
        self.message_type = message_type
        self.sender = sender
        self.protocol = self.PROTOCOL_VERSION
        self.timestamp = kwargs.get("timestamp") or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.conversation_id = kwargs.get("conversation_id") or f"conv-{uuid.uuid4().hex[:8]}"
        
        # Optional fields
        self.auth_token = kwargs.get("auth_token")
        self.league_id = kwargs.get("league_id")
        self.match_id = kwargs.get("match_id")
        self.round_id = kwargs.get("round_id")
        
        # Additional fields
        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        result = {
            "protocol": self.protocol,
            "message_type": self.message_type,
            "sender": self.sender,
            "timestamp": self.timestamp,
            "conversation_id": self.conversation_id,
        }
        
        # Add optional fields if present
        for field in ["auth_token", "league_id", "match_id", "round_id"]:
            value = getattr(self, field, None)
            if value is not None:
                result[field] = value
        
        # Add additional fields
        for key, value in self.__dict__.items():
            if key not in result and not key.startswith("_"):
                result[key] = value
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create message from dictionary."""
        message_type = data.get("message_type")
        sender = data.get("sender")
        
        if not message_type or not sender:
            raise MessageError("Missing required fields: message_type or sender")
        
        return cls(message_type, sender, **{k: v for k, v in data.items() if k not in ["message_type", "sender"]})
    
    def __repr__(self) -> str:
        return f"Message({self.message_type}, from={self.sender})"


def create_message(message_type: str, sender: str, **kwargs) -> Message:
    """Create a new message."""
    return Message(message_type, sender, **kwargs)


def validate_message(data: Dict[str, Any]) -> None:
    """Validate message structure."""
    if not isinstance(data, dict):
        raise MessageError("Message must be a dictionary")
    
    missing = Message.REQUIRED_FIELDS - set(data.keys())
    if missing:
        raise MessageError(f"Missing required fields: {missing}")
    
    if data.get("protocol") != Message.PROTOCOL_VERSION:
        raise MessageError(f"Invalid protocol version: {data.get('protocol')}")
    
    # Validate timestamp format
    timestamp = data.get("timestamp", "")
    if not timestamp.endswith("Z") and "+00:00" not in timestamp:
        raise MessageError("Timestamp must be in UTC format (ISO-8601)")

