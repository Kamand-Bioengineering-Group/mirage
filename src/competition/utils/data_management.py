"""
Data management utilities for the competition system.
This module provides tools for backup, import/export, and scenario management.
"""
import os
import json
import shutil
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import zipfile

from ..core.models import Player, PlayerAttempt, Scenario, SimulationResults, LeaderboardEntry
from ..data.storage import StorageProvider, LocalStorageProvider


class DataManager:
    """Utility class for competition data management."""
    
    def __init__(self, storage_provider: StorageProvider):
        """Initialize with a storage provider."""
        self.storage = storage_provider
        
    def backup_data(self, backup_dir: str = "backups", include_timestamp: bool = True) -> str:
        """
        Create a backup of all competition data.
        
        Args:
            backup_dir: Directory to store backups
            include_timestamp: Whether to include timestamp in backup name
            
        Returns:
            Path to the created backup
        """
        # Create backup directory if it doesn't exist
        backup_path = Path(backup_dir)
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Create backup filename with timestamp if requested
        if include_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"competition_backup_{timestamp}"
        else:
            backup_name = "competition_backup"
            
        backup_file = backup_path / f"{backup_name}.zip"
        
        # Create a temporary directory for organizing backup files
        temp_dir = backup_path / f"temp_{int(time.time())}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # If using LocalStorageProvider, directly copy data files
            if isinstance(self.storage, LocalStorageProvider):
                data_dir = Path(self.storage.data_dir)
                
                # Create subdirectories
                (temp_dir / "players").mkdir(parents=True, exist_ok=True)
                (temp_dir / "attempts").mkdir(parents=True, exist_ok=True)
                (temp_dir / "scenarios").mkdir(parents=True, exist_ok=True)
                (temp_dir / "leaderboard").mkdir(parents=True, exist_ok=True)
                
                # Copy files
                if (data_dir / "players").exists():
                    for file in (data_dir / "players").glob("*.json"):
                        shutil.copy(file, temp_dir / "players" / file.name)
                        
                if (data_dir / "attempts").exists():
                    for file in (data_dir / "attempts").glob("*.json"):
                        shutil.copy(file, temp_dir / "attempts" / file.name)
                        
                if (data_dir / "scenarios").exists():
                    for file in (data_dir / "scenarios").glob("*.json"):
                        shutil.copy(file, temp_dir / "scenarios" / file.name)
                        
                if (data_dir / "leaderboard").exists():
                    for file in (data_dir / "leaderboard").glob("*.json"):
                        shutil.copy(file, temp_dir / "leaderboard" / file.name)
            else:
                # For other storage providers, fetch and serialize data
                self._export_players(temp_dir / "players")
                self._export_attempts(temp_dir / "attempts")  
                self._export_scenarios(temp_dir / "scenarios")
                self._export_leaderboard(temp_dir / "leaderboard")
                
            # Create zip archive
            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)
                        
            print(f"Backup created at: {backup_file}")
            return str(backup_file)
            
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    def restore_backup(self, backup_file: str, target_dir: Optional[str] = None) -> bool:
        """
        Restore data from a backup file.
        
        Args:
            backup_file: Path to backup zip file
            target_dir: Directory to restore to (uses storage provider dir if None)
            
        Returns:
            Success status
        """
        backup_path = Path(backup_file)
        if not backup_path.exists() or not backup_path.is_file():
            print(f"Error: Backup file {backup_file} not found")
            return False
            
        # Determine target directory
        if target_dir:
            restore_dir = Path(target_dir)
        elif isinstance(self.storage, LocalStorageProvider):
            restore_dir = Path(self.storage.data_dir)
        else:
            restore_dir = Path("restored_data")
            
        # Create temporary directory for extraction
        temp_dir = Path(f"temp_restore_{int(time.time())}")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Extract backup
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(temp_dir)
                
            # Create target directories
            restore_dir.mkdir(parents=True, exist_ok=True)
            (restore_dir / "players").mkdir(parents=True, exist_ok=True)
            (restore_dir / "attempts").mkdir(parents=True, exist_ok=True)
            (restore_dir / "scenarios").mkdir(parents=True, exist_ok=True)
            (restore_dir / "leaderboard").mkdir(parents=True, exist_ok=True)
            
            # Copy files to target directory
            if (temp_dir / "players").exists():
                for file in (temp_dir / "players").glob("*.json"):
                    shutil.copy(file, restore_dir / "players" / file.name)
                    
            if (temp_dir / "attempts").exists():
                for file in (temp_dir / "attempts").glob("*.json"):
                    shutil.copy(file, restore_dir / "attempts" / file.name)
                    
            if (temp_dir / "scenarios").exists():
                for file in (temp_dir / "scenarios").glob("*.json"):
                    shutil.copy(file, restore_dir / "scenarios" / file.name)
                    
            if (temp_dir / "leaderboard").exists():
                for file in (temp_dir / "leaderboard").glob("*.json"):
                    shutil.copy(file, restore_dir / "leaderboard" / file.name)
                    
            print(f"Backup restored to: {restore_dir}")
            
            # If restoring to current storage provider directory, reload is needed
            if isinstance(self.storage, LocalStorageProvider) and (
                    not target_dir or Path(target_dir) == Path(self.storage.data_dir)):
                print("Restored to current storage provider directory. Reload required.")
                
            return True
            
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False
            
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    def export_data(self, export_dir: str, format_type: str = "json") -> bool:
        """
        Export all competition data to a directory.
        
        Args:
            export_dir: Directory to export to
            format_type: Export format (json or csv)
            
        Returns:
            Success status
        """
        export_path = Path(export_dir)
        export_path.mkdir(parents=True, exist_ok=True)
        
        try:
            # Create subdirectories
            (export_path / "players").mkdir(parents=True, exist_ok=True)
            (export_path / "attempts").mkdir(parents=True, exist_ok=True)
            (export_path / "scenarios").mkdir(parents=True, exist_ok=True)
            (export_path / "leaderboard").mkdir(parents=True, exist_ok=True)
            
            # Export data
            self._export_players(export_path / "players", format_type)
            self._export_attempts(export_path / "attempts", format_type)
            self._export_scenarios(export_path / "scenarios", format_type)
            self._export_leaderboard(export_path / "leaderboard", format_type)
            
            print(f"Data exported to: {export_path}")
            return True
            
        except Exception as e:
            print(f"Error exporting data: {e}")
            return False
    
    def _export_players(self, export_dir: Path, format_type: str = "json"):
        """Export players to the specified directory."""
        players = self.storage.list_players()
        
        if format_type == "json":
            # Export individual files
            for player in players:
                with open(export_dir / f"{player.id}.json", "w") as f:
                    json.dump(player.to_dict(), f, indent=2)
                    
            # Export combined file
            with open(export_dir / "all_players.json", "w") as f:
                json.dump([p.to_dict() for p in players], f, indent=2)
                
        elif format_type == "csv":
            # Simple CSV export (expand as needed)
            with open(export_dir / "players.csv", "w") as f:
                f.write("id,name,email,created_at\n")
                for player in players:
                    f.write(f"{player.id},{player.name},{player.email},{player.created_at}\n")
    
    def _export_attempts(self, export_dir: Path, format_type: str = "json"):
        """Export attempts to the specified directory."""
        attempts = self.storage.list_attempts()
        
        if format_type == "json":
            # Export individual files
            for attempt in attempts:
                with open(export_dir / f"{attempt.id}.json", "w") as f:
                    json.dump(attempt.to_dict(), f, indent=2)
                    
            # Export combined file
            with open(export_dir / "all_attempts.json", "w") as f:
                json.dump([a.to_dict() for a in attempts], f, indent=2)
                
        elif format_type == "csv":
            # Simple CSV export
            with open(export_dir / "attempts.csv", "w") as f:
                f.write("id,player_id,player_name,scenario_id,timestamp,is_official,score\n")
                for attempt in attempts:
                    score = attempt.results.final_score if attempt.results else "N/A"
                    f.write(f"{attempt.id},{attempt.player_id},{attempt.player_name}," +
                            f"{attempt.scenario_id},{attempt.timestamp},{attempt.is_official},{score}\n")
    
    def _export_scenarios(self, export_dir: Path, format_type: str = "json"):
        """Export scenarios to the specified directory."""
        scenarios = self.storage.list_scenarios()
        
        if format_type == "json":
            # Export individual files
            for scenario in scenarios:
                with open(export_dir / f"{scenario.id}.json", "w") as f:
                    json.dump(scenario.to_dict(), f, indent=2)
                    
            # Export combined file
            with open(export_dir / "all_scenarios.json", "w") as f:
                json.dump([s.to_dict() for s in scenarios], f, indent=2)
                
        elif format_type == "csv":
            # Simple CSV export
            with open(export_dir / "scenarios.csv", "w") as f:
                f.write("id,name,description,r0,difficulty,initial_resources\n")
                for scenario in scenarios:
                    f.write(f"{scenario.id},{scenario.name},{scenario.description}," +
                            f"{scenario.r0},{scenario.difficulty},{scenario.initial_resources}\n")
    
    def _export_leaderboard(self, export_dir: Path, format_type: str = "json"):
        """Export leaderboard to the specified directory."""
        entries = self.storage.get_leaderboard()
        
        if format_type == "json":
            # Export to file
            with open(export_dir / "leaderboard.json", "w") as f:
                json.dump([e.to_dict() for e in entries], f, indent=2)
                
        elif format_type == "csv":
            # Simple CSV export
            with open(export_dir / "leaderboard.csv", "w") as f:
                f.write("rank,player_id,player_name,standard_score,challenging_score,average_score\n")
                for entry in entries:
                    f.write(f"{entry.rank},{entry.player_id},{entry.player_name}," +
                            f"{entry.standard_score},{entry.challenging_score},{entry.average_score}\n")
    
    def import_scenario(self, scenario_file: str) -> Optional[str]:
        """
        Import a scenario from a JSON file.
        
        Args:
            scenario_file: Path to scenario JSON file
            
        Returns:
            Scenario ID if successful, None otherwise
        """
        try:
            with open(scenario_file, "r") as f:
                data = json.load(f)
                
            scenario = Scenario.from_dict(data)
            success = self.storage.save_scenario(scenario)
            
            if success:
                print(f"Scenario '{scenario.name}' imported with ID: {scenario.id}")
                return scenario.id
            else:
                print("Failed to save scenario")
                return None
                
        except Exception as e:
            print(f"Error importing scenario: {e}")
            return None
    
    def create_scenario(self, 
                      id: str,
                      name: str,
                      description: str,
                      r0: float,
                      initial_infections: Dict[str, int],
                      initial_resources: int,
                      difficulty: str,
                      parameters: Dict[str, Any] = None) -> Optional[str]:
        """
        Create a new scenario with the specified parameters.
        
        Args:
            id: Scenario ID
            name: Scenario name
            description: Scenario description
            r0: Basic reproduction number
            initial_infections: Dict mapping locations to infection counts
            initial_resources: Starting resources
            difficulty: Difficulty level
            parameters: Additional parameters
            
        Returns:
            Scenario ID if successful, None otherwise
        """
        try:
            # Generate a seed for reproducibility
            seed = f"{id}_{int(time.time())}"
            
            # Create scenario
            scenario = Scenario(
                id=id,
                name=name,
                description=description,
                seed=seed,
                r0=r0,
                initial_infections=initial_infections,
                initial_resources=initial_resources,
                difficulty=difficulty,
                parameters=parameters or {}
            )
            
            # Save scenario
            success = self.storage.save_scenario(scenario)
            
            if success:
                print(f"Scenario '{name}' created with ID: {id}")
                return id
            else:
                print("Failed to save scenario")
                return None
                
        except Exception as e:
            print(f"Error creating scenario: {e}")
            return None
    
    def delete_scenario(self, scenario_id: str) -> bool:
        """
        Delete a scenario by ID.
        
        Args:
            scenario_id: Scenario ID
            
        Returns:
            Success status
        """
        try:
            # Check if scenario exists
            scenario = self.storage.get_scenario(scenario_id)
            if not scenario:
                print(f"Scenario with ID {scenario_id} not found")
                return False
                
            # If using LocalStorageProvider, directly delete file
            if isinstance(self.storage, LocalStorageProvider):
                file_path = Path(self.storage.data_dir) / "scenarios" / f"{scenario_id}.json"
                if file_path.exists():
                    os.remove(file_path)
                    print(f"Scenario '{scenario.name}' (ID: {scenario_id}) deleted")
                    return True
                else:
                    print(f"Scenario file not found: {file_path}")
                    return False
            else:
                # For other storage providers, would need implementation
                print("Deletion not implemented for this storage provider")
                return False
                
        except Exception as e:
            print(f"Error deleting scenario: {e}")
            return False
    
    def validate_storage_integrity(self) -> Dict[str, Any]:
        """
        Validate the integrity of the storage.
        
        Returns:
            Dict with validation results
        """
        results = {
            "players": {"count": 0, "valid": 0, "invalid": 0, "issues": []},
            "attempts": {"count": 0, "valid": 0, "invalid": 0, "issues": []},
            "scenarios": {"count": 0, "valid": 0, "invalid": 0, "issues": []},
            "leaderboard": {"valid": False, "issues": []}
        }
        
        # Validate players
        try:
            players = self.storage.list_players()
            results["players"]["count"] = len(players)
            
            for player in players:
                try:
                    # Basic validation
                    if not player.id or not player.name:
                        results["players"]["invalid"] += 1
                        results["players"]["issues"].append(f"Player {player.id} has missing required fields")
                    else:
                        results["players"]["valid"] += 1
                except Exception as e:
                    results["players"]["invalid"] += 1
                    results["players"]["issues"].append(f"Error validating player: {e}")
        except Exception as e:
            results["players"]["issues"].append(f"Error listing players: {e}")
            
        # Validate attempts
        try:
            attempts = self.storage.list_attempts()
            results["attempts"]["count"] = len(attempts)
            
            for attempt in attempts:
                try:
                    # Basic validation
                    if not attempt.id or not attempt.player_id or not attempt.scenario_id:
                        results["attempts"]["invalid"] += 1
                        results["attempts"]["issues"].append(f"Attempt {attempt.id} has missing required fields")
                    else:
                        results["attempts"]["valid"] += 1
                        
                    # Check if player exists
                    player = self.storage.get_player(attempt.player_id)
                    if not player and attempt.player_id != "guest":
                        results["attempts"]["issues"].append(
                            f"Attempt {attempt.id} references non-existent player {attempt.player_id}")
                        
                    # Check if scenario exists
                    scenario = self.storage.get_scenario(attempt.scenario_id)
                    if not scenario:
                        results["attempts"]["issues"].append(
                            f"Attempt {attempt.id} references non-existent scenario {attempt.scenario_id}")
                except Exception as e:
                    results["attempts"]["invalid"] += 1
                    results["attempts"]["issues"].append(f"Error validating attempt: {e}")
        except Exception as e:
            results["attempts"]["issues"].append(f"Error listing attempts: {e}")
            
        # Validate scenarios
        try:
            scenarios = self.storage.list_scenarios()
            results["scenarios"]["count"] = len(scenarios)
            
            for scenario in scenarios:
                try:
                    # Basic validation
                    if not scenario.id or not scenario.name:
                        results["scenarios"]["invalid"] += 1
                        results["scenarios"]["issues"].append(f"Scenario {scenario.id} has missing required fields")
                    else:
                        results["scenarios"]["valid"] += 1
                except Exception as e:
                    results["scenarios"]["invalid"] += 1
                    results["scenarios"]["issues"].append(f"Error validating scenario: {e}")
        except Exception as e:
            results["scenarios"]["issues"].append(f"Error listing scenarios: {e}")
            
        # Validate leaderboard
        try:
            entries = self.storage.get_leaderboard()
            
            # Check if entries are properly ranked
            if entries:
                for i, entry in enumerate(entries):
                    if entry.rank != i + 1:
                        results["leaderboard"]["issues"].append(
                            f"Leaderboard entry for {entry.player_name} has incorrect rank: {entry.rank} != {i+1}")
                        
                # Check if all players in leaderboard exist
                for entry in entries:
                    player = self.storage.get_player(entry.player_id)
                    if not player:
                        results["leaderboard"]["issues"].append(
                            f"Leaderboard entry references non-existent player {entry.player_id}")
                
            if not results["leaderboard"]["issues"]:
                results["leaderboard"]["valid"] = True
        except Exception as e:
            results["leaderboard"]["issues"].append(f"Error validating leaderboard: {e}")
            
        return results


