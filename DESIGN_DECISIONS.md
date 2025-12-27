# Design Decision Records (ADRs)

This document records key architectural and design decisions made during the development of the MCP League system.

## ADR-001: Message-Based Communication Protocol

**Status**: Accepted  
**Date**: 2025-12-27  
**Context**: Need for standardized communication between distributed agents.

**Decision**: Use JSON-RPC 2.0 over HTTP with a custom message envelope (league.v2 protocol).

**Rationale**:
- **Interoperability**: JSON-RPC is a standard protocol that enables easy integration
- **HTTP Transport**: Leverages existing HTTP infrastructure, firewalls, and tooling
- **Message Envelope**: Custom envelope allows for protocol versioning and extensibility
- **Asynchronous Support**: HTTP naturally supports async operations with asyncio

**Alternatives Considered**:
- **WebSockets**: More complex, requires persistent connections, harder to debug
- **gRPC**: More efficient but requires code generation, less human-readable
- **Direct TCP**: Lower-level, more complex error handling

**Consequences**:
- ✅ Easy to debug (human-readable JSON)
- ✅ Works with standard HTTP tools (curl, Postman)
- ✅ Supports async/await patterns
- ⚠️ Slightly more overhead than binary protocols
- ⚠️ Requires HTTP server setup

---

## ADR-002: File-Based Persistence

**Status**: Accepted  
**Date**: 2025-12-27  
**Context**: Need for data persistence without external dependencies.

**Decision**: Use JSON file-based storage for standings, matches, and player history.

**Rationale**:
- **Simplicity**: No database setup required, works out of the box
- **Portability**: Easy to backup, version control, and inspect
- **Development**: Fast iteration, easy to debug by viewing files
- **Sufficient**: For tournament-scale data (hundreds of matches), file I/O is adequate

**Alternatives Considered**:
- **SQLite**: More robust but adds dependency, harder to inspect
- **PostgreSQL/MySQL**: Overkill for this use case, requires setup
- **In-Memory Only**: No persistence, data lost on restart

**Consequences**:
- ✅ Zero external dependencies
- ✅ Easy to inspect and debug
- ✅ Simple backup (copy files)
- ⚠️ Not suitable for high-concurrency writes (not needed here)
- ⚠️ No transactions (acceptable for this use case)

**Future Migration Path**: Can easily migrate to database by changing repository implementations.

---

## ADR-003: Asyncio for Concurrency

**Status**: Accepted  
**Date**: 2025-12-27  
**Context**: Need to handle multiple concurrent games and message exchanges.

**Decision**: Use Python asyncio for all asynchronous operations.

**Rationale**:
- **I/O-Bound Operations**: System is primarily I/O-bound (HTTP requests, file I/O)
- **Single-Threaded**: Avoids GIL limitations for I/O operations
- **Native Support**: Python's built-in async support, no external dependencies
- **Scalability**: Can handle hundreds of concurrent operations efficiently

**Alternatives Considered**:
- **Threading**: GIL limits CPU-bound tasks, but this system is I/O-bound
- **Multiprocessing**: Unnecessary overhead, no CPU-intensive tasks
- **Synchronous**: Would block on I/O, poor performance

**Consequences**:
- ✅ Efficient I/O handling
- ✅ Clean async/await syntax
- ✅ Scales well for I/O-bound operations
- ⚠️ Requires async-aware libraries (httpx, not requests)
- ⚠️ All code paths must be async

---

## ADR-004: Shared SDK Architecture

**Status**: Accepted  
**Date**: 2025-12-27  
**Context**: Need for code reuse across multiple agent types.

**Decision**: Create a shared SDK (`league_sdk`) with common utilities, models, and logic.

**Rationale**:
- **DRY Principle**: Avoid code duplication across agents
- **Consistency**: Ensures all agents use same message format, validation, logging
- **Maintainability**: Single source of truth for shared logic
- **Testability**: Shared components can be tested independently

**Structure**:
- `message.py`: Message creation and validation
- `game_logic.py`: Game rules and result calculation
- `repositories.py`: Data persistence
- `logger.py`: Structured logging
- `config_models.py`: Configuration models
- `error_codes.py`: Error code definitions
- `retry.py`: Retry logic

