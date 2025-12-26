"""Player strategy implementations."""

import random
from typing import Dict, Optional
from league_sdk.repositories import HistoryRepository


class Strategy:
    """Player strategy for making choices."""
    
    def __init__(self, logger, history_repo: HistoryRepository):
        self.logger = logger
        self.history_repo = history_repo
    
    def choose_parity(self, opponent_id: Optional[str], context: Dict) -> str:
        """Choose parity (even or odd).
        
        This is a simple random strategy. Can be extended with:
        - History-based analysis
        - Pattern detection
        - LLM-guided decisions
        """
        # Simple random strategy
        return random.choice(["even", "odd"])
    
    def choose_parity_history_based(self, opponent_id: Optional[str], context: Dict) -> str:
        """History-based strategy."""
        if not opponent_id:
            return random.choice(["even", "odd"])
        
        # Analyze opponent's history
        history = self.history_repo.get_history()
        opponent_games = [
            g for g in history
            if g.get("opponent") == opponent_id
        ]
        
        if not opponent_games:
            return random.choice(["even", "odd"])
        
        # Count opponent's choices
        even_count = sum(1 for g in opponent_games if g.get("opponent_choice") == "even")
        odd_count = sum(1 for g in opponent_games if g.get("opponent_choice") == "odd")
        
        # Counter opponent's most common choice
        if even_count > odd_count:
            return "odd"  # Counter their even preference
        elif odd_count > even_count:
            return "even"  # Counter their odd preference
        else:
            return random.choice(["even", "odd"])

