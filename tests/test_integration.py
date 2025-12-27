"""Integration tests for full system flows."""

import pytest
import asyncio
import httpx
from datetime import datetime, timezone
from pathlib import Path
import sys
import tempfile
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent / "SHARED"))

from league_sdk import Message, create_message, validate_message


class TestIntegrationRegistration:
    """Test agent registration flows."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary data directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_referee_registration_flow(self, temp_data_dir):
        """Test complete referee registration flow."""
        # This would require running League Manager
        # For now, test message creation and validation
        message = create_message(
            "REFEREE_REGISTER_REQUEST",
            "referee:REF01",
            referee_meta={
                "display_name": "Test Referee",
                "version": "1.0.0",
                "game_types": ["even_odd"],
                "contact_endpoint": "http://localhost:8001/mcp",
                "max_concurrent_matches": 2,
            },
        )
        
        validate_message(message.to_dict())
        assert message.message_type == "REFEREE_REGISTER_REQUEST"
        assert message.sender == "referee:REF01"
    
    def test_player_registration_flow(self, temp_data_dir):
        """Test complete player registration flow."""
        message = create_message(
            "LEAGUE_REGISTER_REQUEST",
            "player:P01",
            player_meta={
                "display_name": "Test Player",
                "version": "1.0.0",
                "game_types": ["even_odd"],
                "contact_endpoint": "http://localhost:8101/mcp",
            },
        )
        
        validate_message(message.to_dict())
        assert message.message_type == "LEAGUE_REGISTER_REQUEST"
        assert message.sender == "player:P01"


class TestIntegrationGameFlow:
    """Test complete game flow."""
    
    def test_game_invitation_to_completion_flow(self):
        """Test flow from game invitation to game completion."""
        # Step 1: Game invitation
        invitation = create_message(
            "GAME_INVITATION",
            "referee:REF01",
            league_id="test_league",
            round_id=1,
            match_id="R1M1",
            game_type="even_odd",
            role_in_match="PLAYER_A",
            opponent_id="P02",
        )
        validate_message(invitation.to_dict())
        
        # Step 2: Game join ack
        join_ack = create_message(
            "GAME_JOIN_ACK",
            "player:P01",
            match_id="R1M1",
            player_id="P01",
            arrival_timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            accept=True,
        )
        validate_message(join_ack.to_dict())
        
        # Step 3: Choose parity call
        from datetime import timedelta
        deadline = (datetime.now(timezone.utc) + timedelta(seconds=30)).isoformat().replace("+00:00", "Z")
        
        parity_call = create_message(
            "CHOOSE_PARITY_CALL",
            "referee:REF01",
            match_id="R1M1",
            player_id="P01",
            game_type="even_odd",
            context={"opponent_id": "P02", "round_id": 1},
            deadline=deadline,
        )
        validate_message(parity_call.to_dict())
        
        # Step 4: Choose parity response
        parity_response = create_message(
            "CHOOSE_PARITY_RESPONSE",
            "player:P01",
            match_id="R1M1",
            player_id="P01",
            parity_choice="even",
        )
        validate_message(parity_response.to_dict())
        
        # Step 5: Game over
        game_over = create_message(
            "GAME_OVER",
            "referee:REF01",
            match_id="R1M1",
            game_type="even_odd",
            game_result={
                "status": "WIN",
                "winner_player_id": "P01",
                "drawn_number": 8,
                "number_parity": "even",
                "choices": {"P01": "even", "P02": "odd"},
                "reason": "P01 chose even, number was 8 (even)",
            },
        )
        validate_message(game_over.to_dict())


class TestIntegrationErrorHandling:
    """Test error handling flows."""
    
    def test_invalid_auth_token_flow(self):
        """Test flow with invalid authentication token."""
        from league_sdk import ErrorCode, create_error_message
        
        error_info = create_error_message(ErrorCode.E012, "LEAGUE_QUERY", {"provided_token": "invalid"})
        
        error_message = create_message(
            "LEAGUE_ERROR",
            "league_manager",
            error_code=error_info["error_code"],
            error_description=error_info["error_description"],
            original_message_type=error_info["original_message_type"],
            context=error_info["context"],
        )
        
        validate_message(error_message.to_dict())
        assert error_message.message_type == "LEAGUE_ERROR"
        assert getattr(error_message, "error_code") == "E012"
    
    def test_not_enough_players_error(self):
        """Test error when trying to start league with insufficient players."""
        from league_sdk import ErrorCode, create_error_message
        
        error_info = create_error_message(ErrorCode.E005, "START_LEAGUE", {"registered_players": 1})
        
        error_message = create_message(
            "LEAGUE_ERROR",
            "league_manager",
            error_code=error_info["error_code"],
            error_description=error_info["error_description"],
            original_message_type=error_info["original_message_type"],
            context=error_info["context"],
        )
        
        validate_message(error_message.to_dict())
        assert getattr(error_message, "error_code") == "E005"


class TestIntegrationRoundFlow:
    """Test round announcement and completion flow."""
    
    def test_round_announcement_with_endpoints(self):
        """Test ROUND_ANNOUNCEMENT includes player endpoints."""
        announcement = create_message(
            "ROUND_ANNOUNCEMENT",
            "league_manager",
            league_id="test_league",
            round_id=1,
            matches=[
                {
                    "match_id": "R1M1",
                    "game_type": "even_odd",
                    "player_A_id": "P01",
                    "player_B_id": "P02",
                    "referee_endpoint": "http://localhost:8001/mcp",
                    "player_A_endpoint": "http://localhost:8101/mcp",
                    "player_B_endpoint": "http://localhost:8102/mcp",
                },
            ],
        )
        
        validate_message(announcement.to_dict())
        matches = getattr(announcement, "matches", [])
        assert len(matches) == 1
        assert "player_A_endpoint" in matches[0]
        assert "player_B_endpoint" in matches[0]
        assert matches[0]["player_A_endpoint"] == "http://localhost:8101/mcp"
        assert matches[0]["player_B_endpoint"] == "http://localhost:8102/mcp"