**Consequences**:
- ✅ Code reuse and consistency
- ✅ Easier maintenance
- ✅ Centralized testing
- ⚠️ Requires proper package installation
- ⚠️ Changes affect all agents

---

## ADR-005: Round-Robin Tournament Scheduling

**Status**: Accepted  
**Date**: 2025-12-27  
**Context**: Need for fair tournament scheduling where all players play each other.

**Decision**: Implement round-robin scheduling algorithm.

**Rationale**:
- **Fairness**: Every player plays every other player exactly once
- **Simplicity**: Well-understood algorithm, easy to implement
- **Deterministic**: Schedule is predictable and reproducible
- **Scalable**: Works for any number of players (2+)

**Algorithm**:
- Generate all possible player pairs using combinations
- Distribute pairs across rounds to minimize conflicts
- For n players: (n-1) rounds if n is even, n rounds if n is odd

**Alternatives Considered**:
- **Single Elimination**: Faster but less fair (one loss eliminates)
- **Double Elimination**: More complex, still not fully fair
- **Swiss System**: More complex, requires ranking during tournament

**Consequences**:
- ✅ Fair and complete tournament
- ✅ Simple to understand and implement
- ✅ Works for any number of players
- ⚠️ Can result in many rounds for large player counts (acceptable for this use case)

---

## ADR-006: Retry Logic with Exponential Backoff

**Status**: Accepted  
**Date**: 2025-12-27  
**Context**: Network failures and transient errors can cause message delivery failures.

**Decision**: Implement retry logic with exponential backoff for message delivery.

**Rationale**:
- **Reliability**: Handles transient network failures gracefully
- **Exponential Backoff**: Reduces load on failing services
- **Configurable**: Max retries and delays can be adjusted
- **Required by PRD**: NFR-015 specifies retry up to 3 times

**Implementation**:
- Max 3 retries (per PRD requirement)
- Initial delay: 1 second
- Backoff factor: 2x (1s, 2s, 4s)
- Max delay cap: 10 seconds

**Alternatives Considered**:
- **No Retry**: Simple but unreliable
- **Fixed Delay**: Less efficient than exponential backoff
- **Linear Backoff**: Less efficient than exponential

**Consequences**:
- ✅ Improved reliability
- ✅ Handles transient failures
- ✅ Reduces load on failing services
- ⚠️ Slightly more complex code
- ⚠️ Longer total time on failures

---

## ADR-007: Configuration-Driven Timeouts

**Status**: Accepted  
**Date**: 2025-12-27  
**Context**: Need for configurable timeouts without code changes.

**Decision**: Load timeout values from `system.json` configuration file.

**Rationale**:
- **Flexibility**: Adjust timeouts without code changes
- **Environment-Specific**: Different timeouts for dev/test/prod
- **Centralized**: All timeout values in one place
- **Default Fallback**: Provides defaults if config missing

**Configuration Structure**:
```json
{
  "default_timeouts": {
    "game_join": 5,
    "choose_parity": 30,
    "registration": 10,
    "default": 10
  }
}
```

**Consequences**:
- ✅ Configurable without code changes
- ✅ Environment-specific settings
- ✅ Centralized configuration
- ⚠️ Requires config file management

---

## ADR-008: Error Code Enumeration

**Status**: Accepted  
**Date**: 2025-12-27  
**Context**: Need for standardized error reporting across the system.

**Decision**: Define all error codes in centralized enumeration (E001-E023).

**Rationale**:
- **Consistency**: All agents use same error codes
- **Documentation**: Centralized reference for all error codes
- **Type Safety**: Enum prevents typos and invalid codes
- **Extensibility**: Easy to add new error codes

**Structure**:
- Error codes defined in `SHARED/league_sdk/error_codes.py`
- Enum class for type safety
- Description mapping for human-readable messages
- Utility functions for error message creation

**Consequences**:
- ✅ Consistent error handling
- ✅ Type-safe error codes
- ✅ Centralized documentation
- ⚠️ Requires updating enum for new codes

