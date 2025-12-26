"""Message handlers for Player."""

from typing import Dict, Optional
from datetime import datetime, timezone
from league_sdk import Message, create_message


class MessageHandler:
    """Handles incoming messages for Player."""
    
    def __init__(self, player):
        self.player = player
        self.logger = player.logger
    
    async def handle(self, message: Message) -> Message:
        """Route message to appropriate handler."""
        handler_map = {
            "ROUND_ANNOUNCEMENT": self.handle_round_announcement,
            "GAME_INVITATION": self.handle_game_invitation,
            "CHOOSE_PARITY_CALL": self.handle_choose_parity,
            "GAME_OVER": self.handle_game_over,
            "LEAGUE_STANDINGS_UPDATE": self.handle_standings_update,
            "ROUND_COMPLETED": self.handle_round_completed,
            "LEAGUE_COMPLETED": self.handle_league_completed,
        }
        
        handler = handler_map.get(message.message_type)
        if not handler:
            raise ValueError(f"Unknown message type: {message.message_type}")
        
        return await handler(message)
    
    async def handle_game_invitation(self, message: Message) -> Message:
        """Handle game invitation."""
        match_id = getattr(message, "match_id")
        opponent_id = getattr(message, "opponent_id")
        
        self.logger.info(f"Received game invitation: {match_id} vs {opponent_id}")
        
        # Store current game info
        self.player.current_game = {
            "match_id": match_id,
            "opponent_id": opponent_id,
            "referee_endpoint": None,  # Would be extracted from message in real implementation
        }
        
        # Accept invitation
        return create_message(
            "GAME_JOIN_ACK",
            f"player:{self.player.player_id}",
            match_id=match_id,
            player_id=self.player.player_id,
            arrival_timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            accept=True,
            conversation_id=message.conversation_id,
        )
    
    async def handle_choose_parity(self, message: Message) -> Message:
        """Handle parity choice request."""
        match_id = getattr(message, "match_id")
        context = getattr(message, "context", {})
        opponent_id = context.get("opponent_id")
        
        self.logger.info(f"Choosing parity for match {match_id}")
        
        # Use strategy to choose
        choice = self.player.strategy.choose_parity(opponent_id, context)
        
        self.logger.info(f"Chose: {choice}")
        
        return create_message(
            "CHOOSE_PARITY_RESPONSE",
            f"player:{self.player.player_id}",
            match_id=match_id,
            player_id=self.player.player_id,
            parity_choice=choice,
            conversation_id=message.conversation_id,
        )
    
    async def handle_game_over(self, message: Message) -> Message:
        """Handle game over message."""
        match_id = getattr(message, "match_id")
        game_result = getattr(message, "game_result", {})
        
        winner = game_result.get("winner_player_id")
        drawn_number = game_result.get("drawn_number")
        choices = game_result.get("choices", {})
        
        # Record in history
        self.player.history_repo.add_game({
            "match_id": match_id,
            "opponent": self.player.current_game.get("opponent_id") if self.player.current_game else None,
            "my_choice": choices.get(self.player.player_id),
            "opponent_choice": choices.get(self.player.current_game.get("opponent_id")) if self.player.current_game else None,
            "drawn_number": drawn_number,
            "winner": winner,
            "won": winner == self.player.player_id,
        })
        
        self.logger.info(f"Game {match_id} over: winner={winner}, my_choice={choices.get(self.player.player_id)}")
        
        # Clear current game
        self.player.current_game = None
        
        return create_message(
            "ACK",
            f"player:{self.player.player_id}",
            conversation_id=message.conversation_id,
        )
    
    async def handle_round_announcement(self, message: Message) -> Message:
        """Handle round announcement."""
        round_id = getattr(message, "round_id", 0)
        matches = getattr(message, "matches", [])
        self.logger.info(f"Round {round_id} announced with {len(matches)} matches")
        return create_message(
            "ACK",
            f"player:{self.player.player_id}",
            conversation_id=message.conversation_id,
        )
    
    async def handle_standings_update(self, message: Message) -> Message:
        """Handle standings update."""
        standings = getattr(message, "standings", [])
        self.logger.info(f"Standings updated: {len(standings)} players")
        return create_message(
            "ACK",
            f"player:{self.player.player_id}",
            conversation_id=message.conversation_id,
        )
    
    async def handle_round_completed(self, message: Message) -> Message:
        """Handle round completed."""
        round_id = getattr(message, "round_id", 0)
        self.logger.info(f"Round {round_id} completed")
        return create_message(
            "ACK",
            f"player:{self.player.player_id}",
            conversation_id=message.conversation_id,
        )
    
    async def handle_league_completed(self, message: Message) -> Message:
        """Handle league completed."""
        champion = getattr(message, "champion", {})
        self.logger.info(f"League completed! Champion: {champion.get('player_id', 'Unknown')}")
        return create_message(
            "ACK",
            f"player:{self.player.player_id}",
            conversation_id=message.conversation_id,
        )

