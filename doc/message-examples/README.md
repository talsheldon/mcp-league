# Message Examples

This directory contains example JSON messages for the league.v2 protocol.

## Example Files

### Registration Messages
- `referee_register.json` - Referee registration request
- `player_register.json` - Player registration request

### Game Flow Messages
- `round_announcement.json` - Round announcement with match assignments
- `GAME_INVITATION.json` - Game invitation to players
- `GAME_JOIN_ACK.json` - Player acceptance of game invitation
- `CHOOSE_PARITY_CALL.json` - Parity choice request from referee
- `choose_parity_response.json` - Parity choice response from player
- `game_over.json` - Game completion message
- `match_result.json` - Match result report to League Manager

### League Management Messages
- `start_league.json` - Start league request
- `league_status.json` - League status response
- `ROUND_COMPLETED.json` - Round completion notification
- `LEAGUE_STANDINGS_UPDATE.json` - Standings update broadcast
- `LEAGUE_COMPLETED.json` - League completion notification
- `league_query.json` - League query request
- `league_query_response.json` - League query response
- `league_error.json` - Error message example

## Usage

These examples can be used for:
- Testing message creation and validation
- Understanding message structure
- Integration testing
- Protocol implementation reference

See `protocol-spec.md` for complete message specifications.