---

## ADR-009: Structured JSON Logging

**Status**: Accepted  
**Date**: 2025-12-27  
**Context**: Need for machine-readable logs for debugging and monitoring.

**Decision**: Use structured JSON logging format.

**Rationale**:
- **Machine-Readable**: Easy to parse and analyze
- **Searchable**: Can query logs by fields
- **Extensible**: Easy to add new fields
- **Standard Format**: Works with log aggregation tools

**Format**:
```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "level": "INFO",
  "logger": "league_manager",
  "message": "Round 1 announced",
  "agent_id": "league_manager",
  "match_id": "R1M1"
}
```

**Consequences**:
- ✅ Machine-readable logs
- ✅ Easy log analysis
- ✅ Works with log aggregation
- ⚠️ Less human-readable than plain text
- ⚠️ Slightly larger file size

---

## ADR-010: Player Endpoint Discovery via ROUND_ANNOUNCEMENT

**Status**: Accepted  
**Date**: 2025-12-27  
**Context**: Referees need player endpoints to send game invitations.

**Decision**: Include player endpoints in ROUND_ANNOUNCEMENT message from League Manager.

**Rationale**:
- **Single Source of Truth**: League Manager knows all registered player endpoints
- **Flexibility**: Players can use any port/host, not hardcoded
- **Reliability**: No assumptions about port numbering
- **Centralized**: All endpoint information in one place

**Implementation**:
- League Manager includes `player_A_endpoint` and `player_B_endpoint` in match data
- Referee extracts endpoints from ROUND_ANNOUNCEMENT message
- No hardcoded port calculations

**Alternatives Considered**:
- **Hardcoded Formula**: Simple but breaks with non-standard ports
- **Separate Endpoint Query**: Adds extra round-trip, more complex
- **Service Discovery**: Overkill for this use case

**Consequences**:
- ✅ Works with any player configuration
- ✅ No hardcoded assumptions
- ✅ Single source of truth
- ⚠️ Slightly larger ROUND_ANNOUNCEMENT messages

---

## Trade-Off Analysis

### Technology Choices

**FastAPI vs Flask/Django**:
- ✅ FastAPI: Native async support, automatic OpenAPI docs, type hints
- ⚠️ Flask: Simpler but no native async
- ⚠️ Django: Overkill, heavier framework

**JSON-RPC vs REST**:
- ✅ JSON-RPC: Standardized, single endpoint, method-based
- ⚠️ REST: More verbose, multiple endpoints

**File Storage vs Database**:
- ✅ Files: Simple, no setup, easy to inspect
- ⚠️ Database: More robust but adds complexity

**Asyncio vs Threading**:
- ✅ Asyncio: Perfect for I/O-bound operations
- ⚠️ Threading: GIL limitations, more complex

---

## Performance Considerations

**Bottlenecks Identified**:
1. **File I/O**: Standings updates write to disk synchronously
   - **Mitigation**: Could use async file I/O (aiofiles) if needed
   - **Current**: Acceptable for tournament scale

2. **Network Latency**: HTTP requests between agents
   - **Mitigation**: Retry logic handles transient failures
   - **Current**: Acceptable for local/network agents

3. **League Manager**: Single point of coordination
   - **Mitigation**: Could add load balancing or clustering
   - **Current**: Sufficient for expected load

**Optimization Opportunities**:
- Batch standings updates (currently updates after each match)
- Connection pooling for HTTP clients (already using httpx.AsyncClient)
- Cache frequently accessed data (standings, player configs)

---

## Research Methodology

**Design Process**:
1. **Requirements Analysis**: Reviewed PRD and protocol specification
2. **Architecture Design**: Identified components and interactions
3. **Technology Selection**: Evaluated alternatives (see ADRs above)
4. **Implementation**: Built incrementally with testing
5. **Iteration**: Refined based on testing and review

**References**:
- Model Context Protocol (MCP) specification
- JSON-RPC 2.0 specification (https://www.jsonrpc.org/specification)
- FastAPI documentation (https://fastapi.tiangolo.com/)
- Python asyncio documentation

---

**Last Updated**: 2025-12-27

