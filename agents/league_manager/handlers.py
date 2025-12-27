"""Message handlers for League Manager."""

from typing import Dict, Optional
import httpx
from league_sdk import Message, create_message, ErrorCode, create_error_message


class MessageHandler:
    """Handles incoming messages for League Manager."""
    
    def __init__(self, manager):
        self.manager = manager
        self.logger = manager.logger
    
    async def handle(self, message: Message) -> Message:
        """Route message to appropriate handler."""
        handler_map = {
            "REFEREE_REGISTER_REQUEST": self.handle_referee_register,
            "LEAGUE_REGISTER_REQUEST": self.handle_player_register,
            "MATCH_RESULT_REPORT": self.handle_match_result,
            "LEAGUE_QUERY": self.handle_league_query,
            "START_LEAGUE": self.handle_start_league,
        }
        
        handler = handler_map.get(message.message_type)
        if not handler:
            raise ValueError(f"Unknown message type: {message.message_type}")
        
        return await handler(message)
    
    async def handle_referee_register(self, message: Message) -> Message:
        """Handle referee registration."""
        referee_meta = getattr(message, "referee_meta", {})
        referee_id = f"REF{len(self.manager.registered_referees) + 1:02d}"
        
        from league_sdk.config_models import AgentConfig
        config = AgentConfig(
            agent_id=referee_id,
            display_name=referee_meta.get("display_name", referee_id),
            version=referee_meta.get("version", "1.0.0"),
            contact_endpoint=referee_meta.get("contact_endpoint", ""),
            game_types=referee_meta.get("game_types", []),
        )
        
        self.manager.registered_referees[referee_id] = config
        auth_token = self.manager.generate_auth_token(referee_id)
        
        self.logger.info(f"Referee {referee_id} registered")
        
        return create_message(
            "REFEREE_REGISTER_RESPONSE",
            "league_manager",
            status="ACCEPTED",
            referee_id=referee_id,
            auth_token=auth_token,
            conversation_id=message.conversation_id,
        )
    
    async def handle_player_register(self, message: Message) -> Message:
        """Handle player registration request.
        
        Args:
            message: LEAGUE_REGISTER_REQUEST with player_meta
            
        Returns:
            LEAGUE_REGISTER_RESPONSE with status, player_id, and auth_token
        """
        player_meta = getattr(message, "player_meta", {})
        player_id = f"P{len(self.manager.registered_players) + 1:02d}"
        
        from league_sdk.config_models import AgentConfig
        config = AgentConfig(
            agent_id=player_id,
            display_name=player_meta.get("display_name", player_id),
            version=player_meta.get("version", "1.0.0"),
            contact_endpoint=player_meta.get("contact_endpoint", ""),
            game_types=player_meta.get("game_types", []),
        )
        
        self.manager.registered_players[player_id] = config
        auth_token = self.manager.generate_auth_token(player_id)
        
        self.logger.info(f"Player {player_id} registered")
        
        return create_message(
            "LEAGUE_REGISTER_RESPONSE",
            "league_manager",
            status="ACCEPTED",
            player_id=player_id,
            auth_token=auth_token,
            conversation_id=message.conversation_id,
        )
    
    async def handle_match_result(self, message: Message) -> Message:
        """Handle match result report from referee.
        
        Args:
            message: MATCH_RESULT_REPORT with match_id, round_id, and result
            
        Returns:
            MATCH_RESULT_ACK confirming result was recorded
            
        Updates standings, sends standings update to players, and checks round completion.
        """
        match_id = message.match_id
        result = getattr(message, "result", {})
        
        # Update standings
        winner = result.get("winner")
        score = result.get("score", {})
        player_A = result.get("details", {}).get("choices", {}).keys()
        player_ids = list(player_A)
        
        if len(player_ids) >= 2:
            self.manager.standings_repo.update_match_result(
                player_ids[0],
                player_ids[1],
                winner,
                score,
            )
        
        # Mark match as completed
        self.manager.completed_matches.add(match_id)
        
        self.logger.info(f"Match {match_id} result recorded: winner={winner}")
        
        # Send standings update to all players
        await self._send_standings_update()
        
        # Check if round is complete
        await self._check_round_completion()
        
        return create_message(
            "MATCH_RESULT_ACK",
            "league_manager",
            match_id=match_id,
            status="recorded",
            conversation_id=message.conversation_id,
        )
    
    async def handle_league_query(self, message: Message) -> Message:
        """Handle league query from authenticated player.
        
        Args:
            message: LEAGUE_QUERY with auth_token, league_id, query_type, and query_params
            
        Returns:
            LEAGUE_QUERY_RESPONSE with requested data or LEAGUE_ERROR if auth fails
            
        Supported query types:
        - GET_STANDINGS: Returns current league standings
        - GET_NEXT_MATCH: Returns next match for the querying player
        """
        # Validate auth token
        auth_token = getattr(message, "auth_token")
        sender_id = message.sender.split(":")[-1] if ":" in message.sender else message.sender
        
        if not auth_token or not self.manager.validate_auth_token(sender_id, auth_token):
            error_info = create_error_message(ErrorCode.E012, "LEAGUE_QUERY", {"provided_token": auth_token})
            return create_message(
                "LEAGUE_ERROR",
                "league_manager",
                error_code=error_info["error_code"],
                error_description=error_info["error_description"],
                original_message_type=error_info["original_message_type"],
                context=error_info["context"],
                conversation_id=message.conversation_id,
            )
        
        query_type = getattr(message, "query_type", "")
        query_params = getattr(message, "query_params", {})
        
        data = {}
        if query_type == "GET_STANDINGS":
            standings = self.manager.standings_repo.get_standings()
            data["standings"] = [
                {
                    "rank": s.rank,
                    "player_id": s.player_id,
                    "display_name": s.display_name,
                    "played": s.played,
                    "wins": s.wins,
                    "draws": s.draws,
                    "losses": s.losses,
                    "points": s.points,
                }
                for s in standings
            ]
        elif query_type == "GET_NEXT_MATCH":
            player_id = query_params.get("player_id")
            # Find next match for player
            for round_id, matches in self.manager.matches_by_round.items():
                if round_id <= self.manager.current_round:
                    for match in matches:
                        if match.get("player_A_id") == player_id or match.get("player_B_id") == player_id:
                            match_id = match.get("match_id")
                            if match_id not in self.manager.completed_matches:
                                data["next_match"] = match
                                break
        
        return create_message(
            "LEAGUE_QUERY_RESPONSE",
            "league_manager",
            query_type=query_type,
            success=True,
            data=data,
            conversation_id=message.conversation_id,
        )
    
    async def handle_start_league(self, message: Message) -> Message:
        """Handle league start request.
        
        Args:
            message: START_LEAGUE message with league_id
            
        Returns:
            LEAGUE_STATUS with current league state or LEAGUE_ERROR if insufficient players
            
        Initializes standings, generates schedule, and announces first round.
        """
        if self.manager.league_started:
            return create_message(
                "LEAGUE_STATUS",
                "league_manager",
                league_id=self.manager.league_id,
                status="running",
                current_round=self.manager.current_round,
                total_rounds=self.manager.total_rounds,
                matches_completed=len(self.manager.completed_matches),
                conversation_id=message.conversation_id,
            )
        
        # Start league with all registered players
        player_ids = list(self.manager.registered_players.keys())
        if len(player_ids) < 2:
            error_info = create_error_message(ErrorCode.E005, "START_LEAGUE")
            return create_message(
                "LEAGUE_ERROR",
                "league_manager",
                error_code=error_info["error_code"],
                error_description=error_info["error_description"],
                original_message_type=error_info["original_message_type"],
                context={"registered_players": len(player_ids), "required": 2},
                conversation_id=message.conversation_id,
            )
        
        self.manager.start_league(player_ids)
        
        # Announce first round
        await self._announce_round(1)
        
        return create_message(
            "LEAGUE_STATUS",
            "league_manager",
            league_id=self.manager.league_id,
            status="running",
            current_round=1,
            total_rounds=self.manager.total_rounds,
            matches_completed=0,
            conversation_id=message.conversation_id,
        )
    
    async def _announce_round(self, round_id: int) -> None:
        """Announce a new round."""
        matches = self.manager.matches_by_round.get(round_id, [])
        
        # Assign referees to matches and include player endpoints
        referee_ids = list(self.manager.registered_referees.keys())
        for i, match in enumerate(matches):
            if referee_ids:
                referee_id = referee_ids[i % len(referee_ids)]
                referee = self.manager.registered_referees[referee_id]
                match["referee_endpoint"] = referee.contact_endpoint
            
            # Add player endpoints from registered players
            player_A_id = match.get("player_A_id")
            player_B_id = match.get("player_B_id")
            
            if player_A_id and player_A_id in self.manager.registered_players:
                player_A_config = self.manager.registered_players[player_A_id]
                match["player_A_endpoint"] = player_A_config.contact_endpoint
            
            if player_B_id and player_B_id in self.manager.registered_players:
                player_B_config = self.manager.registered_players[player_B_id]
                match["player_B_endpoint"] = player_B_config.contact_endpoint
        
        # Create ROUND_ANNOUNCEMENT message
        announcement = create_message(
            "ROUND_ANNOUNCEMENT",
            "league_manager",
            league_id=self.manager.league_id,
            round_id=round_id,
            matches=matches,
        )
        
        # Send to all referees
        async with httpx.AsyncClient(timeout=10.0) as client:
            for referee_id, referee_config in self.manager.registered_referees.items():
                try:
                    await client.post(
                        referee_config.contact_endpoint,
                        json={
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "handle_message",
                            "params": {"message": announcement.to_dict()},
                        },
                    )
                    self.logger.info(f"Sent ROUND_ANNOUNCEMENT to {referee_id}")
                except Exception as e:
                    self.logger.error(f"Failed to send to {referee_id}: {e}")
        
        # Send to all players
        async with httpx.AsyncClient(timeout=10.0) as client:
            for player_id, player_config in self.manager.registered_players.items():
                try:
                    await client.post(
                        player_config.contact_endpoint,
                        json={
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "handle_message",
                            "params": {"message": announcement.to_dict()},
                        },
                    )
                    self.logger.info(f"Sent ROUND_ANNOUNCEMENT to {player_id}")
                except Exception as e:
                    self.logger.error(f"Failed to send to {player_id}: {e}")
        
        self.logger.info(f"Round {round_id} announced with {len(matches)} matches")
    
    async def _send_standings_update(self) -> None:
        """Send standings update to all players."""
        standings = self.manager.standings_repo.get_standings()
        
        standings_data = [
            {
                "rank": s.rank,
                "player_id": s.player_id,
                "display_name": s.display_name,
                "played": s.played,
                "wins": s.wins,
                "draws": s.draws,
                "losses": s.losses,
                "points": s.points,
            }
            for s in standings
        ]
        
        message = create_message(
            "LEAGUE_STANDINGS_UPDATE",
            "league_manager",
            league_id=self.manager.league_id,
            round_id=self.manager.current_round,
            standings=standings_data,
        )
        
        # Send to all players
        async with httpx.AsyncClient(timeout=10.0) as client:
            for player_id, player_config in self.manager.registered_players.items():
                try:
                    await client.post(
                        player_config.contact_endpoint,
                        json={
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "handle_message",
                            "params": {"message": message.to_dict()},
                        },
                    )
                except Exception as e:
                    self.logger.error(f"Failed to send standings to {player_id}: {e}")
    
    async def _check_round_completion(self) -> None:
        """Check if current round is complete and advance if needed."""
        if not self.manager.league_started:
            return
        
        current_round_matches = self.manager.matches_by_round.get(self.manager.current_round, [])
        completed_in_round = sum(
            1 for m in current_round_matches
            if m.get("match_id") in self.manager.completed_matches
        )
        
        if completed_in_round >= len(current_round_matches):
            # Round complete
            self.logger.info(f"Round {self.manager.current_round} completed")
            
            # Send ROUND_COMPLETED message
            await self._send_round_completed()
            
            # Check if league is complete
            if self.manager.current_round >= self.manager.total_rounds:
                await self._send_league_completed()
            else:
                # Start next round
                self.manager.current_round += 1
                await self._announce_round(self.manager.current_round)
    
    async def _send_round_completed(self) -> None:
        """Send round completed message to players."""
        current_round_matches = self.manager.matches_by_round.get(self.manager.current_round, [])
        completed_count = sum(
            1 for m in current_round_matches
            if m.get("match_id") in self.manager.completed_matches
        )
        
        message = create_message(
            "ROUND_COMPLETED",
            "league_manager",
            league_id=self.manager.league_id,
            round_id=self.manager.current_round,
            matches_completed=completed_count,
            next_round_id=self.manager.current_round + 1 if self.manager.current_round < self.manager.total_rounds else None,
            summary={
                "total_matches": len(current_round_matches),
                "wins": 0,  # Would calculate from standings
                "draws": 0,
                "technical_losses": 0,
            },
        )
        
        # Send to all players
        async with httpx.AsyncClient(timeout=10.0) as client:
            for player_id, player_config in self.manager.registered_players.items():
                try:
                    await client.post(
                        player_config.contact_endpoint,
                        json={
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "handle_message",
                            "params": {"message": message.to_dict()},
                        },
                    )
                except Exception as e:
                    self.logger.error(f"Failed to send round completed to {player_id}: {e}")
    
    async def _send_league_completed(self) -> None:
        """Send league completed message to all agents."""
        standings = self.manager.standings_repo.get_standings()
        champion = standings[0] if standings else None
        
        final_standings = [
            {"rank": s.rank, "player_id": s.player_id, "points": s.points}
            for s in standings
        ]
        
        message = create_message(
            "LEAGUE_COMPLETED",
            "league_manager",
            league_id=self.manager.league_id,
            total_rounds=self.manager.total_rounds,
            total_matches=len(self.manager.completed_matches),
            champion={
                "player_id": champion.player_id if champion else None,
                "display_name": champion.display_name if champion else None,
                "points": champion.points if champion else 0,
            },
            final_standings=final_standings,
        )
        
        # Send to all agents
        all_agents = list(self.manager.registered_players.values()) + list(self.manager.registered_referees.values())
        async with httpx.AsyncClient(timeout=10.0) as client:
            for agent_config in all_agents:
                try:
                    await client.post(
                        agent_config.contact_endpoint,
                        json={
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "handle_message",
                            "params": {"message": message.to_dict()},
                        },
                    )
                except Exception as e:
                    self.logger.error(f"Failed to send league completed to {agent_config.agent_id}: {e}")

