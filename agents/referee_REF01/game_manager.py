"""Game management for Referee."""

from typing import Dict, Optional
from datetime import datetime, timezone, timedelta
from pathlib import Path
import json
import httpx
from league_sdk import Message, create_message
from league_sdk.game_logic import EvenOddGame


class GameManager:
    """Manages game state and flow."""
    
    def __init__(self, logger, referee=None):
        """Initialize GameManager.
        
        Args:
            logger: Logger instance for logging
            referee: Referee instance for accessing config and state
        """
        self.logger = logger
        self.referee = referee
        self.active_games: Dict[str, Dict] = {}
        self._timeout_config = self._load_timeout_config()
    
    def _load_timeout_config(self) -> Dict[str, int]:
        """Load timeout configuration from system.json.
        
        Returns:
            Dictionary with timeout values in seconds
        """
        try:
            config_path = Path("SHARED/config/system.json")
            if config_path.exists():
                with open(config_path, "r") as f:
                    config = json.load(f)
                    return config.get("default_timeouts", {
                        "game_join": 5,
                        "choose_parity": 30,
                        "registration": 10,
                        "default": 10,
                    })
        except Exception as e:
            self.logger.warning(f"Failed to load timeout config: {e}")
        
        # Default values
        return {
            "game_join": 5,
            "choose_parity": 30,
            "registration": 10,
            "default": 10,
        }
    
    async def run_game(
        self,
        referee,
        match_id: str,
        round_id: int,
        player_A_id: str,
        player_B_id: str,
        player_A_endpoint: str,
        player_B_endpoint: str,
    ) -> None:
        """Run a complete game from invitation to result reporting.
        
        Args:
            referee: Referee instance for sending messages and reporting results
            match_id: Unique identifier for this match
            round_id: Round number this match belongs to
            player_A_id: ID of player A
            player_B_id: ID of player B
            player_A_endpoint: HTTP endpoint for player A
            player_B_endpoint: HTTP endpoint for player B
            
        The game flow:
        1. Send game invitations to both players
        2. Wait for players to join (with timeout)
        3. Collect parity choices from both players (with deadline)
        4. Determine winner using EvenOddGame
        5. Send game results to both players
        6. Report match result to League Manager
        """
        try:
            self.logger.info(f"Starting game {match_id}: {player_A_id} vs {player_B_id}")
            
            # Step 1: Send game invitations
            invitation_A = create_message(
                "GAME_INVITATION",
                f"referee:{referee.referee_id}",
                league_id=referee.league_id,
                round_id=round_id,
                match_id=match_id,
                game_type="even_odd",
                role_in_match="PLAYER_A",
                opponent_id=player_B_id,
            )
            
            invitation_B = create_message(
                "GAME_INVITATION",
                f"referee:{referee.referee_id}",
                league_id=referee.league_id,
                round_id=round_id,
                match_id=match_id,
                game_type="even_odd",
                role_in_match="PLAYER_B",
                opponent_id=player_A_id,
            )
            
            # Send invitations
            ack_A = await referee.send_to_player(player_A_endpoint, invitation_A)
            ack_B = await referee.send_to_player(player_B_endpoint, invitation_B)
            
            if not ack_A or not ack_B:
                self.logger.error(f"Players did not join game {match_id}")
                return
            
            if not getattr(ack_A, "accept", False) or not getattr(ack_B, "accept", False):
                self.logger.error(f"Players declined game {match_id}")
                return
            
            # Step 2: Collect choices
            timeout_seconds = self._timeout_config.get("choose_parity", 30)
            deadline = (datetime.now(timezone.utc) + timedelta(seconds=timeout_seconds)).isoformat().replace("+00:00", "Z")
            
            choice_call_A = create_message(
                "CHOOSE_PARITY_CALL",
                f"referee:{referee.referee_id}",
                match_id=match_id,
                player_id=player_A_id,
                game_type="even_odd",
                context={
                    "opponent_id": player_B_id,
                    "round_id": round_id,
                },
                deadline=deadline,
            )
            
            choice_call_B = create_message(
                "CHOOSE_PARITY_CALL",
                f"referee:{referee.referee_id}",
                match_id=match_id,
                player_id=player_B_id,
                game_type="even_odd",
                context={
                    "opponent_id": player_A_id,
                    "round_id": round_id,
                },
                deadline=deadline,
            )
            
            # Send choice calls
            response_A = await referee.send_to_player(player_A_endpoint, choice_call_A)
            response_B = await referee.send_to_player(player_B_endpoint, choice_call_B)
            
            if not response_A or not response_B:
                self.logger.error(f"Players did not respond with choices for {match_id}")
                # Handle timeout - technical loss
                return
            
            choice_A = getattr(response_A, "parity_choice", None)
            choice_B = getattr(response_B, "parity_choice", None)
            
            if not choice_A or not choice_B:
                self.logger.error(f"Invalid choices for {match_id}")
                return
            
            # Step 3: Play game
            game_result = EvenOddGame.play_game(
                player_A_id,
                player_B_id,
                choice_A,
                choice_B,
            )
            
            # Step 4: Send game over to players
            game_over = create_message(
                "GAME_OVER",
                f"referee:{referee.referee_id}",
                match_id=match_id,
                game_type="even_odd",
                game_result={
                    "status": "WIN" if game_result.winner else "DRAW",
                    "winner_player_id": game_result.winner,
                    "drawn_number": game_result.drawn_number,
                    "number_parity": game_result.number_parity,
                    "choices": game_result.choices,
                    "reason": game_result.reason,
                },
            )
            
            await referee.send_to_player(player_A_endpoint, game_over)
            await referee.send_to_player(player_B_endpoint, game_over)
            
            # Step 5: Report to league manager
            await referee.report_match_result(
                match_id,
                {
                    "round_id": round_id,
                    "winner": game_result.winner,
                    "score": game_result.score,
                    "details": {
                        "drawn_number": game_result.drawn_number,
                        "choices": game_result.choices,
                    },
                },
            )
            
            self.logger.info(f"Game {match_id} completed: winner={game_result.winner}")
            
        except Exception as e:
            self.logger.error(f"Error running game {match_id}: {e}", exc_info=True)

