# Product Requirements Document (PRD)
## MCP League - Even/Odd Tournament System

**Version**: 1.0  
**Date**: 2025-12-27  
**Status**: Final

---

## 1. Product Overview

### 1.1 Product Name
MCP League - Even/Odd Tournament System

### 1.2 Product Purpose
A multi-agent system that orchestrates round-robin tournaments where AI agents compete in an Even/Odd number guessing game. The system enables autonomous agents to register, participate in matches, and compete in a structured league format using the Model Context Protocol (MCP).

### 1.3 Product Goals
- Provide a standardized platform for agent-to-agent competition
- Enable fair tournament scheduling through round-robin format
- Support autonomous agent registration and communication
- Track and maintain league standings and match results
- Ensure reliable game execution through referee agents
- Provide extensible architecture for future game types

### 1.4 Target Users
- **Primary**: AI agent developers who want to test their agents in competitive scenarios
- **Secondary**: Researchers studying multi-agent systems and game theory
- **Tertiary**: System operators managing league infrastructure

---

## 2. Objectives

### 2.1 Primary Objectives
1. **Reliability**: System must reliably orchestrate tournaments with 100% match completion rate
2. **Fairness**: All players must play equal number of matches through round-robin scheduling
3. **Autonomy**: Agents must operate independently with minimal human intervention
4. **Extensibility**: System must support adding new game types and agent strategies
5. **Observability**: System must provide comprehensive logging and result tracking

### 2.2 Success Criteria
- ✅ All registered agents can participate in matches
- ✅ League completes with accurate final standings
- ✅ Match results are correctly recorded and persisted
- ✅ System handles agent failures gracefully
- ✅ Protocol compliance verified through automated tests
- ✅ Documentation enables new developers to understand and extend the system

### 2.3 Key Performance Indicators (KPIs)
- **Match Completion Rate**: >95% of scheduled matches complete successfully
- **Registration Success Rate**: 100% of valid registration requests accepted
- **Message Delivery Success**: >99% of protocol messages delivered successfully
- **System Uptime**: >99% availability during active leagues
- **Test Coverage**: >80% code coverage with comprehensive integration tests

---

## 3. Functional Requirements

### 3.1 Agent Registration

#### 3.1.1 Referee Registration
**FR-001**: System MUST accept referee registration requests  
**FR-002**: System MUST assign unique referee IDs (format: REF01, REF02, etc.)  
**FR-003**: System MUST validate referee metadata (display_name, version, game_types, contact_endpoint, max_concurrent_matches)  
**FR-004**: System MUST generate and return authentication tokens for registered referees  
**FR-005**: System MUST reject duplicate registrations from same endpoint

#### 3.1.2 Player Registration
**FR-006**: System MUST accept player registration requests  
**FR-007**: System MUST assign unique player IDs (format: P01, P02, etc.)  
**FR-008**: System MUST validate player metadata (display_name, version, game_types, contact_endpoint)  
**FR-009**: System MUST generate and return authentication tokens for registered players  
**FR-010**: System MUST require minimum 2 players before league can start

### 3.2 League Management

#### 3.2.1 League Initialization
**FR-011**: System MUST generate round-robin schedule for all registered players  
**FR-012**: System MUST calculate correct number of rounds based on player count  
**FR-013**: System MUST initialize standings for all players  
**FR-014**: System MUST assign referees to matches in round-robin fashion

#### 3.2.2 Round Management
**FR-015**: System MUST announce rounds to all registered agents  
**FR-016**: System MUST track match completion status per round  
**FR-017**: System MUST advance to next round when all matches in current round complete  
**FR-018**: System MUST send round completion notifications

#### 3.2.3 League Completion
**FR-019**: System MUST detect when all rounds are complete  
**FR-020**: System MUST determine league champion (player with highest points)  
**FR-021**: System MUST send league completion message to all agents  
**FR-022**: System MUST provide final standings in completion message

### 3.3 Game Execution

#### 3.3.1 Game Invitation
**FR-023**: Referee MUST send game invitations to both players  
**FR-024**: Invitation MUST include match_id, round_id, game_type, role_in_match, opponent_id  
**FR-025**: Players MUST respond with GAME_JOIN_ACK within timeout period  
**FR-026**: Game MUST not start if either player fails to join

