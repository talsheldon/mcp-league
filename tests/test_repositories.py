"""Tests for repositories."""

import pytest
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "SHARED"))

from league_sdk.repositories import (
    StandingsRepository,
    MatchRepository,
    HistoryRepository,
    PlayerStanding,
    MatchResult,
)


class TestStandingsRepository:
    """Test StandingsRepository."""
    
    def test_initialize_player(self):
        """Test player initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = StandingsRepository(Path(tmpdir), "test_league")
            repo.initialize_player("P01", "Player One")
            
            standing = repo.get_player_standing("P01")
            assert standing is not None
            assert standing.player_id == "P01"
            assert standing.display_name == "Player One"
            assert standing.played == 0
            assert standing.points == 0
    
    def test_update_match_result_win(self):
        """Test updating standings with win."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = StandingsRepository(Path(tmpdir), "test_league")
            repo.initialize_player("P01", "Player One")
            repo.initialize_player("P02", "Player Two")
            
            repo.update_match_result("P01", "P02", "P01", {"P01": 3, "P02": 0})
            
            standing_P01 = repo.get_player_standing("P01")
            assert standing_P01.wins == 1
            assert standing_P01.points == 3
            assert standing_P01.played == 1
            
            standing_P02 = repo.get_player_standing("P02")
            assert standing_P02.losses == 1
            assert standing_P02.points == 0
            assert standing_P02.played == 1
    
    def test_update_match_result_draw(self):
        """Test updating standings with draw."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = StandingsRepository(Path(tmpdir), "test_league")
            repo.initialize_player("P01", "Player One")
            repo.initialize_player("P02", "Player Two")
            
            repo.update_match_result("P01", "P02", None, {"P01": 1, "P02": 1})
            
            standing_P01 = repo.get_player_standing("P01")
            assert standing_P01.draws == 1
            assert standing_P01.points == 1
            
            standing_P02 = repo.get_player_standing("P02")
            assert standing_P02.draws == 1
            assert standing_P02.points == 1
    
    def test_get_standings_ranking(self):
        """Test standings ranking."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = StandingsRepository(Path(tmpdir), "test_league")
            repo.initialize_player("P01", "Player One")
            repo.initialize_player("P02", "Player Two")
            repo.initialize_player("P03", "Player Three")
            
            # P01 wins
            repo.update_match_result("P01", "P02", "P01", {"P01": 3, "P02": 0})
            # P03 wins
            repo.update_match_result("P01", "P03", "P03", {"P01": 0, "P03": 3})
            
            standings = repo.get_standings()
            assert standings[0].player_id == "P03"  # Highest points
            assert standings[0].rank == 1


class TestMatchRepository:
    """Test MatchRepository."""
    
    def test_save_and_load_match(self):
        """Test saving and loading match."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = MatchRepository(Path(tmpdir), "test_league")
            
            result = MatchResult(
                match_id="R1M1",
                round_id=1,
                player_A_id="P01",
                player_B_id="P02",
                winner="P01",
                score={"P01": 3, "P02": 0},
                details={"drawn_number": 8, "choices": {"P01": "even", "P02": "odd"}},
            )
            
            repo.save_match("R1M1", result)
            
            loaded = repo.load_match("R1M1")
            assert loaded is not None
            assert loaded.match_id == "R1M1"
            assert loaded.winner == "P01"


class TestHistoryRepository:
    """Test HistoryRepository."""
    
    def test_add_game(self):
        """Test adding game to history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = HistoryRepository(Path(tmpdir), "P01")
            
            game_data = {
                "match_id": "R1M1",
                "opponent": "P02",
                "my_choice": "even",
                "opponent_choice": "odd",
                "drawn_number": 8,
                "winner": "P01",
                "won": True,
            }
            
            repo.add_game(game_data)
            
            history = repo.get_history()
            assert len(history) == 1
            assert history[0]["match_id"] == "R1M1"
            assert history[0]["won"] is True

