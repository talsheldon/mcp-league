# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-12-27

### Added
- Initial implementation of MCP League tournament system
- League Manager agent for tournament orchestration
- Referee agent for game management
- Player agent with strategy support
- Shared SDK with common utilities
- Round-robin tournament scheduling
- Message-based communication protocol (league.v2)
- Error code enumeration (E001-E023)
- Retry logic with exponential backoff
- Comprehensive test suite
- Product Requirements Document (PRD.md)
- Architecture documentation (ARCHITECTURE.md)
- Design Decision Records (DESIGN_DECISIONS.md)
- Complete message examples
- Integration tests
- Error handling tests

### Fixed
- Player endpoint discovery (now uses ROUND_ANNOUNCEMENT data)
- Configuration-based timeouts (loaded from system.json)
- Max concurrent matches enforcement
- Error code implementation completeness

### Changed
- Improved code documentation with comprehensive docstrings
- Enhanced error handling with standardized error codes
- Updated message examples to include all message types

---

## [Unreleased]

### Planned
- Performance benchmarks and analysis
- Additional test coverage improvements
- Security enhancements (token expiration, rate limiting)
- Visual diagrams (sequence diagrams, state machines)