def create_advanced_scenarios(data_manager: DataManager) -> List[str]:
    """
    Create a set of advanced scenarios beyond the standard ones.
    
    Args:
        data_manager: DataManager instance
        
    Returns:
        List of created scenario IDs
    """
    created_scenarios = []
    
    # Expert scenario - high R0 and multiple initial outbreaks
    expert_id = data_manager.create_scenario(
        id="expert",
        name="Expert Challenge",
        description="An extremely difficult scenario with a highly contagious disease, multiple outbreak sites, and limited resources.",
        r0=4.0,
        initial_infections={
            "capital": 75,
            "major_city_1": 50,
            "major_city_2": 50,
            "rural_area_1": 25
        },
        initial_resources=600,
        difficulty="expert",
        parameters={
            "disease_mortality": 0.04,
            "treatment_effectiveness": 0.5,
            "vaccine_development_time": 180,
            "economic_impact_factor": 1.5,
            "healthcare_capacity_factor": 0.7
        }
    )
    if expert_id:
        created_scenarios.append(expert_id)
    
    # Balanced scenario - moderate difficulty focusing on balance
    balanced_id = data_manager.create_scenario(
        id="balanced",
        name="Balanced Challenge",
        description="A moderately difficult scenario that tests your ability to balance health and economic outcomes.",
        r0=3.0,
        initial_infections={
            "capital": 80,
            "major_city_1": 40
        },
        initial_resources=800,
        difficulty="intermediate",
        parameters={
            "disease_mortality": 0.025,
            "treatment_effectiveness": 0.65,
            "vaccine_development_time": 150,
            "economic_impact_factor": 1.3,
            "healthcare_capacity_factor": 0.85,
            "economic_resilience": 0.7
        }
    )
    if balanced_id:
        created_scenarios.append(balanced_id)
    
    # Economic scenario - focuses on economic challenges
    economic_id = data_manager.create_scenario(
        id="economic",
        name="Economic Crisis",
        description="A scenario where the disease has a severe economic impact, testing your ability to preserve the economy.",
        r0=2.8,
        initial_infections={
            "capital": 100,
            "financial_district": 50
        },
        initial_resources=850,
        difficulty="specialized",
        parameters={
            "disease_mortality": 0.02,
            "treatment_effectiveness": 0.7,
            "vaccine_development_time": 140,
            "economic_impact_factor": 2.0,
            "healthcare_capacity_factor": 0.9,
            "economic_resilience": 0.5,
            "global_trade_impact": 0.7
        }
    )
    if economic_id:
        created_scenarios.append(economic_id)
    
    # Resource-limited scenario - focuses on efficient resource use
    limited_id = data_manager.create_scenario(
        id="resource_limited",
        name="Resource Scarcity",
        description="A scenario with very limited resources, testing your efficiency and prioritization.",
        r0=3.2,
        initial_infections={
            "capital": 60,
            "major_city_1": 30
        },
        initial_resources=400,
        difficulty="specialized",
        parameters={
            "disease_mortality": 0.03,
            "treatment_effectiveness": 0.6,
            "vaccine_development_time": 160,
            "economic_impact_factor": 1.2,
            "healthcare_capacity_factor": 0.6,
            "resource_replenishment_rate": 0.5
        }
    )
    if limited_id:
        created_scenarios.append(limited_id)
        
    return created_scenarios 