#### 3.3.2 Parity Choice Collection
**FR-027**: Referee MUST send CHOOSE_PARITY_CALL to each player with deadline  
**FR-028**: Players MUST respond with CHOOSE_PARITY_RESPONSE (even or odd)  
**FR-029**: Referee MUST enforce deadline for parity choices  
**FR-030**: Referee MUST handle timeout scenarios (technical loss)

#### 3.3.3 Game Result Calculation
**FR-031**: Referee MUST draw random number (1-10)  
**FR-032**: Referee MUST determine number parity (even/odd)  
**FR-033**: Referee MUST determine winner based on matching choices  
**FR-034**: Referee MUST handle draw scenarios (both players choose same, number matches)  
**FR-035**: Referee MUST send GAME_OVER message to both players with result

#### 3.3.4 Match Result Reporting
**FR-036**: Referee MUST report match result to League Manager  
**FR-037**: Report MUST include winner, score, and game details  
**FR-038**: League Manager MUST update standings based on result  
**FR-039**: League Manager MUST send standings update to all players

### 3.4 Communication Protocol

#### 3.4.1 Message Format
**FR-040**: All messages MUST follow league.v2 protocol specification  
**FR-041**: All messages MUST include required envelope fields (protocol, message_type, sender, timestamp, conversation_id)  
**FR-042**: All messages MUST use JSON-RPC 2.0 over HTTP  
**FR-043**: All timestamps MUST be in ISO-8601 format with UTC timezone

#### 3.4.2 Message Delivery
**FR-044**: System MUST deliver messages with retry logic for transient failures  
**FR-045**: System MUST handle message delivery timeouts  
**FR-046**: System MUST log all message send/receive events

#### 3.4.3 Error Handling
**FR-047**: System MUST return appropriate error codes for invalid requests  
**FR-048**: System MUST include error context in error messages  
**FR-049**: System MUST handle authentication failures gracefully

### 3.5 Data Persistence

#### 3.5.1 Standings Management
**FR-050**: System MUST persist standings after each match  
**FR-051**: Standings MUST include wins, losses, draws, points, rank  
**FR-052**: System MUST maintain standings across system restarts

#### 3.5.2 Match History
**FR-053**: System MUST store match results with full game details  
**FR-054**: System MUST maintain player-specific game history  
**FR-055**: System MUST enable querying of historical matches

### 3.6 Query and Status

#### 3.6.1 League Queries
**FR-056**: Players MUST be able to query current standings  
**FR-057**: Players MUST be able to query next match information  
**FR-058**: Queries MUST require valid authentication token  
**FR-059**: System MUST return query results in standardized format

---

## 4. Non-Functional Requirements

### 4.1 Performance Requirements

#### 4.1.1 Response Time
**NFR-001**: Message processing MUST complete within 100ms for standard operations  
**NFR-002**: Registration requests MUST be processed within 500ms  
**NFR-003**: Game result calculation MUST complete within 50ms

#### 4.1.2 Throughput
**NFR-004**: System MUST handle at least 10 concurrent games per referee  
**NFR-005**: System MUST support at least 20 registered players  
**NFR-006**: System MUST process at least 100 messages per second

### 4.2 Scalability Requirements

#### 4.2.1 Horizontal Scaling
**NFR-007**: System MUST support multiple referee instances  
**NFR-008**: System MUST support multiple league manager instances (with shared state)  
**NFR-009**: System MUST distribute load across available referees

#### 4.2.2 Resource Usage
**NFR-010**: Each agent process MUST use less than 512MB RAM  
**NFR-011**: System MUST handle leagues with up to 50 players

### 4.3 Reliability Requirements

#### 4.3.1 Availability
**NFR-012**: System MUST maintain 99% uptime during active leagues  
**NFR-013**: System MUST recover gracefully from agent failures  
**NFR-014**: System MUST persist state to survive process restarts

#### 4.3.2 Error Recovery
**NFR-015**: System MUST retry failed message deliveries up to 3 times  
**NFR-016**: System MUST handle network timeouts without crashing  
**NFR-017**: System MUST log all errors for debugging

### 4.4 Security Requirements

#### 4.4.1 Authentication
**NFR-018**: System MUST validate authentication tokens for protected operations  
**NFR-019**: System MUST generate cryptographically secure tokens  
**NFR-020**: System MUST reject requests with invalid tokens

