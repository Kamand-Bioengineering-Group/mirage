"""
Storage interfaces and implementations for competition data.
This module provides a uniform interface for data access regardless of 
the underlying storage mechanism (local files or Firebase).
"""
from abc import ABC, abstractmethod
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Protocol

from ..core.models import Player, PlayerAttempt, Scenario, SimulationResults, LeaderboardEntry


class StorageProvider(ABC):
    """Abstract base class for storage providers."""
    
    @abstractmethod
    def save_player(self, player: Player) -> bool:
        """Save player information."""
        pass
    
    @abstractmethod
    def get_player(self, player_id: str) -> Optional[Player]:
        """Get player by ID."""
        pass
    
    @abstractmethod
    def list_players(self) -> List[Player]:
        """List all players."""
        pass
    
    @abstractmethod
    def save_attempt(self, attempt: PlayerAttempt) -> bool:
        """Save an attempt."""
        pass
    
    @abstractmethod
    def get_attempt(self, attempt_id: str) -> Optional[PlayerAttempt]:
        """Get attempt by ID."""
        pass
    
    @abstractmethod
    def list_attempts(self, player_id: Optional[str] = None, 
                     scenario_id: Optional[str] = None,
                     is_official: Optional[bool] = None) -> List[PlayerAttempt]:
        """List attempts, optionally filtered."""
        pass
    
    @abstractmethod
    def save_scenario(self, scenario: Scenario) -> bool:
        """Save a scenario configuration."""
        pass
    
    @abstractmethod
    def get_scenario(self, scenario_id: str) -> Optional[Scenario]:
        """Get scenario by ID."""
        pass
    
    @abstractmethod
    def list_scenarios(self) -> List[Scenario]:
        """List all scenarios."""
        pass
    
    @abstractmethod
    def save_leaderboard(self, entries: List[LeaderboardEntry]) -> bool:
        """Save the current leaderboard."""
        pass
    
    @abstractmethod
    def get_leaderboard(self) -> List[LeaderboardEntry]:
        """Get the current leaderboard."""
        pass


