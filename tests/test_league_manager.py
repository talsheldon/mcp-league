"""Tests for League Manager."""

import pytest
import tempfile
from pathlib import Path
import sys
import asyncio
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).parent.parent / "SHARED"))
sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "league_manager"))

from league_sdk import Message, create_message
from handlers import MessageHandler


class TestLeagueManagerHandlers:
    """Test League Manager message handlers."""
    
    @pytest.fixture
    def mock_manager(self):
        """Create mock league manager."""
        from league_sdk.repositories import StandingsRepository
        import tempfile
        from pathlib import Path
        
        manager = Mock()
        manager.registered_players = {}
        manager.registered_referees = {}
        manager.auth_tokens = {}
        manager.league_id = "test_league"
        manager.current_round = 1
        manager.total_rounds = 1
        manager.league_started = False
        manager.matches_by_round = {}
        manager.logger = Mock()
        
        # Use real repository for standings
        temp_dir = Path(tempfile.mkdtemp())
        manager.standings_repo = StandingsRepository(temp_dir, "test_league")
        manager.completed_matches = set()
        manager.generate_auth_token = lambda agent_id: f"tok_{agent_id}_abc123"
        manager.validate_auth_token = lambda agent_id, token: token == f"tok_{agent_id}_abc123"
        
        return manager
    
    @pytest.fixture
    def handler(self, mock_manager):
        """Create message handler."""
        return MessageHandler(mock_manager)
    
    def test_handle_referee_register(self, handler, mock_manager):
        """Test referee registration."""
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
        
        response = asyncio.run(handler.handle(message))
        
        assert response.message_type == "REFEREE_REGISTER_RESPONSE"
        assert getattr(response, "status") == "ACCEPTED"
        assert "REF" in getattr(response, "referee_id")
        assert len(mock_manager.registered_referees) == 1
    
    def test_handle_player_register(self, handler, mock_manager):
        """Test player registration."""
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
        
        response = asyncio.run(handler.handle(message))
        
        assert response.message_type == "LEAGUE_REGISTER_RESPONSE"
        assert getattr(response, "status") == "ACCEPTED"
        assert "P" in getattr(response, "player_id")
        assert len(mock_manager.registered_players) == 1
    
    def test_handle_match_result(self, handler, mock_manager):
        """Test match result handling."""
        # Setup: Initialize players in standings
        mock_manager.standings_repo.initialize_player("P01", "Player 1")
        mock_manager.standings_repo.initialize_player("P02", "Player 2")
        
        # Mock the async HTTP calls to avoid actual network requests
        import asyncio
        from unittest.mock import patch, AsyncMock
        
        async def _test():
            with patch('agents.league_manager.handlers.httpx.AsyncClient') as mock_client:
                # Mock the async context manager
                mock_client.return_value.__aenter__ = AsyncMock(return_value=AsyncMock())
                mock_client.return_value.__aexit__ = AsyncMock(return_value=None)
                
                message = create_message(
                    "MATCH_RESULT_REPORT",
                    "referee:REF01",
                    league_id="test_league",
                    match_id="R1M1",
                    round_id=1,
                    game_type="even_odd",
                    result={
                        "winner": "P01",
                        "score": {"P01": 3, "P02": 0},
                        "details": {
                            "choices": {"P01": "even", "P02": "odd"},
                        },
                    },
                )
                
                response = await handler.handle(message)
                
                assert response.message_type == "MATCH_RESULT_ACK"
                assert getattr(response, "status") == "recorded"
                assert "R1M1" in mock_manager.completed_matches
        
        asyncio.run(_test())
