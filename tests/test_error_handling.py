"""Tests for error handling and error codes."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "SHARED"))

from league_sdk import ErrorCode, get_error_description, create_error_message, create_message


class TestErrorCodes:
    """Test error code enumeration and utilities."""
    
    def test_all_error_codes_defined(self):
        """Test that all required error codes are defined."""
        required_codes = [
            "E001", "E002", "E003", "E004",  # General
            "E005", "E006", "E007",  # Registration
            "E008", "E009", "E010", "E011",  # Validation
            "E012", "E013", "E014",  # Authentication
            "E015", "E016", "E017", "E018",  # Game
            "E019", "E020",  # Timeout
            "E021", "E022", "E023",  # League
        ]
        
        for code in required_codes:
            assert hasattr(ErrorCode, code), f"Error code {code} not defined"
            assert ErrorCode[code].value == code
    
    def test_error_description_exists(self):
        """Test that all error codes have descriptions."""
        for error_code in ErrorCode:
            description = get_error_description(error_code)
            assert description != "UNKNOWN_ERROR", f"No description for {error_code.value}"
            assert len(description) > 0
    
    def test_create_error_message(self):
        """Test error message creation."""
        error_info = create_error_message(
            ErrorCode.E012,
            "LEAGUE_QUERY",
            {"provided_token": "invalid"}
        )
        
        assert error_info["error_code"] == "E012"
        assert error_info["error_description"] == "AUTH_TOKEN_INVALID"
        assert error_info["original_message_type"] == "LEAGUE_QUERY"
        assert error_info["context"]["provided_token"] == "invalid"


class TestErrorMessages:
    """Test LEAGUE_ERROR message creation."""
    
    def test_auth_token_invalid_error(self):
        """Test AUTH_TOKEN_INVALID error message."""
        from league_sdk import create_error_message
        
        error_info = create_error_message(ErrorCode.E012, "LEAGUE_QUERY")
        
        error_message = create_message(
            "LEAGUE_ERROR",
            "league_manager",
            error_code=error_info["error_code"],
            error_description=error_info["error_description"],
            original_message_type=error_info["original_message_type"],
            context=error_info["context"],
        )
        
        assert error_message.message_type == "LEAGUE_ERROR"
        assert getattr(error_message, "error_code") == "E012"
        assert getattr(error_message, "error_description") == "AUTH_TOKEN_INVALID"
    
    def test_not_enough_players_error(self):
        """Test NOT_ENOUGH_PLAYERS error message."""
        from league_sdk import create_error_message
        
        error_info = create_error_message(ErrorCode.E005, "START_LEAGUE", {"registered": 1})
        
        error_message = create_message(
            "LEAGUE_ERROR",
            "league_manager",
            error_code=error_info["error_code"],
            error_description=error_info["error_description"],
            original_message_type=error_info["original_message_type"],
            context=error_info["context"],
        )
        
        assert getattr(error_message, "error_code") == "E005"
        assert getattr(error_message, "error_description") == "NOT_ENOUGH_PLAYERS"
    
    def test_invalid_message_format_error(self):
        """Test INVALID_MESSAGE_FORMAT error message."""
        from league_sdk import create_error_message
        
        error_info = create_error_message(ErrorCode.E001, "UNKNOWN_TYPE", {"field": "protocol"})
        
        error_message = create_message(
            "LEAGUE_ERROR",
            "league_manager",
            error_code=error_info["error_code"],
            error_description=error_info["error_description"],
            original_message_type=error_info["original_message_type"],
            context=error_info["context"],
        )
        
        assert getattr(error_message, "error_code") == "E001"
        assert getattr(error_message, "error_description") == "INVALID_MESSAGE_FORMAT"


class TestErrorCodeUsage:
    """Test error code usage in handlers."""
    
    def test_error_code_enumeration(self):
        """Test that error codes can be used as enum values."""
        assert ErrorCode.E005.value == "E005"
        assert ErrorCode.E012.value == "E012"
        assert str(ErrorCode.E005.value) == "E005"
    
    def test_error_code_comparison(self):
        """Test error code comparison."""
        assert ErrorCode.E005 == ErrorCode.E005
        assert ErrorCode.E005 != ErrorCode.E012

