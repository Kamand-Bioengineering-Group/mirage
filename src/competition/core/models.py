"""
Core domain models for the competition system.
These models represent the business entities and are platform-agnostic.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid


@dataclass
class SimulationResults:
    """Results from a single simulation run."""
    player_id: str
    scenario_id: str
    total_steps: int
    population_survived: float  # 0-1 score
    gdp_preserved: float  # 0-1 score
    infection_control: float  # 0-1 score
    resource_efficiency: float  # 0-1 score
    time_to_containment: float  # 0-1 score
    final_score: float  # Weighted combination
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "player_id": self.player_id,
            "scenario_id": self.scenario_id,
            "total_steps": self.total_steps,
            "population_survived": self.population_survived,
            "gdp_preserved": self.gdp_preserved,
            "infection_control": self.infection_control,
            "resource_efficiency": self.resource_efficiency,
            "time_to_containment": self.time_to_containment,
            "final_score": self.final_score,
            "metadata": self.metadata,
            "raw_metrics": self.raw_metrics
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SimulationResults':
        """Create from dictionary representation."""
        return cls(
            player_id=data["player_id"],
            scenario_id=data["scenario_id"],
            total_steps=data["total_steps"],
            population_survived=data["population_survived"],
            gdp_preserved=data["gdp_preserved"],
            infection_control=data["infection_control"],
            resource_efficiency=data["resource_efficiency"],
            time_to_containment=data["time_to_containment"],
            final_score=data["final_score"],
            metadata=data.get("metadata", {}),
            raw_metrics=data.get("raw_metrics", {})
        )


@dataclass
class PlayerAttempt:
    """Represents a single competition attempt by a player."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    player_id: str = ""
    player_name: str = ""
    scenario_id: str = ""
    results: Optional[SimulationResults] = None
    timestamp: datetime = field(default_factory=datetime.now)
    is_official: bool = False  # Whether it's a practice run or official attempt
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "player_id": self.player_id,
            "player_name": self.player_name,
            "scenario_id": self.scenario_id,
            "results": self.results.to_dict() if self.results else None,
            "timestamp": self.timestamp.isoformat(),
            "is_official": self.is_official
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlayerAttempt':
        """Create from dictionary representation."""
        attempt = cls(
            id=data["id"],
            player_id=data["player_id"],
            player_name=data["player_name"],
            scenario_id=data["scenario_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            is_official=data["is_official"]
        )
        
        if data.get("results"):
            attempt.results = SimulationResults.from_dict(data["results"])
            
        return attempt


@dataclass
class Player:
    """Represents a player in the competition."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    email: str = ""
    strategy_document: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "strategy_document": self.strategy_document,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        """Create from dictionary representation."""
        return cls(
            id=data["id"],
            name=data["name"],
            email=data["email"],
            strategy_document=data.get("strategy_document", ""),
            created_at=datetime.fromisoformat(data["created_at"])
        )


@dataclass
class Scenario:
    """Represents a competition scenario configuration."""
    id: str  # 'standard' or 'challenging'
    name: str
    description: str
    seed: str  # For reproducibility
    r0: float
    initial_infections: Dict[str, int]  # Location -> count
    initial_resources: int
    difficulty: str  # 'standard' or 'challenging'
    parameters: Dict[str, Any] = field(default_factory=dict)  # Other simulation parameters
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "seed": self.seed,
            "r0": self.r0,
            "initial_infections": self.initial_infections,
            "initial_resources": self.initial_resources,
            "difficulty": self.difficulty,
            "parameters": self.parameters
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Scenario':
        """Create from dictionary representation."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            seed=data["seed"],
            r0=data["r0"],
            initial_infections=data["initial_infections"],
            initial_resources=data["initial_resources"],
            difficulty=data["difficulty"],
            parameters=data.get("parameters", {})
        )


@dataclass
class LeaderboardEntry:
    """Entry in the competition leaderboard."""
    rank: int
    player_id: str
    player_name: str
    standard_score: float
    challenging_score: float
    average_score: float
    timestamps: Dict[str, str]  # scenario_id -> timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "rank": self.rank,
            "player_id": self.player_id,
            "player_name": self.player_name,
            "standard_score": self.standard_score,
            "challenging_score": self.challenging_score,
            "average_score": self.average_score,
            "timestamps": self.timestamps
        } 