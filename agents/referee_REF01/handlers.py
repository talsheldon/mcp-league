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
        
        raise ValueError(f"Unknown message type: {message.message_type}")
    
    async def handle_round_announcement(self, message: Message) -> Message:
        """Handle round announcement and start matches."""
        matches = getattr(message, "matches", [])
        round_id = getattr(message, "round_id", 0)
        
        # Start games for matches assigned to this referee
        for match in matches:
            referee_endpoint = match.get("referee_endpoint", "")
            if f":{self.referee.port}" in referee_endpoint:
                match_id = match.get("match_id")
                player_A_id = match.get("player_A_id")
                player_B_id = match.get("player_B_id")
                
                # Get player endpoints from league manager (simplified - in real implementation)
                # For now, assume players are on standard ports
                player_A_endpoint = f"http://localhost:{8100 + int(player_A_id[1:])}/mcp"
                player_B_endpoint = f"http://localhost:{8100 + int(player_B_id[1:])}/mcp"
                
                # Start game asynchronously
                asyncio.create_task(
                    self.referee.game_manager.run_game(
                        self.referee,
                        match_id,
                        round_id,
                        player_A_id,
                        player_B_id,
                        player_A_endpoint,
                        player_B_endpoint,
                    )
                )
        
        return create_message(
            "ACK",
            f"referee:{self.referee.referee_id}",
            conversation_id=message.conversation_id,
        )

