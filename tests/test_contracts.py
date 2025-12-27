"""Test protocol message compliance with the league.v2 protocol specification."""

import pytest
from datetime import datetime, timezone
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "SHARED"))

from league_sdk import Message, create_message, validate_message


class TestContractsCompliance:
    """Test that messages comply with the league.v2 protocol specification."""
    
    def test_referee_register_request(self):
        """Test REFEREE_REGISTER_REQUEST message structure."""
        message = create_message(
            "REFEREE_REGISTER_REQUEST",
            "referee:REF01",
            referee_meta={
                "display_name": "Referee Alpha",
                "version": "1.0.0",
                "game_types": ["even_odd"],
                "contact_endpoint": "http://localhost:8001/mcp",
                "max_concurrent_matches": 2,
            },
        )
        
        msg_dict = message.to_dict()
        
        # Required fields for REFEREE_REGISTER_REQUEST
        assert msg_dict["protocol"] == "league.v2"
        assert msg_dict["message_type"] == "REFEREE_REGISTER_REQUEST"
        assert msg_dict["sender"] == "referee:REF01"
        assert "timestamp" in msg_dict
        assert "conversation_id" in msg_dict
        assert "referee_meta" in msg_dict
        
        # Required referee_meta fields
        meta = msg_dict["referee_meta"]
        assert "display_name" in meta
        assert "version" in meta
        assert "game_types" in meta
        assert "contact_endpoint" in meta
        assert "max_concurrent_matches" in meta
        
        validate_message(msg_dict)
    
    def test_referee_register_response(self):
        """Test REFEREE_REGISTER_RESPONSE matches protocol specification"""
        message = create_message(
            "REFEREE_REGISTER_RESPONSE",
            "league_manager",
            status="ACCEPTED",
            referee_id="REF01",
            reason=None,
        )
        
        msg_dict = message.to_dict()
        
        # Required fields for REFEREE_REGISTER_REQUEST
        assert msg_dict["message_type"] == "REFEREE_REGISTER_RESPONSE"
        assert msg_dict["status"] == "ACCEPTED"
        assert msg_dict["referee_id"] == "REF01"
        assert "reason" in msg_dict  # Optional but should be present
    
    def test_player_register_request(self):
        """Test LEAGUE_REGISTER_REQUEST matches protocol specification"""
        message = create_message(
            "LEAGUE_REGISTER_REQUEST",
            "player:P01",
            player_meta={
                "display_name": "Agent Alpha",
                "version": "1.0.0",
                "game_types": ["even_odd"],
                "contact_endpoint": "http://localhost:8101/mcp",
            },
        )
        
        msg_dict = message.to_dict()
        
        # Required fields 3.1
        assert msg_dict["message_type"] == "LEAGUE_REGISTER_REQUEST"
        assert "player_meta" in msg_dict
        
        meta = msg_dict["player_meta"]
        assert "display_name" in meta
        assert "version" in meta
        assert "game_types" in meta
        assert "contact_endpoint" in meta
    
    def test_player_register_response(self):
        """Test LEAGUE_REGISTER_RESPONSE matches protocol specification"""
        message = create_message(
            "LEAGUE_REGISTER_RESPONSE",
            "league_manager",
            status="ACCEPTED",
            player_id="P01",
            reason=None,
        )
        
        msg_dict = message.to_dict()
        assert msg_dict["message_type"] == "LEAGUE_REGISTER_RESPONSE"
        assert msg_dict["status"] == "ACCEPTED"
        assert msg_dict["player_id"] == "P01"
    
    def test_game_invitation(self):
        """Test GAME_INVITATION matches protocol specification"""
        message = create_message(
            "GAME_INVITATION",
            "referee:REF01",
            league_id="league_2025_even_odd",
            round_id=1,
            match_id="R1M1",
            game_type="even_odd",
            role_in_match="PLAYER_A",
            opponent_id="P02",
        )
        
        msg_dict = message.to_dict()
        
        # Required fields 2.2
        assert msg_dict["message_type"] == "GAME_INVITATION"
        assert msg_dict["league_id"] == "league_2025_even_odd"
        assert msg_dict["round_id"] == 1
        assert msg_dict["match_id"] == "R1M1"
        assert msg_dict["game_type"] == "even_odd"
        assert msg_dict["role_in_match"] == "PLAYER_A"
        assert msg_dict["opponent_id"] == "P02"
        assert "conversation_id" in msg_dict
    
    def test_game_join_ack(self):
        """Test GAME_JOIN_ACK matches protocol specification"""
        message = create_message(
            "GAME_JOIN_ACK",
            "player:P01",
            match_id="R1M1",
            player_id="P01",
            arrival_timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            accept=True,
        )
        
        msg_dict = message.to_dict()
        
        # Required fields 3.2
        assert msg_dict["message_type"] == "GAME_JOIN_ACK"
        assert msg_dict["match_id"] == "R1M1"
        assert msg_dict["player_id"] == "P01"
        assert "arrival_timestamp" in msg_dict
        assert msg_dict["accept"] is True
    
    def test_choose_parity_call(self):
        """Test CHOOSE_PARITY_CALL matches protocol specification"""
        deadline = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        message = create_message(
            "CHOOSE_PARITY_CALL",
            "referee:REF01",
            match_id="R1M1",
            player_id="P01",
            game_type="even_odd",
            context={
                "opponent_id": "P02",
                "round_id": 1,
                "your_standings": {
                    "wins": 2,
                    "losses": 1,
                    "draws": 0,
                },
            },
            deadline=deadline,
        )
        
        msg_dict = message.to_dict()
        
        # Required fields 2.3
        assert msg_dict["message_type"] == "CHOOSE_PARITY_CALL"
        assert msg_dict["match_id"] == "R1M1"
        assert msg_dict["player_id"] == "P01"
        assert msg_dict["game_type"] == "even_odd"
        assert "context" in msg_dict
        assert "deadline" in msg_dict
        assert msg_dict["deadline"] == deadline
    
    def test_choose_parity_response(self):
        """Test CHOOSE_PARITY_RESPONSE matches protocol specification"""
        message = create_message(
            "CHOOSE_PARITY_RESPONSE",
            "player:P01",
            match_id="R1M1",
            player_id="P01",
            parity_choice="even",
        )
        
        msg_dict = message.to_dict()
        
        # Required fields 3.3
        assert msg_dict["message_type"] == "CHOOSE_PARITY_RESPONSE"
        assert msg_dict["match_id"] == "R1M1"
        assert msg_dict["player_id"] == "P01"
        assert msg_dict["parity_choice"] == "even"
        assert msg_dict["parity_choice"] in ["even", "odd"]
    
    def test_game_over(self):
        """Test GAME_OVER matches protocol specification"""
        message = create_message(
            "GAME_OVER",
            "referee:REF01",
            match_id="R1M1",
            game_type="even_odd",
            game_result={
                "status": "WIN",
                "winner_player_id": "P01",
                "drawn_number": 8,
                "number_parity": "even",
                "choices": {
                    "P01": "even",
                    "P02": "odd",
                },
                "reason": "P01 chose even, number was 8 (even)",
            },
        )
        
        msg_dict = message.to_dict()
        
        # Required fields 2.4
        assert msg_dict["message_type"] == "GAME_OVER"
        assert msg_dict["match_id"] == "R1M1"
        assert msg_dict["game_type"] == "even_odd"
        assert "game_result" in msg_dict
        
        result = msg_dict["game_result"]
        assert result["status"] in ["WIN", "DRAW", "TECHNICAL_LOSS"]
        assert "winner_player_id" in result
        assert "drawn_number" in result
        assert "number_parity" in result
        assert "choices" in result
        assert "reason" in result
    
    def test_match_result_report(self):
        """Test MATCH_RESULT_REPORT matches protocol specification"""
        message = create_message(
            "MATCH_RESULT_REPORT",
            "referee:REF01",
            league_id="league_2025_even_odd",
            round_id=1,
            match_id="R1M1",
            game_type="even_odd",
            result={
                "winner": "P01",
                "score": {
                    "P01": 3,
                    "P02": 0,
                },
                "details": {
                    "drawn_number": 8,
                    "choices": {
                        "P01": "even",
                        "P02": "odd",
                    },
                },
            },
        )
        
        msg_dict = message.to_dict()
        
        # Required fields 2.5
        assert msg_dict["message_type"] == "MATCH_RESULT_REPORT"
        assert msg_dict["league_id"] == "league_2025_even_odd"
        assert msg_dict["round_id"] == 1
        assert msg_dict["match_id"] == "R1M1"
        assert msg_dict["game_type"] == "even_odd"
        assert "result" in msg_dict
        
        result = msg_dict["result"]
        assert "winner" in result
        assert "score" in result
        assert "details" in result
    
    def test_round_announcement(self):
        """Test ROUND_ANNOUNCEMENT matches protocol specification"""
        message = create_message(
            "ROUND_ANNOUNCEMENT",
            "league_manager",
            league_id="league_2025_even_odd",
            round_id=1,
            matches=[
                {
                    "match_id": "R1M1",
                    "game_type": "even_odd",
                    "player_A_id": "P01",
                    "player_B_id": "P02",
                    "referee_endpoint": "http://localhost:8001/mcp",
                },
            ],
        )
        
        msg_dict = message.to_dict()
        
        # Required fields 1.1
        assert msg_dict["message_type"] == "ROUND_ANNOUNCEMENT"
        assert msg_dict["league_id"] == "league_2025_even_odd"
        assert msg_dict["round_id"] == 1
        assert "matches" in msg_dict
        assert isinstance(msg_dict["matches"], list)
        
        match = msg_dict["matches"][0]
        assert "match_id" in match
        assert "game_type" in match
        assert "player_A_id" in match
        assert "player_B_id" in match
        assert "referee_endpoint" in match
    
    def test_league_query(self):
        """Test LEAGUE_QUERY matches protocol specification"""
        message = create_message(
            "LEAGUE_QUERY",
            "player:P01",
            auth_token="tok_p01_abc123",
            league_id="league_2025_even_odd",
            query_type="GET_STANDINGS",
            query_params={},
        )
        
        msg_dict = message.to_dict()
        
        # Required fields 3.4
        assert msg_dict["message_type"] == "LEAGUE_QUERY"
        assert msg_dict["auth_token"] == "tok_p01_abc123"
        assert msg_dict["league_id"] == "league_2025_even_odd"
        assert msg_dict["query_type"] == "GET_STANDINGS"
        assert "query_params" in msg_dict
    
    def test_league_error(self):
        """Test LEAGUE_ERROR matches protocol specification"""
        message = create_message(
            "LEAGUE_ERROR",
            "league_manager",
            error_code="E012",
            error_description="AUTH_TOKEN_INVALID",
            original_message_type="LEAGUE_QUERY",
            context={
                "provided_token": "tok-invalid-xxx",
                "expected_format": "tok-{agent_id}-{hash}",
            },
        )
        
        msg_dict = message.to_dict()
        
        # Required fields 1.6
        assert msg_dict["message_type"] == "LEAGUE_ERROR"
        assert msg_dict["error_code"] == "E012"
        assert msg_dict["error_description"] == "AUTH_TOKEN_INVALID"
        assert "original_message_type" in msg_dict
        assert "context" in msg_dict
    
    def test_start_league(self):
        """Test START_LEAGUE matches protocol specification"""
        message = create_message(
            "START_LEAGUE",
            "launcher",
            league_id="league_2025_even_odd",
        )
        
        msg_dict = message.to_dict()
        
        # Required fields 4.1
        assert msg_dict["message_type"] == "START_LEAGUE"
        assert msg_dict["league_id"] == "league_2025_even_odd"
        assert msg_dict["sender"] == "launcher"

