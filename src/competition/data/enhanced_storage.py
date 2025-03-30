"""
Enhanced storage providers with error recovery and validation.
This module extends the base storage providers with additional reliability features.
"""
import os
import json
import time
import shutil
import tempfile
import logging
import fcntl
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Type, TypeVar, cast
import threading
import uuid

from ..core.models import Player, PlayerAttempt, Scenario, SimulationResults, LeaderboardEntry
from .storage import StorageProvider, LocalStorageProvider

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('competition.storage')

# Generic type for models
T = TypeVar('T', Player, PlayerAttempt, Scenario, LeaderboardEntry)


class EnhancedLocalStorageProvider(LocalStorageProvider):
    """
    Enhanced local storage provider with error recovery and validation.
    
    Features:
    1. Transaction-like file operations
    2. Automatic backups
    3. Data validation
    4. File locking for concurrency
    5. Retry mechanism
    """
    
    def __init__(self, data_dir: str = "data", backup_interval: int = 24):
        """
        Initialize provider with enhanced features.
        
        Args:
            data_dir: Directory for data storage
            backup_interval: Hours between automatic backups
        """
        super().__init__(data_dir)
        self.locks = {}  # File locks registry
        self.last_backup = datetime.now()
        self.backup_interval = backup_interval  # hours
        self._ensure_backup_directory()
        self._check_backup_schedule()
        
    def _ensure_backup_directory(self):
        """Ensure backup directory exists."""
        (Path(self.data_dir) / "backups").mkdir(parents=True, exist_ok=True)
    
    def _check_backup_schedule(self):
        """Check if it's time for a scheduled backup."""
        now = datetime.now()
        hours_since_backup = (now - self.last_backup).total_seconds() / 3600
        
        if hours_since_backup >= self.backup_interval:
            try:
                self._create_backup()
                self.last_backup = now
            except Exception as e:
                logger.error(f"Scheduled backup failed: {e}")
    
    def _create_backup(self):
        """Create a backup of all data files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path(self.data_dir) / "backups" / f"backup_{timestamp}"
        
        try:
            # Create backup directories
            backup_dir.mkdir(parents=True, exist_ok=True)
            (backup_dir / "players").mkdir(parents=True, exist_ok=True)
            (backup_dir / "attempts").mkdir(parents=True, exist_ok=True)
            (backup_dir / "scenarios").mkdir(parents=True, exist_ok=True)
            (backup_dir / "leaderboard").mkdir(parents=True, exist_ok=True)
            
            # Copy files
            self._backup_directory("players", backup_dir)
            self._backup_directory("attempts", backup_dir)
            self._backup_directory("scenarios", backup_dir)
            self._backup_directory("leaderboard", backup_dir)
            
            logger.info(f"Created backup at {backup_dir}")
            return str(backup_dir)
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            if backup_dir.exists():
                shutil.rmtree(backup_dir, ignore_errors=True)
            raise
    
    def _backup_directory(self, subdir: str, backup_dir: Path):
        """Backup a specific subdirectory."""
        source_dir = Path(self.data_dir) / subdir
        target_dir = backup_dir / subdir
        
        if source_dir.exists():
            for file in source_dir.glob("*.json"):
                shutil.copy2(file, target_dir / file.name)
    
    def _acquire_lock(self, file_path: Path):
        """
        Acquire a lock on a file for concurrent access.
        
        Args:
            file_path: Path to the file to lock
        """
        if str(file_path) not in self.locks:
            self.locks[str(file_path)] = threading.Lock()
            
        lock = self.locks[str(file_path)]
        lock.acquire()
        
        # Also use file system lock for multi-process safety
        try:
            # Make parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create file if it doesn't exist
            if not file_path.exists():
                with open(file_path, 'w') as f:
                    f.write('{}')
                    
            # Open file for locking
            file_handle = open(file_path, 'r+')
            fcntl.flock(file_handle, fcntl.LOCK_EX)
            return file_handle
        except Exception as e:
            # Release the threading lock if file locking fails
            lock.release()
            logger.error(f"Failed to acquire lock on {file_path}: {e}")
            raise
    
    def _release_lock(self, file_path: Path, file_handle):
        """
        Release a previously acquired lock.
        
        Args:
            file_path: Path to the locked file
            file_handle: Open file handle with lock
        """
        try:
            # Release file system lock
            fcntl.flock(file_handle, fcntl.LOCK_UN)
            file_handle.close()
        except Exception as e:
            logger.error(f"Error releasing file lock: {e}")
        finally:
            # Release threading lock
            if str(file_path) in self.locks:
                self.locks[str(file_path)].release()
    
    def _atomic_write(self, file_path: Path, data: Dict[str, Any]) -> bool:
        """
        Write data atomically to ensure consistency.
        
        Args:
            file_path: Target file path
            data: Data to write
            
        Returns:
            Success status
        """
        # Create parent directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create a temporary file in the same directory
        temp_file = file_path.parent / f".tmp_{uuid.uuid4().hex}_{file_path.name}"
        
        try:
            # Write to temp file
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            # Ensure data is flushed to disk
            os.fsync(f.fileno())
            
            # Rename temp file to target (atomic operation on most file systems)
            temp_file.rename(file_path)
            return True
        except Exception as e:
            logger.error(f"Error during atomic write to {file_path}: {e}")
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except:
                    pass
            return False
    
    def _validate_model(self, model: Any, expected_type: Type[T]) -> bool:
        """
        Validate model type and required fields.
        
        Args:
            model: Model instance to validate
            expected_type: Expected model type
            
        Returns:
            Validation result
        """
        if not isinstance(model, expected_type):
            logger.error(f"Invalid model type: expected {expected_type.__name__}, got {type(model).__name__}")
            return False
            
        # Check required fields based on model type
        if expected_type == Player:
            player = cast(Player, model)
            if not player.id or not player.name:
                logger.error(f"Invalid Player: missing required fields")
                return False
                
        elif expected_type == PlayerAttempt:
            attempt = cast(PlayerAttempt, model)
            if not attempt.id or not attempt.player_id or not attempt.scenario_id:
                logger.error(f"Invalid PlayerAttempt: missing required fields")
                return False
                
        elif expected_type == Scenario:
            scenario = cast(Scenario, model)
            if not scenario.id or not scenario.name or not scenario.seed:
                logger.error(f"Invalid Scenario: missing required fields")
                return False
                
        return True
    
    def _with_retry(self, operation, *args, max_retries=3, **kwargs):
        """
        Execute an operation with retries.
        
        Args:
            operation: Function to execute
            max_retries: Maximum retry attempts
            *args, **kwargs: Arguments for the operation
            
        Returns:
            Result of the operation
        """
        retries = 0
        last_error = None
        
        while retries < max_retries:
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                last_error = e
                retries += 1
                wait_time = 0.1 * (2 ** retries)  # Exponential backoff
                logger.warning(f"Operation failed, retrying in {wait_time:.2f}s ({retries}/{max_retries}): {e}")
                time.sleep(wait_time)
                
        logger.error(f"Operation failed after {max_retries} retries: {last_error}")
        raise last_error
    
    # Override storage methods with enhanced versions
    
    def save_player(self, player: Player) -> bool:
        """Save player with validation and atomic write."""
        if not self._validate_model(player, Player):
            return False
            
        file_path = Path(self.data_dir) / "players" / f"{player.id}.json"
        file_handle = None
        
        try:
            file_handle = self._acquire_lock(file_path)
            result = self._atomic_write(file_path, player.to_dict())
            self._check_backup_schedule()
            return result
        except Exception as e:
            logger.error(f"Error saving player: {e}")
            return False
        finally:
            if file_handle:
                self._release_lock(file_path, file_handle)
    
    def get_player(self, player_id: str) -> Optional[Player]:
        """Get player with error recovery."""
        file_path = Path(self.data_dir) / "players" / f"{player_id}.json"
        
        if not file_path.exists():
            return None
            
        file_handle = None
        
        try:
            file_handle = self._acquire_lock(file_path)
            
            # Check if backup is needed
            return self._with_retry(self._read_player, file_path)
        except Exception as e:
            logger.error(f"Error getting player: {e}")
            return None
        finally:
            if file_handle:
                self._release_lock(file_path, file_handle)
    
    def _read_player(self, file_path: Path) -> Optional[Player]:
        """Read player from file with error handling."""
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                player = Player.from_dict(data)
                
                # Validate after loading
                if not self._validate_model(player, Player):
                    logger.warning(f"Loaded player with invalid data: {file_path}")
                    
                return player
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {file_path}: {e}")
            self._recover_file(file_path)
            raise
        except Exception as e:
            logger.error(f"Error reading player file {file_path}: {e}")
            raise
    
    def _recover_file(self, file_path: Path) -> bool:
        """
        Attempt to recover a corrupted file from backups.
        
        Args:
            file_path: Path to corrupted file
            
        Returns:
            Recovery success status
        """
        logger.info(f"Attempting to recover file: {file_path}")
        
        # Check for backups
        backup_dir = Path(self.data_dir) / "backups"
        if not backup_dir.exists():
            logger.warning("No backup directory found")
            return False
            
        # Get all backup directories, sorted by newest first
        backup_dirs = sorted(
            [d for d in backup_dir.glob("backup_*") if d.is_dir()],
            key=lambda d: d.name,
            reverse=True
        )
        
        if not backup_dirs:
            logger.warning("No backup directories found")
            return False
            
        # Try to find the file in backups
        relative_path = file_path.relative_to(Path(self.data_dir))
        
        for backup in backup_dirs:
            backup_file = backup / relative_path
            if backup_file.exists():
                try:
                    # Copy the backup file to the original location
                    shutil.copy2(backup_file, file_path)
                    logger.info(f"Successfully recovered {file_path} from {backup}")
                    return True
                except Exception as e:
                    logger.error(f"Failed to copy backup file: {e}")
        
        logger.warning(f"No valid backup found for {file_path}")
        return False
    
    def save_attempt(self, attempt: PlayerAttempt) -> bool:
        """Save attempt with validation and atomic write."""
        if not self._validate_model(attempt, PlayerAttempt):
            return False
            
        file_path = Path(self.data_dir) / "attempts" / f"{attempt.id}.json"
        file_handle = None
        
        try:
            file_handle = self._acquire_lock(file_path)
            result = self._atomic_write(file_path, attempt.to_dict())
            self._check_backup_schedule()
            return result
        except Exception as e:
            logger.error(f"Error saving attempt: {e}")
            return False
        finally:
            if file_handle:
                self._release_lock(file_path, file_handle)
    
    def get_attempt(self, attempt_id: str) -> Optional[PlayerAttempt]:
        """Get attempt with error recovery."""
        file_path = Path(self.data_dir) / "attempts" / f"{attempt_id}.json"
        
        if not file_path.exists():
            return None
            
        file_handle = None
        
        try:
            file_handle = self._acquire_lock(file_path)
            return self._with_retry(self._read_attempt, file_path)
        except Exception as e:
            logger.error(f"Error getting attempt: {e}")
            return None
        finally:
            if file_handle:
                self._release_lock(file_path, file_handle)
    
    def _read_attempt(self, file_path: Path) -> Optional[PlayerAttempt]:
        """Read attempt from file with error handling."""
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                attempt = PlayerAttempt.from_dict(data)
                
                # Validate after loading
                if not self._validate_model(attempt, PlayerAttempt):
                    logger.warning(f"Loaded attempt with invalid data: {file_path}")
                    
                return attempt
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {file_path}: {e}")
            self._recover_file(file_path)
            raise
        except Exception as e:
            logger.error(f"Error reading attempt file {file_path}: {e}")
            raise
    
    def save_scenario(self, scenario: Scenario) -> bool:
        """Save scenario with validation and atomic write."""
        if not self._validate_model(scenario, Scenario):
            return False
            
        file_path = Path(self.data_dir) / "scenarios" / f"{scenario.id}.json"
        file_handle = None
        
        try:
            file_handle = self._acquire_lock(file_path)
            result = self._atomic_write(file_path, scenario.to_dict())
            self._check_backup_schedule()
            return result
        except Exception as e:
            logger.error(f"Error saving scenario: {e}")
            return False
        finally:
            if file_handle:
                self._release_lock(file_path, file_handle)
    
    def get_scenario(self, scenario_id: str) -> Optional[Scenario]:
        """Get scenario with error recovery."""
        file_path = Path(self.data_dir) / "scenarios" / f"{scenario_id}.json"
        
        if not file_path.exists():
            return None
            
        file_handle = None
        
        try:
            file_handle = self._acquire_lock(file_path)
            return self._with_retry(self._read_scenario, file_path)
        except Exception as e:
            logger.error(f"Error getting scenario: {e}")
            return None
        finally:
            if file_handle:
                self._release_lock(file_path, file_handle)
    
    def _read_scenario(self, file_path: Path) -> Optional[Scenario]:
        """Read scenario from file with error handling."""
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                scenario = Scenario.from_dict(data)
                
                # Validate after loading
                if not self._validate_model(scenario, Scenario):
                    logger.warning(f"Loaded scenario with invalid data: {file_path}")
                    
                return scenario
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {file_path}: {e}")
            self._recover_file(file_path)
            raise
        except Exception as e:
            logger.error(f"Error reading scenario file {file_path}: {e}")
            raise
    
    def save_leaderboard(self, entries: List[LeaderboardEntry]) -> bool:
        """Save leaderboard with atomic write."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Convert entries to dictionaries
        entries_data = [entry.to_dict() for entry in entries]
        
        # Save timestamped version for history
        history_path = Path(self.data_dir) / "leaderboard" / f"leaderboard_{timestamp}.json"
        current_path = Path(self.data_dir) / "leaderboard" / "current_leaderboard.json"
        
        history_handle = None
        current_handle = None
        
        try:
            # Save history version
            history_handle = self._acquire_lock(history_path)
            history_result = self._atomic_write(history_path, entries_data)
            
            # Save current version
            current_handle = self._acquire_lock(current_path)
            current_result = self._atomic_write(current_path, entries_data)
            
            self._check_backup_schedule()
            return history_result and current_result
            
        except Exception as e:
            logger.error(f"Error saving leaderboard: {e}")
            return False
            
        finally:
            if history_handle:
                self._release_lock(history_path, history_handle)
            if current_handle:
                self._release_lock(current_path, current_handle)
    
    def get_leaderboard(self) -> List[LeaderboardEntry]:
        """Get leaderboard with error recovery."""
        file_path = Path(self.data_dir) / "leaderboard" / "current_leaderboard.json"
        
        if not file_path.exists():
            return []
            
        file_handle = None
        
        try:
            file_handle = self._acquire_lock(file_path)
            return self._with_retry(self._read_leaderboard, file_path)
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []
        finally:
            if file_handle:
                self._release_lock(file_path, file_handle)
    
    def _read_leaderboard(self, file_path: Path) -> List[LeaderboardEntry]:
        """Read leaderboard from file with error handling."""
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                entries = []
                
                for entry_data in data:
                    try:
                        entry = LeaderboardEntry(**entry_data)
                        entries.append(entry)
                    except Exception as e:
                        logger.error(f"Error parsing leaderboard entry: {e}")
                        
                return entries
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {file_path}: {e}")
            self._recover_file(file_path)
            raise
        except Exception as e:
            logger.error(f"Error reading leaderboard file {file_path}: {e}")
            raise
    
    def list_players(self) -> List[Player]:
        """List players with error recovery."""
        players_dir = Path(self.data_dir) / "players"
        
        if not players_dir.exists():
            return []
            
        players = []
        
        for file_path in players_dir.glob("*.json"):
            try:
                player = self.get_player(file_path.stem)
                if player:
                    players.append(player)
            except Exception as e:
                logger.error(f"Error loading player {file_path}: {e}")
                
        return players
    
    def list_attempts(self, player_id: Optional[str] = None,
                     scenario_id: Optional[str] = None,
                     is_official: Optional[bool] = None) -> List[PlayerAttempt]:
        """List attempts with error recovery and filtering."""
        attempts_dir = Path(self.data_dir) / "attempts"
        
        if not attempts_dir.exists():
            return []
            
        attempts = []
        
        for file_path in attempts_dir.glob("*.json"):
            try:
                attempt = self.get_attempt(file_path.stem)
                
                if not attempt:
                    continue
                    
                # Apply filters
                if player_id and attempt.player_id != player_id:
                    continue
                if scenario_id and attempt.scenario_id != scenario_id:
                    continue
                if is_official is not None and attempt.is_official != is_official:
                    continue
                    
                attempts.append(attempt)
            except Exception as e:
                logger.error(f"Error loading attempt {file_path}: {e}")
                
        return attempts
    
    def list_scenarios(self) -> List[Scenario]:
        """List scenarios with error recovery."""
        scenarios_dir = Path(self.data_dir) / "scenarios"
        
        if not scenarios_dir.exists():
            return []
            
        scenarios = []
        
        for file_path in scenarios_dir.glob("*.json"):
            try:
                scenario = self.get_scenario(file_path.stem)
                if scenario:
                    scenarios.append(scenario)
            except Exception as e:
                logger.error(f"Error loading scenario {file_path}: {e}")
                
        return scenarios 