#### 4.4.2 Input Validation
**NFR-021**: System MUST validate all message fields before processing  
**NFR-022**: System MUST sanitize all user inputs  
**NFR-023**: System MUST reject malformed messages

### 4.5 Usability Requirements

#### 4.5.1 Documentation
**NFR-024**: System MUST provide comprehensive README with setup instructions  
**NFR-025**: System MUST document all protocol messages with examples  
**NFR-026**: System MUST provide troubleshooting guide

#### 4.5.2 Observability
**NFR-027**: System MUST provide structured JSON logging  
**NFR-028**: System MUST log all significant events  
**NFR-029**: System MUST enable log aggregation and analysis

---

## 5. User Stories / Use Cases

### 5.1 Referee Agent Use Cases

#### UC-001: Referee Registration
**As a** referee agent developer  
**I want to** register my referee with the league manager  
**So that** my referee can be assigned to matches

**Acceptance Criteria**:
- Referee sends REFEREE_REGISTER_REQUEST with valid metadata
- League Manager responds with REFEREE_REGISTER_RESPONSE (ACCEPTED)
- Referee receives unique ID and authentication token
- Referee is available for match assignments

#### UC-002: Match Assignment
**As a** referee agent  
**I want to** receive match assignments from the league manager  
**So that** I can orchestrate games

**Acceptance Criteria**:
- Referee receives ROUND_ANNOUNCEMENT with assigned matches
- Referee identifies matches where it is the assigned referee
- Referee initiates game flow for assigned matches

#### UC-003: Game Orchestration
**As a** referee agent  
**I want to** orchestrate a complete game between two players  
**So that** a fair match result is determined

**Acceptance Criteria**:
- Referee sends game invitations to both players
- Both players accept and join the game
- Referee collects parity choices from both players
- Referee determines winner and reports result
- Both players receive game result

### 5.2 Player Agent Use Cases

#### UC-004: Player Registration
**As a** player agent developer  
**I want to** register my player with the league manager  
**So that** my player can participate in the tournament

**Acceptance Criteria**:
- Player sends LEAGUE_REGISTER_REQUEST with valid metadata
- League Manager responds with LEAGUE_REGISTER_RESPONSE (ACCEPTED)
- Player receives unique ID and authentication token
- Player is included in league schedule

#### UC-005: Game Participation
**As a** player agent  
**I want to** receive game invitations and participate in matches  
**So that** I can compete in the tournament

**Acceptance Criteria**:
- Player receives GAME_INVITATION for assigned match
- Player responds with GAME_JOIN_ACK (accept=True)
- Player receives CHOOSE_PARITY_CALL with deadline
- Player responds with CHOOSE_PARITY_RESPONSE
- Player receives GAME_OVER with match result

#### UC-006: Standings Query
**As a** player agent  
**I want to** query current league standings  
**So that** I can track my position in the tournament

**Acceptance Criteria**:
- Player sends LEAGUE_QUERY with valid auth token
- League Manager responds with current standings
- Standings include rank, wins, losses, points

### 5.3 League Manager Use Cases

#### UC-007: League Initialization
**As a** league operator  
**I want to** start a league with registered players  
**So that** the tournament can begin

**Acceptance Criteria**:
- At least 2 players are registered
- League Manager generates round-robin schedule
- League Manager sends ROUND_ANNOUNCEMENT to all agents
- League status changes to "running"

#### UC-008: Standings Management
**As a** league manager  
**I want to** maintain accurate standings  
**So that** players can track their progress

**Acceptance Criteria**:
- Standings updated after each match result
- Standings persisted to disk
- Standings broadcast to all players after updates
- Standings correctly rank players by points

---

## 6. Acceptance Criteria

### 6.1 Functional Acceptance Criteria

**AC-001**: System successfully registers at least 2 players and 1 referee  
**AC-002**: System generates valid round-robin schedule for any number of players (2-50)  
**AC-003**: System completes at least 95% of scheduled matches successfully  
**AC-004**: System correctly determines winners for all completed games  
**AC-005**: System maintains accurate standings throughout tournament  
**AC-006**: System completes full league and determines champion  
**AC-007**: All protocol messages comply with league.v2 specification  
**AC-008**: System handles agent failures without crashing  
**AC-009**: System persists all match results and standings

### 6.2 Non-Functional Acceptance Criteria

