"""Configuration loader for league system."""

from pathlib import Path
from typing import Dict, Any, Optional
import json
from .config_models import AgentConfig, LeagueConfig, GameConfig, load_config


def load_system_config(config_dir: Path) -> Dict[str, Any]:
    """Load system configuration from system.json.
    
    Args:
        config_dir: Path to configuration directory
        
    Returns:
        Dictionary with system configuration or empty dict if file not found
    """
    config_file = config_dir / "system.json"
    if config_file.exists():
        return load_config(config_file)
    return {}


def load_league_config(config_dir: Path, league_id: str) -> Optional[Dict[str, Any]]:
    """Load league-specific configuration.
    
    Args:
        config_dir: Path to configuration directory
        league_id: Identifier of the league
        
    Returns:
        Dictionary with league configuration or None if file not found
    """
    config_file = config_dir / "leagues" / f"{league_id}.json"
    if config_file.exists():
        return load_config(config_file)
    return None


def load_game_registry(config_dir: Path) -> Dict[str, Any]:
    """Load game type registry.
    
    Args:
        config_dir: Path to configuration directory
        
    Returns:
        Dictionary with games registry or default empty games dict
    """
    config_file = config_dir / "games" / "games_registry.json"
    if config_file.exists():
        return load_config(config_file)
    return {"games": {}}


def load_agent_defaults(config_dir: Path, agent_type: str) -> Dict[str, Any]:
    """Load default configuration for an agent type.
    
    Args:
        config_dir: Path to configuration directory
        agent_type: Type of agent (e.g., "referee", "player")
        
    Returns:
        Dictionary with default configuration or empty dict if file not found
    """
    config_file = config_dir / "defaults" / f"{agent_type}.json"
    if config_file.exists():
        return load_config(config_file)
    return {}


def load_agents_config(config_dir: Path) -> Dict[str, Any]:
    """Load agents configuration file.
    
    Args:
        config_dir: Path to configuration directory
        
    Returns:
        Dictionary with agents configuration or empty dict if file not found
    """
    config_file = config_dir / "agents" / "agents_config.json"
    if config_file.exists():
        return load_config(config_file)
    return {}


def get_config_path(base_path: Optional[Path] = None) -> Path:
    """Get configuration directory path.
    
    Args:
        base_path: Optional base path, defaults to SHARED/config
        
    Returns:
        Path to configuration directory
    """
    if base_path is None:
        # Default to SHARED/config relative to current file
        current_file = Path(__file__)
        return current_file.parent.parent / "config"
    return base_path / "config"

