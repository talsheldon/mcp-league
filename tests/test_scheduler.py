"""Tests for scheduler."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "league_manager"))

from scheduler import RoundRobinScheduler


class TestRoundRobinScheduler:
    """Test RoundRobinScheduler."""
    
    def test_generate_schedule_two_players(self):
        """Test schedule for 2 players."""
        scheduler = RoundRobinScheduler()
        schedule = scheduler.generate_schedule(["P01", "P02"])
        
        assert len(schedule) == 1
        assert len(schedule[1]) == 1
        assert schedule[1][0]["player_A_id"] in ["P01", "P02"]
        assert schedule[1][0]["player_B_id"] in ["P01", "P02"]
        assert schedule[1][0]["player_A_id"] != schedule[1][0]["player_B_id"]
    
    def test_generate_schedule_four_players(self):
        """Test schedule for 4 players."""
        scheduler = RoundRobinScheduler()
        schedule = scheduler.generate_schedule(["P01", "P02", "P03", "P04"])
        
        # 4 players = 6 matches total, 2 matches per round, 3 rounds
        total_matches = sum(len(matches) for matches in schedule.values())
        assert total_matches == 6
        
        # Check all players appear
        all_players = set()
        for round_matches in schedule.values():
            for match in round_matches:
                all_players.add(match["player_A_id"])
                all_players.add(match["player_B_id"])
        
        assert all_players == {"P01", "P02", "P03", "P04"}
    
    def test_generate_schedule_three_players(self):
        """Test schedule for 3 players."""
        scheduler = RoundRobinScheduler()
        schedule = scheduler.generate_schedule(["P01", "P02", "P03"])
        
        # 3 players = 3 matches total
        total_matches = sum(len(matches) for matches in schedule.values())
        assert total_matches == 3

