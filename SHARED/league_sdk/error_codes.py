"""Error code definitions for league.v2 protocol."""

from enum import Enum
from typing import Dict, Optional


class ErrorCode(str, Enum):
    """Error codes for league protocol messages."""
    
    # General errors (E001-E004)
    E001 = "E001"  # INVALID_MESSAGE_FORMAT
    E002 = "E002"  # UNSUPPORTED_PROTOCOL_VERSION
    E003 = "E003"  # MISSING_REQUIRED_FIELD
    E004 = "E004"  # INVALID_FIELD_VALUE
    
    # Registration errors (E005-E007)
    E005 = "E005"  # NOT_ENOUGH_PLAYERS
    E006 = "E006"  # DUPLICATE_REGISTRATION
    E007 = "E007"  # INVALID_AGENT_METADATA
    
    # Validation errors (E008-E011)
    E008 = "E008"  # INVALID_PLAYER_ID
    E009 = "E009"  # INVALID_REFEREE_ID
    E010 = "E010"  # INVALID_LEAGUE_ID
    E011 = "E011"  # INVALID_MATCH_ID
    
    # Authentication errors (E012-E014)
    E012 = "E012"  # AUTH_TOKEN_INVALID
    E013 = "E013"  # AUTH_TOKEN_EXPIRED
    E014 = "E014"  # AUTH_TOKEN_MISSING
    
    # Game errors (E015-E018)
    E015 = "E015"  # GAME_ALREADY_STARTED
    E016 = "E016"  # PLAYER_NOT_REGISTERED
    E017 = "E017"  # REFEREE_NOT_REGISTERED
    E018 = "E018"  # MATCH_NOT_FOUND
    
    # Timeout errors (E019-E020)
    E019 = "E019"  # CHOICE_TIMEOUT
    E020 = "E020"  # JOIN_TIMEOUT
    
    # League errors (E021-E023)
    E021 = "E021"  # LEAGUE_ALREADY_STARTED
    E022 = "E022"  # LEAGUE_NOT_STARTED
    E023 = "E023"  # ROUND_NOT_FOUND


# Error code to description mapping
ERROR_DESCRIPTIONS: Dict[ErrorCode, str] = {
    ErrorCode.E001: "INVALID_MESSAGE_FORMAT",
    ErrorCode.E002: "UNSUPPORTED_PROTOCOL_VERSION",
    ErrorCode.E003: "MISSING_REQUIRED_FIELD",
    ErrorCode.E004: "INVALID_FIELD_VALUE",
    ErrorCode.E005: "NOT_ENOUGH_PLAYERS",
    ErrorCode.E006: "DUPLICATE_REGISTRATION",
    ErrorCode.E007: "INVALID_AGENT_METADATA",
    ErrorCode.E008: "INVALID_PLAYER_ID",
    ErrorCode.E009: "INVALID_REFEREE_ID",
    ErrorCode.E010: "INVALID_LEAGUE_ID",
    ErrorCode.E011: "INVALID_MATCH_ID",
    ErrorCode.E012: "AUTH_TOKEN_INVALID",
    ErrorCode.E013: "AUTH_TOKEN_EXPIRED",
    ErrorCode.E014: "AUTH_TOKEN_MISSING",
    ErrorCode.E015: "GAME_ALREADY_STARTED",
    ErrorCode.E016: "PLAYER_NOT_REGISTERED",
    ErrorCode.E017: "REFEREE_NOT_REGISTERED",
    ErrorCode.E018: "MATCH_NOT_FOUND",
    ErrorCode.E019: "CHOICE_TIMEOUT",
    ErrorCode.E020: "JOIN_TIMEOUT",
    ErrorCode.E021: "LEAGUE_ALREADY_STARTED",
    ErrorCode.E022: "LEAGUE_NOT_STARTED",
    ErrorCode.E023: "ROUND_NOT_FOUND",
}


def get_error_description(error_code: ErrorCode) -> str:
    """Get human-readable description for an error code."""
    return ERROR_DESCRIPTIONS.get(error_code, "UNKNOWN_ERROR")


def create_error_message(
    error_code: ErrorCode,
    original_message_type: Optional[str] = None,
    context: Optional[Dict] = None,
) -> Dict:
    """Create a standardized error message."""
    return {
        "error_code": error_code.value,
        "error_description": get_error_description(error_code),
        "original_message_type": original_message_type,
        "context": context or {},
    }

