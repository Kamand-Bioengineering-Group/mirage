"""
Core data models for the XPECTO Epidemic 2.0 competition system.

This module defines the basic data structures used throughout the competition
system, including Player, Scenario, Result, and Attempt classes.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional

@dataclass
class Player:
    """Represents a competition participant."""
    id: str
    name: str
    email: str
    registered_date: datetime = field(default_factory=datetime.now)
    attempts: List[Any] = field(default_factory=list)

@dataclass
class Scenario:
    """Represents a competition scenario."""
    id: str
    name: str
    description: str
    seed: int
    r0: float
    initial_infections: int
    initial_resources: int
    difficulty: str = "standard"

@dataclass
class Result:
    """Stores simulation results."""
    population_survived: float
    gdp_preserved: float
    infection_control: float
    resource_efficiency: float
    time_to_containment: float
    final_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Attempt:
    """Represents a player's attempt at a scenario."""
    id: str
    player_id: str
    scenario_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    is_practice: bool = False
    result: Optional[Result] = None 