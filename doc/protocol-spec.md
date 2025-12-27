# League Protocol Specification

## Protocol Version: league.v2

This document specifies the message protocol for the Even/Odd League system.

## Message Envelope

All messages follow a common envelope structure:

```json
{
  "protocol": "league.v2",
  "message_type": "MESSAGE_TYPE",
  "sender": "agent_type:agent_id",
  "timestamp": "2025-01-15T10:00:00Z",
  "conversation_id": "conv-unique-id"
}
```

### Required Fields

- `protocol`: Protocol version (must be "league.v2")
- `message_type`: Type of message
- `sender`: Sender identifier in format `agent_type:agent_id`
- `timestamp`: ISO-8601 timestamp in UTC (must end with "Z")
- `conversation_id`: Unique conversation identifier

### Optional Fields

- `auth_token`: Authentication token for protected operations
- `league_id`: League identifier
- `match_id`: Match identifier
- `round_id`: Round number

## Message Types

See message examples in `message-examples/` for detailed message specifications.

## Agent Types

1. **League Manager**: `league_manager`
2. **Referee**: `referee:REF01`, `referee:REF02`, etc.
3. **Player**: `player:P01`, `player:P02`, etc.

## Communication

- All communication uses JSON-RPC 2.0 over HTTP
- Endpoint: `/mcp` on each agent's server
- Default ports:
  - League Manager: 8000
  - Referees: 8001, 8002, etc.
  - Players: 8101, 8102, etc.

## Error Handling

Error codes are defined in the protocol specification.