class LocalStorageProvider(StorageProvider):
    """Stores competition data in local JSON files."""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize with data directory path."""
        self.data_dir = Path(data_dir)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        (self.data_dir / "players").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "attempts").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "scenarios").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "leaderboard").mkdir(parents=True, exist_ok=True)
    
    def save_player(self, player: Player) -> bool:
        """Save player information to a JSON file."""
        try:
            with open(self.data_dir / "players" / f"{player.id}.json", "w") as f:
                json.dump(player.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving player: {e}")
            return False
    
    def get_player(self, player_id: str) -> Optional[Player]:
        """Get player from JSON file by ID."""
        try:
            file_path = self.data_dir / "players" / f"{player_id}.json"
            if not file_path.exists():
                return None
                
            with open(file_path, "r") as f:
                data = json.load(f)
                return Player.from_dict(data)
        except Exception as e:
            print(f"Error getting player: {e}")
            return None
    
    def list_players(self) -> List[Player]:
        """List all players from JSON files."""
        players = []
        try:
            player_dir = self.data_dir / "players"
            for file_path in player_dir.glob("*.json"):
                with open(file_path, "r") as f:
                    data = json.load(f)
                    players.append(Player.from_dict(data))
            return players
        except Exception as e:
            print(f"Error listing players: {e}")
            return []
    
    def save_attempt(self, attempt: PlayerAttempt) -> bool:
        """Save an attempt to a JSON file."""
        try:
            with open(self.data_dir / "attempts" / f"{attempt.id}.json", "w") as f:
                json.dump(attempt.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving attempt: {e}")
            return False
    
    def get_attempt(self, attempt_id: str) -> Optional[PlayerAttempt]:
        """Get attempt from JSON file by ID."""
        try:
            file_path = self.data_dir / "attempts" / f"{attempt_id}.json"
            if not file_path.exists():
                return None
                
            with open(file_path, "r") as f:
                data = json.load(f)
                return PlayerAttempt.from_dict(data)
        except Exception as e:
            print(f"Error getting attempt: {e}")
            return None
    
    def list_attempts(self, player_id: Optional[str] = None, 
                     scenario_id: Optional[str] = None,
                     is_official: Optional[bool] = None) -> List[PlayerAttempt]:
        """List attempts, optionally filtered."""
        attempts = []
        try:
            attempt_dir = self.data_dir / "attempts"
            for file_path in attempt_dir.glob("*.json"):
                with open(file_path, "r") as f:
                    data = json.load(f)
                    attempt = PlayerAttempt.from_dict(data)
                    
                    # Apply filters
                    if player_id and attempt.player_id != player_id:
                        continue
                    if scenario_id and attempt.scenario_id != scenario_id:
                        continue
                    if is_official is not None and attempt.is_official != is_official:
                        continue
                        
                    attempts.append(attempt)
            return attempts
        except Exception as e:
            print(f"Error listing attempts: {e}")
            return []
    
    def save_scenario(self, scenario: Scenario) -> bool:
        """Save a scenario to a JSON file."""
        try:
            with open(self.data_dir / "scenarios" / f"{scenario.id}.json", "w") as f:
                json.dump(scenario.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving scenario: {e}")
            return False
    
    def get_scenario(self, scenario_id: str) -> Optional[Scenario]:
        """Get scenario from JSON file by ID."""
        try:
            file_path = self.data_dir / "scenarios" / f"{scenario_id}.json"
            if not file_path.exists():
                return None
                
            with open(file_path, "r") as f:
                data = json.load(f)
                return Scenario.from_dict(data)
        except Exception as e:
            print(f"Error getting scenario: {e}")
            return None
    
    def list_scenarios(self) -> List[Scenario]:
        """List all scenarios from JSON files."""
        scenarios = []
        try:
            scenario_dir = self.data_dir / "scenarios"
            for file_path in scenario_dir.glob("*.json"):
                with open(file_path, "r") as f:
                    data = json.load(f)
                    scenarios.append(Scenario.from_dict(data))
            return scenarios
        except Exception as e:
            print(f"Error listing scenarios: {e}")
            return []
    
    def save_leaderboard(self, entries: List[LeaderboardEntry]) -> bool:
        """Save the current leaderboard to a JSON file."""
        try:
            leaderboard_data = [entry.to_dict() for entry in entries]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save timestamped version for history
            with open(self.data_dir / "leaderboard" / f"leaderboard_{timestamp}.json", "w") as f:
                json.dump(leaderboard_data, f, indent=2)
                
            # Save current version
            with open(self.data_dir / "leaderboard" / "current_leaderboard.json", "w") as f:
                json.dump(leaderboard_data, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error saving leaderboard: {e}")
            return False
    
    def get_leaderboard(self) -> List[LeaderboardEntry]:
        """Get the current leaderboard from JSON file."""
        try:
            file_path = self.data_dir / "leaderboard" / "current_leaderboard.json"
            if not file_path.exists():
                return []
                
            with open(file_path, "r") as f:
                data = json.load(f)
                return [LeaderboardEntry(**entry) for entry in data]
        except Exception as e:
            print(f"Error getting leaderboard: {e}")
            return []


# Placeholder for future Firebase implementation
class FirebaseStorageProvider(StorageProvider):
    """Stores competition data in Firebase."""
    
    def __init__(self, firebase_app=None):
        """Initialize with Firebase app reference."""
        self.firebase_app = firebase_app
        # Firebase storage would be initialized here
        # self.db = firebase_app.firestore()
        
    def save_player(self, player: Player) -> bool:
        """Save player to Firebase."""
        # Placeholder implementation
        print("Firebase save_player would be called with:", player.to_dict())
        return True
    
    def get_player(self, player_id: str) -> Optional[Player]:
        """Get player from Firebase by ID."""
        # Placeholder implementation
        print("Firebase get_player would be called with ID:", player_id)
        return None
    
    def list_players(self) -> List[Player]:
        """List all players from Firebase."""
        # Placeholder implementation
        print("Firebase list_players would be called")
        return []
    
    def save_attempt(self, attempt: PlayerAttempt) -> bool:
        """Save an attempt to Firebase."""
        # Placeholder implementation
        print("Firebase save_attempt would be called with:", attempt.to_dict())
        return True
    
    def get_attempt(self, attempt_id: str) -> Optional[PlayerAttempt]:
        """Get attempt from Firebase by ID."""
        # Placeholder implementation
        print("Firebase get_attempt would be called with ID:", attempt_id)
        return None
    
    def list_attempts(self, player_id: Optional[str] = None, 
                     scenario_id: Optional[str] = None,
                     is_official: Optional[bool] = None) -> List[PlayerAttempt]:
        """List attempts from Firebase, optionally filtered."""
        # Placeholder implementation
        print("Firebase list_attempts would be called with filters:",
              {"player_id": player_id, "scenario_id": scenario_id, "is_official": is_official})
        return []
    
    def save_scenario(self, scenario: Scenario) -> bool:
        """Save a scenario to Firebase."""
        # Placeholder implementation
        print("Firebase save_scenario would be called with:", scenario.to_dict())
        return True
    
    def get_scenario(self, scenario_id: str) -> Optional[Scenario]:
        """Get scenario from Firebase by ID."""
        # Placeholder implementation
        print("Firebase get_scenario would be called with ID:", scenario_id)
        return None
    
    def list_scenarios(self) -> List[Scenario]:
        """List all scenarios from Firebase."""
        # Placeholder implementation
        print("Firebase list_scenarios would be called")
        return []
    
    def save_leaderboard(self, entries: List[LeaderboardEntry]) -> bool:
        """Save the current leaderboard to Firebase."""
        # Placeholder implementation
        print("Firebase save_leaderboard would be called with entries count:", len(entries))
        return True
    
    def get_leaderboard(self) -> List[LeaderboardEntry]:
        """Get the current leaderboard from Firebase."""
        # Placeholder implementation
        print("Firebase get_leaderboard would be called")
        return [] 