**AC-010**: System processes messages within specified time limits  
**AC-011**: System supports concurrent games as configured  
**AC-012**: System provides comprehensive logging for debugging  
**AC-013**: System validates all inputs and rejects invalid data  
**AC-014**: System has >80% test coverage including integration tests

---

## 7. Stakeholder Requirements

### 7.1 Developer Requirements
- Clear code structure and documentation
- Comprehensive test suite for confidence in changes
- Extensible architecture for adding features
- Type hints and docstrings for IDE support

### 7.2 Operator Requirements
- Simple deployment and configuration
- Comprehensive logging for troubleshooting
- Health check endpoints
- Graceful error handling

### 7.3 Agent Developer Requirements
- Clear protocol documentation
- Message examples for all types
- Error code reference
- Testing utilities

---

## 8. Constraints

### 8.1 Technical Constraints
- **Protocol**: Must use JSON-RPC 2.0 over HTTP
- **Language**: Python 3.10+ required
- **Dependencies**: Must use specified libraries (FastAPI, Pydantic, etc.)
- **Storage**: File-based JSON storage (no database requirement)
- **Communication**: HTTP-based, no direct inter-process communication

### 8.2 Business Constraints
- **Timeline**: Must be deliverable within project timeframe
- **Resources**: Must run on standard development machines
- **Compatibility**: Must work on macOS, Linux, Windows

### 8.3 Regulatory Constraints
- None specified

---

## 9. Assumptions

### 9.1 Technical Assumptions
- Agents are network-accessible via HTTP
- Agents implement the league.v2 protocol correctly
- Network latency is acceptable (<100ms for local agents)
- File system is available for data persistence
- System clock is synchronized across agents

### 9.2 Business Assumptions
- Agents will register before league starts
- Agents will respond to messages within timeout periods
- League operators will monitor system health
- Developers have Python 3.10+ installed

### 9.3 Operational Assumptions
- League Manager runs continuously during active leagues
- Referees and Players can be started/stopped independently
- Log files can be rotated and archived
- Configuration files are managed by operators

---

## 10. Out of Scope

The following are explicitly **NOT** included in this version:

- Web-based user interface or dashboard
- Real-time match visualization
- Agent strategy evaluation or ranking
- Multi-league management (single league per instance)
- Agent performance analytics
- Automated agent deployment
- Cloud deployment automation
- Database backend (file-based only)
- WebSocket communication (HTTP only)
- Mobile applications

---

## 11. Success Metrics

### 11.1 Functional Metrics
- **Match Completion Rate**: >95%
- **Registration Success Rate**: 100%
- **Protocol Compliance**: 100% of messages valid
- **Standings Accuracy**: 100% correct calculations

### 11.2 Quality Metrics
- **Test Coverage**: >80%
- **Code Documentation**: >90% of functions documented
- **Error Handling**: All error codes implemented and tested
- **Type Safety**: >95% type hint coverage

### 11.3 Performance Metrics
- **Message Processing**: <100ms average
- **Game Completion**: <5 seconds per game
- **System Startup**: <10 seconds for all agents

---

## 12. Dependencies

### 12.1 External Dependencies
- Python 3.10+
- FastAPI for HTTP server
- Pydantic for data validation
- httpx for HTTP client
- pytest for testing

### 12.2 Internal Dependencies
- Shared SDK (league_sdk) must be installed
- Configuration files must be present
- Network connectivity between agents

---

## 13. Risks and Mitigations

### 13.1 Technical Risks
- **Risk**: Agent failures during matches  
  **Mitigation**: Timeout handling and technical loss assignment

- **Risk**: Network connectivity issues  
  **Mitigation**: Retry logic and error reporting

- **Risk**: Data corruption in JSON files  
  **Mitigation**: Atomic writes and validation

### 13.2 Operational Risks
- **Risk**: Configuration errors  
  **Mitigation**: Configuration validation on startup

- **Risk**: Port conflicts  
  **Mitigation**: Clear documentation and error messages

---

## 14. Future Enhancements

Potential future features (not in v1.0):
- Web dashboard for league monitoring
- Support for additional game types
- Agent performance analytics
- Multi-league support
- Database backend option
- Real-time match streaming
- Agent marketplace

---

## Document Approval

**Prepared by**: Development Team  
**Reviewed by**: [To be filled]  
**Approved by**: [To be filled]  
**Date**: 2025-12-27

---

**End of PRD**

