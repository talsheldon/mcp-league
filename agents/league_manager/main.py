"""League Manager - Orchestrates the tournament."""

import asyncio
import argparse
from pathlib import Path
from typing import Dict, List, Optional
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "SHARED"))

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from league_sdk import (
    Message,
    create_message,
    validate_message,
    setup_logger,
    StandingsRepository,
    MatchRepository,
)
from league_sdk.config_models import AgentConfig

from .handlers import MessageHandler
from .scheduler import RoundRobinScheduler


class LeagueManager:
    """League Manager agent."""
    
    def __init__(
        self,
        league_id: str,
        port: int = 8000,
        data_dir: Path = Path("SHARED/data"),
        log_dir: Path = Path("SHARED/logs"),
    ):
        self.league_id = league_id
        self.port = port
        self.data_dir = data_dir
        self.log_dir = log_dir
        
        # Setup logger
        self.logger = setup_logger(
            "league_manager",
            log_dir / "league" / league_id,
            agent_id="league_manager",
        )
        
        # Repositories
        self.standings_repo = StandingsRepository(data_dir, league_id)
        self.match_repo = MatchRepository(data_dir, league_id)
        
        # State
        self.registered_players: Dict[str, AgentConfig] = {}
        self.registered_referees: Dict[str, AgentConfig] = {}
        self.auth_tokens: Dict[str, str] = {}  # agent_id -> token
        self.current_round = 0
        self.total_rounds = 0
        self.matches_by_round: Dict[int, List[Dict]] = {}
        self.completed_matches: set = set()
        self.league_started = False
        
        # Scheduler
        self.scheduler = RoundRobinScheduler()
        
        # Message handler
        self.handler = MessageHandler(self)
        
        # FastAPI app
        self.app = FastAPI(title="League Manager")
        self.app.post("/mcp")(self.handle_mcp_request)
    
    async def handle_mcp_request(self, request: dict):
        """Handle MCP JSON-RPC request."""
        try:
            method = request.get("method", "handle_message")
            params = request.get("params", {})
            message_data = params.get("message", {})
            
            validate_message(message_data)
            message = Message.from_dict(message_data)
            
            response = await self.handler.handle(message)
            
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request.get("id", 1),
                "result": response.to_dict() if hasattr(response, "to_dict") else response,
            })
        except Exception as e:
            self.logger.error(f"Error handling request: {e}", exc_info=True)
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request.get("id", 1),
                "error": {"code": -32000, "message": str(e)},
            }, status_code=500)
    
    def generate_auth_token(self, agent_id: str) -> str:
        """Generate authentication token."""
        import hashlib
        token = f"tok_{agent_id}_{hashlib.md5(f'{agent_id}{self.league_id}'.encode()).hexdigest()[:8]}"
        self.auth_tokens[agent_id] = token
        return token
    
    def validate_auth_token(self, agent_id: str, token: str) -> bool:
        """Validate authentication token."""
        return self.auth_tokens.get(agent_id) == token
    
    def start_league(self, player_ids: List[str]) -> None:
        """Start the league with given players."""
        if self.league_started:
            raise ValueError("League already started")
        
        if len(player_ids) < 2:
            raise ValueError("Need at least 2 players")
        
        # Initialize standings
        for player_id in player_ids:
            player = self.registered_players.get(player_id)
            if player:
                self.standings_repo.initialize_player(
                    player_id,
                    player.display_name,
                )
        
        # Generate schedule
        schedule = self.scheduler.generate_schedule(player_ids)
        self.total_rounds = len(schedule)
        self.matches_by_round = schedule
        self.league_started = True
        self.current_round = 1
        
        self.logger.info(f"League {self.league_id} started with {len(player_ids)} players, {self.total_rounds} rounds")
    
    def run(self):
        """Run the league manager server."""
        self.logger.info(f"Starting League Manager on port {self.port}")
        uvicorn.run(self.app, host="0.0.0.0", port=self.port, log_level="info")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="League Manager")
    parser.add_argument("--league-id", required=True, help="League ID")
    parser.add_argument("--port", type=int, default=8000, help="Port number")
    parser.add_argument("--data-dir", type=Path, default=Path("SHARED/data"), help="Data directory")
    parser.add_argument("--log-dir", type=Path, default=Path("SHARED/logs"), help="Log directory")
    
    args = parser.parse_args()
    
    manager = LeagueManager(
        league_id=args.league_id,
        port=args.port,
        data_dir=args.data_dir,
        log_dir=args.log_dir,
    )
    
    manager.run()


if __name__ == "__main__":
    main()

