"""Message handlers for Referee."""

import asyncio
from typing import Dict, Optional
from datetime import datetime, timezone, timedelta
import httpx
from league_sdk import Message, create_message
from league_sdk.game_logic import EvenOddGame


class MessageHandler:
    """Handles incoming messages for Referee."""
    
    def __init__(self, referee):
        self.referee = referee
        self.logger = referee.logger
    
    async def handle(self, message: Message) -> Message:
        """Route message to appropriate handler."""
        # Referee doesn't receive many message types directly
        # Most communication is initiated by referee
        if message.message_type == "ROUND_ANNOUNCEMENT":
            return await self.handle_round_announcement(message)
        elif message.message_type == "LEAGUE_COMPLETED":
            # Acknowledge league completion
            self.logger.info(f"League {getattr(message, 'league_id', 'unknown')} completed")
            return create_message(
                "ACK",
                f"referee:{self.referee.referee_id}",
                conversation_id=message.conversation_id,
            )
        
        raise ValueError(f"Unknown message type: {message.message_type}")
    
    async def handle_round_announcement(self, message: Message) -> Message:
        """Handle round announcement and start matches assigned to this referee.
        
        Args:
            message: ROUND_ANNOUNCEMENT message with matches list
            
        Returns:
            ACK message confirming receipt
            
        For each match assigned to this referee:
        - Validates player endpoints are present
        - Checks max_concurrent_matches limit
        - Starts game asynchronously
        - Tracks active games for concurrency control
        """
        matches = getattr(message, "matches", [])
        round_id = getattr(message, "round_id", 0)
        
        # Start games for matches assigned to this referee
        for match in matches:
            referee_endpoint = match.get("referee_endpoint", "")
            if f":{self.referee.port}" in referee_endpoint:
                match_id = match.get("match_id")
                player_A_id = match.get("player_A_id")
                player_B_id = match.get("player_B_id")
                
                # Get player endpoints from ROUND_ANNOUNCEMENT message
                player_A_endpoint = match.get("player_A_endpoint")
                player_B_endpoint = match.get("player_B_endpoint")
                
                if not player_A_endpoint or not player_B_endpoint:
                    self.logger.error(f"Missing player endpoints in match {match_id}")
                    continue
                
                # Check max concurrent matches limit
                if len(self.referee.active_games) >= self.referee.max_concurrent_matches:
                    self.logger.warning(
                        f"Cannot start game {match_id}: max_concurrent_matches ({self.referee.max_concurrent_matches}) reached. "
                        f"Active games: {len(self.referee.active_games)}"
                    )
                    continue
                
                # Track active game
                self.referee.active_games.add(match_id)
                
                # Start game asynchronously
                async def run_and_cleanup():
                    try:
                        await self.referee.game_manager.run_game(
                            self.referee,
                            match_id,
                            round_id,
                            player_A_id,
                            player_B_id,
                            player_A_endpoint,
                            player_B_endpoint,
                        )
                    finally:
                        # Remove from active games when done
                        self.referee.active_games.discard(match_id)
                
                asyncio.create_task(run_and_cleanup())
        
        return create_message(
            "ACK",
            f"referee:{self.referee.referee_id}",
            conversation_id=message.conversation_id,
        )

