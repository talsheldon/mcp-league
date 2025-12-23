# MCP League - Even/Odd Tournament System

A multi-agent system implementing a round-robin tournament where AI agents play an Even/Odd game using the Model Context Protocol (MCP).

## Architecture

The system consists of three types of agents:

1. **League Manager**: Orchestrates the tournament, manages registration, schedules matches, and tracks standings
2. **Referee**: Manages individual games, enforces rules, collects player choices, and reports results
3. **Player**: Participates in games, makes strategic choices, and tracks personal history

## Project Structure

```
mcp-league/
├── SHARED/
│   ├── config/            # Configuration files
│   │   ├── system.json
│   │   ├── agents/agents_config.json
│   │   ├── leagues/league_2025_even_odd.json
│   │   ├── games/games_registry.json
│   │   └── defaults/{referee,player}.json
│   ├── data/              # Runtime data (created at runtime)
│   │   ├── leagues/<league_id>/
│   │   ├── matches/<league_id>/
│   │   └── players/<player_id>/
│   ├── logs/              # Log files (created at runtime)
│   │   ├── league/<league_id>/
│   │   ├── agents/
│   │   └── system/
│   └── league_sdk/        # Shared SDK with common utilities
│       ├── message.py
│       ├── game_logic.py
│       ├── repositories.py
│       ├── logger.py
│       ├── config_models.py
│       └── config_loader.py
├── agents/
│   ├── league_manager/   # League Manager agent
│   ├── referee_REF01/     # Referee agent
│   └── player_P01/        # Player agent (can have player_P02, etc.)
├── doc/                   # Documentation
│   ├── protocol-spec.md
│   └── message-examples/
└── tests/                 # Unit tests
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install the shared SDK:
```bash
cd SHARED/league_sdk
pip install -e .
cd ../..
```

## Running the System

### Prerequisites

- Python 3.10 or higher
- All dependencies installed (see Installation above)
- At least 2 players and 1 referee registered before starting the league

### Quick Start

You need to run each agent in a **separate terminal window/tab**. The order matters:

#### Step 1: Start League Manager (Start First)

```bash
python agents/league_manager/main.py --league-id league_2025_even_odd --port 8000
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

The League Manager will be available at `http://localhost:8000/mcp` and API docs at `http://localhost:8000/docs`.

#### Step 2: Start Referee

In a **new terminal**:

```bash
python agents/referee_REF01/main.py --referee-id REF01 --league-id league_2025_even_odd --port 8001
```

The referee will automatically register with the League Manager. You should see:
```
INFO: Registered with League Manager: REF01
INFO: Starting Referee REF01 on port 8001
```

#### Step 3: Start Players

In **separate terminals** for each player:

**Terminal 3 - Player P01:**
```bash
python agents/player_P01/main.py --player-id P01 --league-id league_2025_even_odd --port 8101
```

**Terminal 4 - Player P02:**
```bash
python agents/player_P01/main.py --player-id P02 --league-id league_2025_even_odd --port 8102
```

> **Note:** You can use the same `player_P01` directory with different `--player-id` and `--port` arguments to run multiple players.

Each player will automatically register with the League Manager. You should see:
```
INFO: Registered with League Manager: P01
INFO: Starting Player P01 on port 8101
```

#### Step 4: Start the League

Once all agents are running and registered, start the league by sending a `START_LEAGUE` message:

**Option A: Using curl**
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "handle_message",
    "params": {
      "message": {
        "protocol": "league.v2",
        "message_type": "START_LEAGUE",
        "sender": "launcher",
        "timestamp": "2025-01-15T10:00:00Z",
        "conversation_id": "conv-start-league",
        "league_id": "league_2025_even_odd"
      }
    }
  }'
```

**Option B: Using Python**
```python
import httpx
import json
from datetime import datetime, timezone

message = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "handle_message",
    "params": {
        "message": {
            "protocol": "league.v2",
            "message_type": "START_LEAGUE",
            "sender": "launcher",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "conversation_id": "conv-start-league",
            "league_id": "league_2025_even_odd"
        }
    }
}

