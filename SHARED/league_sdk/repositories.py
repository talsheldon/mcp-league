"""Data repositories for league state management."""

from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from dataclasses import dataclass, asdict


@dataclass
class PlayerStanding:
    """Player standing in league."""
    rank: int
    player_id: str
    display_name: str
    played: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    points: int = 0


@dataclass
class MatchResult:
    """Match result."""
    match_id: str
    round_id: int
    player_A_id: str
    player_B_id: str
    winner: Optional[str]
    score: Dict[str, int]
    details: Dict[str, Any]


class StandingsRepository:
    """Repository for league standings."""
    
    def __init__(self, data_dir: Path, league_id: str):
        self.data_dir = data_dir / "leagues" / league_id
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.standings_file = self.data_dir / "standings.json"
        self._standings: Dict[str, PlayerStanding] = {}
        self._load()
    
    def _load(self) -> None:
        """Load standings from file."""
        if self.standings_file.exists():
            with open(self.standings_file, "r") as f:
                data = json.load(f)
                self._standings = {
                    pid: PlayerStanding(**s) for pid, s in data.items()
                }
    
    def _save(self) -> None:
        """Save standings to file."""
        data = {pid: asdict(standing) for pid, standing in self._standings.items()}
        with open(self.standings_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def initialize_player(self, player_id: str, display_name: str) -> None:
        """Initialize player in standings."""
        if player_id not in self._standings:
            self._standings[player_id] = PlayerStanding(
                rank=0,
                player_id=player_id,
                display_name=display_name,
            )
            self._save()
    
    def update_match_result(
        self,
        player_A_id: str,
        player_B_id: str,
        winner: Optional[str],
        score: Dict[str, int],
    ) -> None:
        """Update standings with match result."""
        for player_id in [player_A_id, player_B_id]:
            if player_id not in self._standings:
                continue
            
            standing = self._standings[player_id]
            standing.played += 1
            
            if winner == player_id:
                standing.wins += 1
                standing.points += score.get(player_id, 3)
            elif winner is None:
                standing.draws += 1
                standing.points += score.get(player_id, 1)
            else:
                standing.losses += 1
                standing.points += score.get(player_id, 0)
        
        self._update_ranks()
        self._save()
    
    def _update_ranks(self) -> None:
        """Update player ranks based on points."""
        sorted_players = sorted(
            self._standings.values(),
            key=lambda s: (-s.points, -s.wins, s.losses),
        )
        for rank, standing in enumerate(sorted_players, 1):
            standing.rank = rank
    
    def get_standings(self) -> List[PlayerStanding]:
        """Get current standings."""
        return sorted(
            self._standings.values(),
            key=lambda s: (s.rank, s.player_id),
        )
    
    def get_player_standing(self, player_id: str) -> Optional[PlayerStanding]:
        """Get standing for specific player."""
        return self._standings.get(player_id)


class MatchRepository:
    """Repository for match results."""
    
    def __init__(self, data_dir: Path, league_id: str):
        self.data_dir = data_dir / "matches" / league_id
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def save_match(self, match_id: str, result: MatchResult) -> None:
        """Save match result."""
        match_file = self.data_dir / f"{match_id}.json"
        with open(match_file, "w") as f:
            json.dump(asdict(result), f, indent=2)
    
    def load_match(self, match_id: str) -> Optional[MatchResult]:
        """Load match result."""
        match_file = self.data_dir / f"{match_id}.json"
        if match_file.exists():
            with open(match_file, "r") as f:
                data = json.load(f)
                return MatchResult(**data)
        return None


class HistoryRepository:
    """Repository for player game history."""
    
    def __init__(self, data_dir: Path, player_id: str):
        self.data_dir = data_dir / "players" / player_id
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.data_dir / "history.json"
        self._history: List[Dict[str, Any]] = []
        self._load()
    
    def _load(self) -> None:
        """Load history from file."""
        if self.history_file.exists():
            with open(self.history_file, "r") as f:
                self._history = json.load(f)
    
    def _save(self) -> None:
        """Save history to file."""
        with open(self.history_file, "w") as f:
            json.dump(self._history, f, indent=2)
    
    def add_game(self, game_data: Dict[str, Any]) -> None:
        """Add game to history."""
        self._history.append(game_data)
        self._save()
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get full game history."""
        return self._history.copy()

