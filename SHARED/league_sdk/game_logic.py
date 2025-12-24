"""Game logic for Even/Odd game."""

import random
from typing import Dict, Optional, Literal
from dataclasses import dataclass


ParityChoice = Literal["even", "odd"]


@dataclass
class GameResult:
    """Game result."""
    winner: Optional[str]
    drawn_number: int
    number_parity: ParityChoice
    choices: Dict[str, ParityChoice]
    score: Dict[str, int]
    reason: str


class EvenOddGame:
    """Even/Odd game logic."""
    
    MIN_NUMBER = 1
    MAX_NUMBER = 10
    
    @staticmethod
    def validate_choice(choice: str) -> bool:
        """Validate parity choice."""
        return choice.lower() in ["even", "odd"]
    
    @staticmethod
    def draw_number() -> int:
        """Draw random number."""
        return random.randint(EvenOddGame.MIN_NUMBER, EvenOddGame.MAX_NUMBER)
    
    @staticmethod
    def get_parity(number: int) -> ParityChoice:
        """Get parity of number."""
        return "even" if number % 2 == 0 else "odd"
    
    @classmethod
    def play_game(
        cls,
        player_A_id: str,
        player_B_id: str,
        choice_A: ParityChoice,
        choice_B: ParityChoice,
    ) -> GameResult:
        """Play a game and determine winner."""
        # Validate choices
        if not cls.validate_choice(choice_A) or not cls.validate_choice(choice_B):
            raise ValueError("Invalid parity choice")
        
        # Draw number
        drawn_number = cls.draw_number()
        number_parity = cls.get_parity(drawn_number)
        
        # Determine winner
        winner = None
        score = {player_A_id: 0, player_B_id: 0}
        reason = ""
        
        if choice_A == number_parity:
            winner = player_A_id
            score[player_A_id] = 3
            reason = f"{player_A_id} chose {choice_A}, number was {drawn_number} ({number_parity})"
        elif choice_B == number_parity:
            winner = player_B_id
            score[player_B_id] = 3
            reason = f"{player_B_id} chose {choice_B}, number was {drawn_number} ({number_parity})"
        else:
            # Both chose wrong (shouldn't happen, but handle it)
            reason = f"Both players chose incorrectly. Number was {drawn_number} ({number_parity})"
        
        return GameResult(
            winner=winner,
            drawn_number=drawn_number,
            number_parity=number_parity,
            choices={player_A_id: choice_A, player_B_id: choice_B},
            score=score,
            reason=reason,
        )