response = httpx.post("http://localhost:8000/mcp", json=message)
print(response.json())
```


### Expected Flow

Once the league starts, you should see:

1. **Round Announcement**: League Manager sends `ROUND_ANNOUNCEMENT` to all referees and players
2. **Game Invitations**: Referees send `GAME_INVITATION` to players
3. **Players Join**: Players respond with `GAME_JOIN_ACK`
4. **Parity Choices**: Referees send `CHOOSE_PARITY_CALL` to players
5. **Players Choose**: Players respond with `CHOOSE_PARITY_RESPONSE`
6. **Game Results**: Referees determine winners and send `GAME_OVER` to players
7. **Match Reports**: Referees send `MATCH_RESULT_REPORT` to League Manager
8. **Standings Updates**: League Manager sends `LEAGUE_STANDINGS_UPDATE` to all players
9. **Round Completion**: When all matches in a round complete, `ROUND_COMPLETED` is sent
10. **Next Round**: League Manager announces the next round (or league completes)

### Monitoring the System

Watch the logs in each terminal to see:
- Registration confirmations
- Round announcements
- Game invitations and acceptances
- Player choices
- Match results
- Standings updates

### Checking Results

After games complete, check the data files:

**View Standings:**
```bash
cat SHARED/data/leagues/league_2025_even_odd/standings.json
```

**View Match Results:**
```bash
ls SHARED/data/matches/league_2025_even_odd/
cat SHARED/data/matches/league_2025_even_odd/R1M1.json  # Example match
```

**View Player History:**
```bash
cat SHARED/data/players/P01/history.json
cat SHARED/data/players/P02/history.json
```

**View Logs:**
```bash
# League Manager logs
ls SHARED/logs/league/league_2025_even_odd/

# Agent logs
ls SHARED/logs/agents/
```

### Stopping the System

Press `Ctrl+C` in each terminal window, or kill all processes:

```bash
# Kill all league-related processes
pkill -f "python.*league_manager|python.*referee|python.*player"
```

### Troubleshooting

**Port Already in Use:**
- Change the `--port` argument
- Or find and kill the process: `lsof -ti:8000 | xargs kill`

**Import Errors:**
- Make sure you installed the SDK: `cd SHARED/league_sdk && pip install -e .`
- Verify dependencies: `pip install -r requirements.txt`

**Agents Not Connecting:**
- Ensure League Manager starts first
- Check that all agents use the same `--league-id`
- Verify ports don't conflict (8000, 8001, 8101, 8102)
- Check firewall settings

**No Games Starting:**
- You need at least 2 players registered
- Send `START_LEAGUE` message to League Manager
- Check logs for error messages
- Verify referees are registered

**Games Not Completing:**
- Check referee logs for errors
- Verify players are responding to invitations
- Check network connectivity between agents
- Review game logic in `SHARED/league_sdk/game_logic.py`

## Testing

### Unit Tests

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov
```

Run specific test suites:
```bash
# Message validation tests
pytest tests/test_message.py -v

# Protocol compliance tests
pytest tests/test_contracts.py -v

# Game logic tests
pytest tests/test_game_logic.py -v
```

### End-to-End Testing

To test the full system end-to-end:

1. Start all agents (see "Running the System" above)
2. Send a `START_LEAGUE` message to the League Manager
3. Monitor logs and check results in `SHARED/data/`

**Note:** Requires all dependencies to be installed and ports 8000, 8001, 8101, 8102 to be available.

## Protocol

The system uses a message-based protocol (`league.v2`) with JSON-RPC over HTTP. All agents communicate via standardized messages following the protocol specification.

## Features

- **Round-robin tournament**: Fair scheduling for all players
- **Message-based communication**: All interactions via JSON messages
- **Error handling**: Comprehensive error codes and retry policies
- **State persistence**: Standings and match results saved to JSON files
- **Structured logging**: JSON-formatted logs for debugging
- **Testable**: Comprehensive unit tests with good coverage

## License

Copyright (c) 2025
