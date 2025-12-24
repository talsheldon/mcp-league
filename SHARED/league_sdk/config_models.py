"""Configuration models for league agents."""

from dataclasses import dataclass
from typing import List, Optional
import json
from pathlib import Path


@dataclass
class AgentConfig:
    """Agent configuration."""
    agent_id: str
    display_name: str
    version: str
    contact_endpoint: str
    game_types: List[str]


@dataclass
class LeagueConfig:
    """League configuration."""
    league_id: str
    game_type: str
    players: List[str]
    referees: List[str]
    rounds: int


@dataclass
class GameConfig:
    """Game configuration."""
    game_type: str
    min_number: int = 1
    max_number: int = 10
    choice_timeout: int = 30
    join_timeout: int = 5


def load_config(config_path: Path) -> dict:
    """Load configuration from JSON file."""
    with open(config_path, "r") as f:
        return json.load(f)

