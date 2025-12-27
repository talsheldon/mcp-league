"""Tests for message handling."""

import pytest
from datetime import datetime, timezone
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "SHARED"))

from league_sdk.message import Message, create_message, validate_message, MessageError


class TestMessage:
    """Test Message class."""
    
    def test_create_message(self):
        """Test message creation."""
        msg = create_message("TEST_MESSAGE", "player:P01", league_id="test_league")
        assert msg.message_type == "TEST_MESSAGE"
        assert msg.sender == "player:P01"
        assert msg.league_id == "test_league"
        assert msg.protocol == "league.v2"
        assert msg.conversation_id is not None
    
    def test_message_to_dict(self):
        """Test message to dictionary conversion."""
        msg = create_message("TEST", "player:P01", league_id="test")
        data = msg.to_dict()
        
        assert data["message_type"] == "TEST"
        assert data["sender"] == "player:P01"
        assert data["protocol"] == "league.v2"
        assert "timestamp" in data
        assert "conversation_id" in data
        assert data["league_id"] == "test"
    
    def test_message_from_dict(self):
        """Test message from dictionary."""
        data = {
            "protocol": "league.v2",
            "message_type": "TEST",
            "sender": "player:P01",
            "timestamp": "2025-01-15T10:00:00Z",
            "conversation_id": "conv-123",
            "league_id": "test",
        }
        
        msg = Message.from_dict(data)
        assert msg.message_type == "TEST"
        assert msg.sender == "player:P01"
        assert msg.league_id == "test"
    
    def test_validate_message_valid(self):
        """Test validation of valid message."""
        data = {
            "protocol": "league.v2",
            "message_type": "TEST",
            "sender": "player:P01",
            "timestamp": "2025-01-15T10:00:00Z",
            "conversation_id": "conv-123",
        }
        
        validate_message(data)  # Should not raise
    
    def test_validate_message_missing_field(self):
        """Test validation with missing field."""
        data = {
            "protocol": "league.v2",
            "message_type": "TEST",
            "sender": "player:P01",
            # Missing timestamp and conversation_id
        }
        
        with pytest.raises(MessageError):
            validate_message(data)
    
    def test_validate_message_wrong_protocol(self):
        """Test validation with wrong protocol."""
        data = {
            "protocol": "league.v1",
            "message_type": "TEST",
            "sender": "player:P01",
            "timestamp": "2025-01-15T10:00:00Z",
            "conversation_id": "conv-123",
        }
        
        with pytest.raises(MessageError):
            validate_message(data)

