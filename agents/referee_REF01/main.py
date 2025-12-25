"""Referee - Manages individual games."""

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
from league_sdk.game_logic import EvenOddGame

from .handlers import MessageHandler
from .game_manager import GameManager


class Referee:
    """Referee agent."""
    
    def __init__(
        self,
        referee_id: str,
        league_id: str,
        league_manager_endpoint: str = "http://localhost:8000/mcp",
        port: int = 8001,
        data_dir: Path = Path("SHARED/data"),
        log_dir: Path = Path("SHARED/logs"),
    ):
        self.referee_id = referee_id
        self.league_id = league_id
        self.league_manager_endpoint = league_manager_endpoint
        self.port = port
        self.data_dir = data_dir
        self.log_dir = log_dir
        
        # Setup logger
        self.logger = setup_logger(
            "referee",
            log_dir / "agents",
            agent_id=referee_id,
        )
        
        # State
        self.registered = False
        self.auth_token: Optional[str] = None
        self.game_manager = GameManager(self.logger)
        
        # Message handler
        self.handler = MessageHandler(self)
        
        # FastAPI app
        self.app = FastAPI(title=f"Referee {referee_id}")
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
                    "REFEREE_REGISTER_REQUEST",
                    f"referee:{self.referee_id}",
                    referee_meta={
                        "display_name": f"Referee {self.referee_id}",
                        "version": "1.0.0",
                        "game_types": ["even_odd"],
                        "contact_endpoint": f"http://localhost:{self.port}/mcp",
                        "max_concurrent_matches": 2,
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
                    self.logger.info(f"Registered with League Manager: {self.referee_id}")
                    return True
                
                return False
        except Exception as e:
            self.logger.error(f"Registration failed: {e}")
            return False
    
    async def send_to_player(self, player_endpoint: str, message: Message) -> Optional[Message]:
        """Send message to player."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    player_endpoint,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "handle_message",
                        "params": {"message": message.to_dict()},
                    },
                )
                
                result = response.json().get("result", {})
                if "error" in response.json():
                    self.logger.error(f"Error from player: {response.json()['error']}")
                    return None
                
                return Message.from_dict(result) if result else None
        except Exception as e:
            self.logger.error(f"Error sending to player {player_endpoint}: {e}")
            return None
    
    async def report_match_result(self, match_id: str, result: Dict) -> None:
        """Report match result to League Manager."""
        try:
            async with httpx.AsyncClient() as client:
                message = create_message(
                    "MATCH_RESULT_REPORT",
                    f"referee:{self.referee_id}",
                    league_id=self.league_id,
                    match_id=match_id,
                    round_id=result.get("round_id"),
                    game_type="even_odd",
                    result=result,
                )
                
                await client.post(
                    self.league_manager_endpoint,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "handle_message",
                        "params": {"message": message.to_dict()},
                    },
                )
                
                self.logger.info(f"Match result reported: {match_id}")
        except Exception as e:
            self.logger.error(f"Error reporting match result: {e}")
    
    def run(self):
        """Run the referee server."""
        self.logger.info(f"Starting Referee {self.referee_id} on port {self.port}")
        uvicorn.run(self.app, host="0.0.0.0", port=self.port, log_level="info")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Referee Agent")
    parser.add_argument("--referee-id", required=True, help="Referee ID")
    parser.add_argument("--league-id", required=True, help="League ID")
    parser.add_argument("--league-manager-endpoint", default="http://localhost:8000/mcp", help="League Manager endpoint")
    parser.add_argument("--port", type=int, default=8001, help="Port number")
    parser.add_argument("--data-dir", type=Path, default=Path("SHARED/data"), help="Data directory")
    parser.add_argument("--log-dir", type=Path, default=Path("SHARED/logs"), help="Log directory")
    
    args = parser.parse_args()
    
    referee = Referee(
        referee_id=args.referee_id,
        league_id=args.league_id,
        league_manager_endpoint=args.league_manager_endpoint,
        port=args.port,
        data_dir=args.data_dir,
        log_dir=args.log_dir,
    )
    
    # Register with league manager
    import asyncio
    asyncio.run(referee.register_with_league_manager())
    
    referee.run()


if __name__ == "__main__":
    main()

