"""Round-robin tournament scheduler."""

from typing import List, Dict
import itertools


class RoundRobinScheduler:
    """Generates round-robin tournament schedule."""
    
    def generate_schedule(self, player_ids: List[str]) -> Dict[int, List[Dict]]:
        """Generate round-robin tournament schedule.
        
        Args:
            player_ids: List of player IDs to schedule matches for
            
        Returns:
            Dictionary mapping round_id (int) to list of match dictionaries.
            Each match dict contains: match_id, game_type, player_A_id, player_B_id
            
        Algorithm:
        - Generates all possible player pairs using combinations
        - Distributes pairs across rounds to ensure fair scheduling
        - For n players: (n-1) rounds if n is even, n rounds if n is odd
        """
        n = len(player_ids)
        if n < 2:
            return {}
        
        # Create pairs for round-robin
        schedule = {}
        round_num = 1
        
        # Generate all possible pairs
        pairs = list(itertools.combinations(player_ids, 2))
        
        # Distribute pairs into rounds
        # For n players, we need (n-1) rounds if n is even, or n rounds if n is odd
        matches_per_round = n // 2 if n % 2 == 0 else (n - 1) // 2
        
        match_num = 1
        for i in range(0, len(pairs), matches_per_round):
            round_matches = []
            for j in range(matches_per_round):
                if i + j < len(pairs):
                    player_A, player_B = pairs[i + j]
                    round_matches.append({
                        "match_id": f"R{round_num}M{match_num}",
                        "game_type": "even_odd",
                        "player_A_id": player_A,
                        "player_B_id": player_B,
                    })
                    match_num += 1
            
            if round_matches:
                schedule[round_num] = round_matches
                round_num += 1
        
        return schedule

