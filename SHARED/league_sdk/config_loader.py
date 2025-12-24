"""Configuration loader for league system."""

from pathlib import Path
from typing import Dict, Any, Optional
import json
from .config_models import AgentConfig, LeagueConfig, GameConfig, load_config


def load_system_config(config_dir: Path) -> Dict[str, Any]:
    """Load system configuration."""
    config_file = config_dir / "system.json"
    if config_file.exists():
        return load_config(config_file)
    return {}


def load_league_config(config_dir: Path, league_id: str) -> Optional[Dict[str, Any]]:
    """Load league configuration."""
    config_file = config_dir / "leagues" / f"{league_id}.json"
    if config_file.exists():
        return load_config(config_file)
    return None


def load_game_registry(config_dir: Path) -> Dict[str, Any]:
    """Load game registry."""
    config_file = config_dir / "games" / "games_registry.json"
    if config_file.exists():
        return load_config(config_file)
    return {"games": {}}


def load_agent_defaults(config_dir: Path, agent_type: str) -> Dict[str, Any]:
    """Load default configuration for agent type."""
    config_file = config_dir / "defaults" / f"{agent_type}.json"
    if config_file.exists():
        return load_config(config_file)
    return {}


def load_agents_config(config_dir: Path) -> Dict[str, Any]:
    """Load agents configuration."""
    config_file = config_dir / "agents" / "agents_config.json"
    if config_file.exists():
        return load_config(config_file)
    return {}


def get_config_path(base_path: Optional[Path] = None) -> Path:
    """Get configuration directory path."""
    if base_path is None:
        # Default to SHARED/config relative to current file
        current_file = Path(__file__)
        return current_file.parent.parent / "config"
    return base_path / "config"

