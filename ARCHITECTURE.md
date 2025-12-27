# System Architecture

## Overview

The MCP League system is a distributed multi-agent system implementing a round-robin tournament for the Even/Odd game. The architecture follows a message-based, event-driven design using JSON-RPC over HTTP.

## System Components

### 1. League Manager
**Role**: Central orchestrator and state manager

**Responsibilities**:
- Agent registration (referees and players)
- Tournament scheduling (round-robin)
- Standings management
- Match result aggregation
- Round progression control

**Key Components**:
- `LeagueManager`: Main agent class
- `MessageHandler`: Message routing and processing
- `RoundRobinScheduler`: Tournament schedule generation
- `StandingsRepository`: Standings persistence

### 2. Referee Agents
**Role**: Game orchestration and rule enforcement

**Responsibilities**:
- Receive match assignments
- Invite players to games
- Collect player choices
- Determine game winners
- Report results to League Manager

**Key Components**:
- `Referee`: Main agent class
- `GameManager`: Game flow orchestration
- `MessageHandler`: Message processing

### 3. Player Agents
**Role**: Game participants

**Responsibilities**:
- Register with League Manager
- Accept game invitations
- Make strategic choices
- Track personal game history

**Key Components**:
- `Player`: Main agent class
- `Strategy`: Decision-making logic
- `MessageHandler`: Message processing
- `HistoryRepository`: Personal game history

## Communication Architecture

### Protocol
- **Protocol Version**: league.v2
- **Transport**: JSON-RPC 2.0 over HTTP
- **Message Format**: JSON with standardized envelope

### Message Flow

```
┌─────────────────┐
│ League Manager  │
└────────┬────────┘
         │
         ├─── ROUND_ANNOUNCEMENT ───┐
         │                           │
         │                           ▼
    ┌────┴────┐              ┌──────────────┐
    │ Referee │              │   Players   │
    └────┬────┘              └──────┬───────┘
         │                           │
         ├─── GAME_INVITATION ───────┤
         │                           │
         │◄── GAME_JOIN_ACK ────────┤
         │                           │
         ├─── CHOOSE_PARITY_CALL ────┤
         │                           │
         │◄── CHOOSE_PARITY_RESPONSE─┤
         │                           │
         ├─── GAME_OVER ─────────────┤
         │                           │
         │                           │
         └─── MATCH_RESULT_REPORT ───┘
                   │
                   ▼
         ┌─────────────────┐
         │ League Manager  │
         └─────────────────┘
```

## Data Flow

### Registration Flow
1. Agent sends registration request to League Manager
2. League Manager validates and assigns ID
3. League Manager generates auth token
4. League Manager responds with ID and token

### Game Flow
1. League Manager announces round with matches
2. Referee receives announcement, identifies assigned matches
3. Referee sends invitations to players
4. Players accept and join
5. Referee collects parity choices
6. Referee determines winner
7. Referee reports result to League Manager
8. League Manager updates standings

### Standings Update Flow
1. Match result received by League Manager
2. Standings updated in repository
3. Standings broadcast to all players
4. Round completion checked
5. Next round announced if applicable

## Data Persistence

### File Structure
```
SHARED/data/
├── leagues/<league_id>/
│   └── standings.json
├── matches/<league_id>/
│   └── <match_id>.json
└── players/<player_id>/
    └── history.json
```

### Data Models
- **Standings**: Player rank, wins, losses, draws, points
- **Match Results**: Winner, score, game details, choices
- **Player History**: Personal game records with opponents

## Concurrency Model

### Asynchronous Operations
- All message handling uses async/await
- Games run as asyncio tasks
- Multiple games can run concurrently per referee

### Concurrency Control
- Referees track active games
- `max_concurrent_matches` limit enforced
- Games cleaned up on completion

## Error Handling

### Error Codes
- E001-E004: General errors
- E005-E007: Registration errors
- E008-E011: Validation errors
- E012-E014: Authentication errors
- E015-E018: Game errors
- E019-E020: Timeout errors
- E021-E023: League errors

### Error Propagation
- Errors returned as LEAGUE_ERROR messages
- Error context included for debugging
- Original message type preserved

## Configuration

### Configuration Files
- `system.json`: System-wide settings (timeouts, scoring)
- `leagues/<id>.json`: League-specific configuration
- `defaults/referee.json`: Default referee settings
- `defaults/player.json`: Default player settings

### Configuration Loading
- Loaded at agent startup
- Validated against Pydantic models
- Defaults provided for missing values

## Security

### Authentication
- Auth tokens generated on registration
- Tokens validated for protected operations
- Token format: `tok_{agent_id}_{hash}`

### Input Validation
- All messages validated against protocol
- Pydantic models enforce type safety
- Invalid messages rejected with error codes

## Extensibility Points

### Adding New Game Types
1. Implement game logic in `SHARED/league_sdk/game_logic.py`
2. Register in `games_registry.json`
3. Update message types if needed

### Custom Player Strategies
1. Extend `Strategy` class in `agents/player_P01/strategy.py`
2. Implement `choose_parity()` method
3. Use history repository for context

### Additional Message Types
1. Define in protocol specification
2. Add to message creation utilities
3. Implement handlers in relevant agents

## Performance Considerations

### Scalability
- Stateless message handling
- File-based persistence (can be replaced with DB)
- Horizontal scaling of referees

### Bottlenecks
- League Manager is single point of coordination
- File I/O for persistence (consider async I/O)
- Network latency between agents

### Optimization Opportunities
- Batch standings updates
- Cache frequently accessed data
- Use connection pooling for HTTP clients

---

## Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    League Manager                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Handler    │  │  Scheduler   │  │  Repository  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
         │                    │                    │
         │ ROUND_ANNOUNCEMENT │                    │
         │                    │                    │
    ┌────▼────┐         ┌─────▼─────┐      ┌──────▼──────┐
    │ Referee │         │  Referee  │      │   Player    │
    │  REF01  │         │   REF02   │      │    P01      │
    └────┬────┘         └─────┬─────┘      └──────┬──────┘
         │                    │                    │
         │ GAME_INVITATION    │                    │
         │                    │                    │
         └────────────────────┴────────────────────┘
```

---

## Deployment Architecture

### Single Machine Deployment
- All agents run as separate processes
- Localhost communication
- Shared file system for data

### Distributed Deployment
- Agents can run on different machines
- Network connectivity required
- Shared storage or data replication needed

---

**Last Updated**: 2025-12-27

