"""Tests for game logic."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "SHARED"))

from league_sdk.game_logic import EvenOddGame, GameResult


class TestEvenOddGame:
    """Test Even/Odd game logic."""
    
    def test_validate_choice(self):
        """Test choice validation."""
        assert EvenOddGame.validate_choice("even") is True
        assert EvenOddGame.validate_choice("odd") is True
        assert EvenOddGame.validate_choice("EVEN") is True
        assert EvenOddGame.validate_choice("ODD") is True
        assert EvenOddGame.validate_choice("invalid") is False
        assert EvenOddGame.validate_choice("") is False
    
    def test_draw_number(self):
        """Test number drawing."""
        for _ in range(100):
            number = EvenOddGame.draw_number()
            assert EvenOddGame.MIN_NUMBER <= number <= EvenOddGame.MAX_NUMBER
    
    def test_get_parity(self):
        """Test parity calculation."""
        assert EvenOddGame.get_parity(2) == "even"
        assert EvenOddGame.get_parity(4) == "even"
        assert EvenOddGame.get_parity(6) == "even"
        assert EvenOddGame.get_parity(8) == "even"
        assert EvenOddGame.get_parity(10) == "even"
        
        assert EvenOddGame.get_parity(1) == "odd"
        assert EvenOddGame.get_parity(3) == "odd"
        assert EvenOddGame.get_parity(5) == "odd"
        assert EvenOddGame.get_parity(7) == "odd"
        assert EvenOddGame.get_parity(9) == "odd"
    
    def test_play_game_player_A_wins(self):
        """Test game where player A wins."""
        # Mock random to return even number
        import random
        original_randint = random.randint
        
        def mock_randint(a, b):
            return 8  # Even number
        
        random.randint = mock_randint
        
        try:
            result = EvenOddGame.play_game("P01", "P02", "even", "odd")
            assert result.winner == "P01"
            assert result.drawn_number == 8
            assert result.number_parity == "even"
            assert result.score["P01"] == 3
            assert result.score["P02"] == 0
        finally:
            random.randint = original_randint
    
    def test_play_game_player_B_wins(self):
        """Test game where player B wins."""
        import random
        original_randint = random.randint
        
        def mock_randint(a, b):
            return 7  # Odd number
        
        random.randint = mock_randint
        
        try:
            result = EvenOddGame.play_game("P01", "P02", "even", "odd")
            assert result.winner == "P02"
            assert result.drawn_number == 7
            assert result.number_parity == "odd"
            assert result.score["P01"] == 0
            assert result.score["P02"] == 3
        finally:
            random.randint = original_randint
    
    def test_play_game_invalid_choice(self):
        """Test game with invalid choice."""
        with pytest.raises(ValueError):
            EvenOddGame.play_game("P01", "P02", "invalid", "odd")

