"""Player - Participates in games."""

import asyncio
import argparse
from pathlib import Path
from typing import Dict, Optional
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "SHARED"))

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import httpx
from league_sdk import Message, create_message, validate_message, setup_logger
from league_sdk.repositories import HistoryRepository

from .handlers import MessageHandler
from .strategy import Strategy


class Player:
    """Player agent."""
    
    def __init__(
        self,
        player_id: str,
        league_id: str,
        league_manager_endpoint: str = "http://localhost:8000/mcp",
        port: int = 8101,
        data_dir: Path = Path("SHARED/data"),
        log_dir: Path = Path("SHARED/logs"),
    ):
        self.player_id = player_id
        self.league_id = league_id
        self.league_manager_endpoint = league_manager_endpoint
        self.port = port
        self.data_dir = data_dir
        self.log_dir = log_dir
        
        # Setup logger
        self.logger = setup_logger(
            "player",
            log_dir / "agents",
            agent_id=player_id,
        )
        
        # Repositories
        self.history_repo = HistoryRepository(data_dir, player_id)
        
        # State
        self.registered = False
        self.auth_token: Optional[str] = None
        self.strategy = Strategy(self.logger, self.history_repo)
        self.current_game: Optional[Dict] = None
        
        # Message handler
        self.handler = MessageHandler(self)
        
        # FastAPI app
        self.app = FastAPI(title=f"Player {player_id}")
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
    
    async def register_with_league_manager(self) -> bool:
        """Register with League Manager."""
        try:
            async with httpx.AsyncClient() as client:
                message = create_message(
                    "LEAGUE_REGISTER_REQUEST",
                    f"player:{self.player_id}",
                    player_meta={
                        "display_name": f"Player {self.player_id}",
                        "version": "1.0.0",
                        "game_types": ["even_odd"],
                        "contact_endpoint": f"http://localhost:{self.port}/mcp",
                    },
                )
                
                response = await client.post(
                    self.league_manager_endpoint,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "handle_message",
                        "params": {"message": message.to_dict()},
                    },
                )
                
                result = response.json().get("result", {})
                if result.get("status") == "ACCEPTED":
                    self.auth_token = result.get("auth_token")
                    self.registered = True
                    self.logger.info(f"Registered with League Manager: {self.player_id}")
                    return True
                
                return False
        except Exception as e:
            self.logger.error(f"Registration failed: {e}")
            return False
    
    async def send_to_referee(self, referee_endpoint: str, message: Message) -> Optional[Message]:
        """Send message to referee."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    referee_endpoint,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "handle_message",
                        "params": {"message": message.to_dict()},
                    },
                )
                
                result = response.json().get("result", {})
                if "error" in response.json():
                    self.logger.error(f"Error from referee: {response.json()['error']}")
                    return None
                
                return Message.from_dict(result) if result else None
        except Exception as e:
            self.logger.error(f"Error sending to referee {referee_endpoint}: {e}")
            return None
    
    def run(self):
        """Run the player server."""
        self.logger.info(f"Starting Player {self.player_id} on port {self.port}")
        uvicorn.run(self.app, host="0.0.0.0", port=self.port, log_level="info")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Player Agent")
    parser.add_argument("--player-id", required=True, help="Player ID")
    parser.add_argument("--league-id", required=True, help="League ID")
    parser.add_argument("--league-manager-endpoint", default="http://localhost:8000/mcp", help="League Manager endpoint")
    parser.add_argument("--port", type=int, default=8101, help="Port number")
    parser.add_argument("--data-dir", type=Path, default=Path("SHARED/data"), help="Data directory")
    parser.add_argument("--log-dir", type=Path, default=Path("SHARED/logs"), help="Log directory")
    
    args = parser.parse_args()
    
    player = Player(
        player_id=args.player_id,
        league_id=args.league_id,
        league_manager_endpoint=args.league_manager_endpoint,
        port=args.port,
        data_dir=args.data_dir,
        log_dir=args.log_dir,
    )
    
    # Register with league manager
    asyncio.run(player.register_with_league_manager())
    
    player.run()


if __name__ == "__main__":
    main()

