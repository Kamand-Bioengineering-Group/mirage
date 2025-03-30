"""
Competition API for the XPECTO Epidemic 2.0 simulation.

This module provides the main entry point for interacting with the competition
system. It handles player registration, result tracking, and integrates with
the epidemic simulation engine.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid

from .models import Player, Scenario, Result, Attempt
from .testing.engine_adapter import MockEngine

class CompetitionAPI:
    """
    Main API for the competition system.
    
    This class provides methods for registering players, creating scenarios,
    and recording competition attempts and results.
    """
    
    def __init__(self, 
                 storage_dir: str = "./competition_data",
                 use_mock_engine: bool = True):
        """
        Initialize the competition API.
        
        Parameters:
        -----------
        storage_dir : str
            Directory where competition data will be stored
        use_mock_engine : bool
            Whether to use the mock engine (default) or the real engine
        """
        self.storage_dir = storage_dir
        self.use_mock_engine = use_mock_engine
        self.players: Dict[str, Player] = {}
        self.scenarios: Dict[str, Scenario] = {}
        self.attempts: Dict[str, Attempt] = {}
        
        # Create storage directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)
        os.makedirs(os.path.join(storage_dir, "players"), exist_ok=True)
        os.makedirs(os.path.join(storage_dir, "scenarios"), exist_ok=True)
        os.makedirs(os.path.join(storage_dir, "attempts"), exist_ok=True)
        os.makedirs(os.path.join(storage_dir, "results"), exist_ok=True)
    
    def register_player(self, name: str, email: str) -> Player:
        """
        Register a new player in the competition.
        
        Parameters:
        -----------
        name : str
            Player's name
        email : str
            Player's email address
            
        Returns:
        --------
        Player
            The newly registered player
        """
        player_id = str(uuid.uuid4())
        player = Player(
            id=player_id,
            name=name,
            email=email
        )
        self.players[player_id] = player
        
        # Save player data
        self._save_player(player)
        
        return player
    
    def create_scenario(self, 
                       name: str,
                       description: str,
                       seed: int,
                       r0: float,
                       initial_infections: int,
                       initial_resources: int,
                       difficulty: str = "standard") -> Scenario:
        """
        Create a new competition scenario.
        
        Parameters:
        -----------
        name : str
            Scenario name
        description : str
            Description of the scenario
        seed : int
            Random seed for reproducibility
        r0 : float
            Base reproduction number for the disease
        initial_infections : int
            Number of initially infected people
        initial_resources : int
            Initial resources available
        difficulty : str
            Difficulty level ("standard", "challenging", "expert")
            
        Returns:
        --------
        Scenario
            The newly created scenario
        """
        scenario_id = str(uuid.uuid4())
        scenario = Scenario(
            id=scenario_id,
            name=name,
            description=description,
            seed=seed,
            r0=r0,
            initial_infections=initial_infections,
            initial_resources=initial_resources,
            difficulty=difficulty
        )
        self.scenarios[scenario_id] = scenario
        
        # Save scenario data
        self._save_scenario(scenario)
        
        return scenario
    
    def submit_attempt(self, 
                      player_id: str,
                      scenario_id: str,
                      engine_state: Dict[str, Any],
                      is_practice: bool = False) -> Attempt:
        """
        Submit a competition attempt.
        
        Parameters:
        -----------
        player_id : str
            ID of the player making the attempt
        scenario_id : str
            ID of the scenario being attempted
        engine_state : Dict[str, Any]
            Final state of the engine after the simulation
        is_practice : bool
            Whether this is a practice attempt
            
        Returns:
        --------
        Attempt
            The recorded attempt
        """
        if player_id not in self.players:
            raise ValueError(f"Player with ID {player_id} not found")
        if scenario_id not in self.scenarios:
            raise ValueError(f"Scenario with ID {scenario_id} not found")
        
        # Calculate results
        result = self._calculate_results(engine_state)
        
        # Create attempt
        attempt_id = str(uuid.uuid4())
        attempt = Attempt(
            id=attempt_id,
            player_id=player_id,
            scenario_id=scenario_id,
            is_practice=is_practice,
            result=result
        )
        
        # Add attempt to player's attempts
        self.attempts[attempt_id] = attempt
        self.players[player_id].attempts.append(attempt)
        
        # Save attempt data
        self._save_attempt(attempt)
        
        return attempt
    
    def get_player(self, player_id: str) -> Optional[Player]:
        """Get a player by ID."""
        return self.players.get(player_id)
    
    def get_scenario(self, scenario_id: str) -> Optional[Scenario]:
        """Get a scenario by ID."""
        return self.scenarios.get(scenario_id)
    
    def get_attempt(self, attempt_id: str) -> Optional[Attempt]:
        """Get an attempt by ID."""
        return self.attempts.get(attempt_id)
    
    def get_leaderboard(self, scenario_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get the current leaderboard.
        
        Parameters:
        -----------
        scenario_id : Optional[str]
            If provided, only include attempts for this scenario
            
        Returns:
        --------
        List[Dict[str, Any]]
            List of player results, sorted by score
        """
        leaderboard = []
        
        for attempt_id, attempt in self.attempts.items():
            if scenario_id and attempt.scenario_id != scenario_id:
                continue
            if attempt.is_practice:
                continue
            
            player = self.players.get(attempt.player_id)
            scenario = self.scenarios.get(attempt.scenario_id)
            
            if not player or not scenario or not attempt.result:
                continue
                
            leaderboard.append({
                "player_name": player.name,
                "player_id": player.id,
                "scenario_name": scenario.name,
                "scenario_id": scenario.id,
                "attempt_id": attempt.id,
                "timestamp": attempt.timestamp.isoformat(),
                "score": attempt.result.final_score,
                "population_survived": attempt.result.population_survived,
                "gdp_preserved": attempt.result.gdp_preserved,
                "infection_control": attempt.result.infection_control,
                "resource_efficiency": attempt.result.resource_efficiency,
                "time_to_containment": attempt.result.time_to_containment,
            })
        
        # Sort by score, descending
        leaderboard.sort(key=lambda x: x["score"], reverse=True)
        
        return leaderboard
    
    def create_engine(self, scenario_id: Optional[str] = None) -> MockEngine:
        """
        Create a simulation engine based on a scenario.
        
        Parameters:
        -----------
        scenario_id : Optional[str]
            ID of the scenario to use. If None, creates a default engine.
            
        Returns:
        --------
        MockEngine
            A properly initialized engine
        """
        # For now, always return a mock engine
        # TODO: Support real engine when ready
        engine = MockEngine()
        
        # Configure engine based on scenario if provided
        if scenario_id and scenario_id in self.scenarios:
            scenario = self.scenarios[scenario_id]
            
            # Set basic parameters
            engine.disease_params["r0_base"] = scenario.r0
            engine.metrics["population"]["infected"] = scenario.initial_infections
            engine.metrics["resources"]["available"] = scenario.initial_resources
            engine.metrics["resources"]["total_initial"] = scenario.initial_resources
            
            # Update difficulty settings
            if scenario.difficulty == "challenging":
                engine.disease_params["mortality_rate_base"] = 0.03
            elif scenario.difficulty == "expert":
                engine.disease_params["mortality_rate_base"] = 0.04
                engine.metrics["healthcare"]["capacity"] = 300  # Reduced capacity
            
            # Update state
            engine._update_state()
        
        return engine
    
    def _calculate_results(self, engine_state: Dict[str, Any]) -> Result:
        """
        Calculate competition results from engine state.
        
        Parameters:
        -----------
        engine_state : Dict[str, Any]
            Final state of the engine after simulation
            
        Returns:
        --------
        Result
            Calculated results
        """
        # Extract metrics from engine state
        metrics = engine_state.get("metrics", {})
        
        # Population metrics
        population = metrics.get("population", {})
        total_population = population.get("total", 10000)
        dead_population = population.get("dead", 0)
        population_survived = (total_population - dead_population) / total_population
        
        # Economic metrics
        economy = metrics.get("economy", {})
        initial_gdp = economy.get("initial_gdp", 1000)
        final_gdp = economy.get("current_gdp", 0)
        gdp_preserved = final_gdp / initial_gdp if initial_gdp > 0 else 0
        
        # Infection control
        max_infection_rate = metrics.get("max_infection_rate", 1.0)
        infection_control = 1.0 - max_infection_rate
        
        # Resource efficiency
        resources = metrics.get("resources", {})
        total_resources = resources.get("total_initial", 5000)
        spent_resources = resources.get("total_spent", 0)
        resource_efficiency = 1.0 - (spent_resources / total_resources) if total_resources > 0 else 0
        
        # Time to containment
        containment_achieved = metrics.get("containment_achieved", False)
        containment_step = metrics.get("containment_step", -1)
        time_to_containment = 0.0
        
        if containment_achieved and containment_step >= 0:
            # Normalize to 0-1 scale, assuming 200 steps max
            time_to_containment = 1.0 - (containment_step / 200)
        
        # Calculate final score (weighted average)
        final_score = (
            0.3 * population_survived +
            0.2 * gdp_preserved +
            0.2 * infection_control +
            0.15 * resource_efficiency +
            0.15 * time_to_containment
        )
        
        # Create result object
        result = Result(
            population_survived=population_survived,
            gdp_preserved=gdp_preserved,
            infection_control=infection_control,
            resource_efficiency=resource_efficiency,
            time_to_containment=time_to_containment,
            final_score=final_score,
            metadata={"raw_metrics": metrics}
        )
        
        return result
    
    def _save_player(self, player: Player) -> None:
        """Save player data to storage."""
        player_data = {
            "id": player.id,
            "name": player.name,
            "email": player.email,
            "registered_date": player.registered_date.isoformat(),
        }
        
        file_path = os.path.join(self.storage_dir, "players", f"{player.id}.json")
        with open(file_path, "w") as f:
            json.dump(player_data, f, indent=2)
    
    def _save_scenario(self, scenario: Scenario) -> None:
        """Save scenario data to storage."""
        scenario_data = {
            "id": scenario.id,
            "name": scenario.name,
            "description": scenario.description,
            "seed": scenario.seed,
            "r0": scenario.r0,
            "initial_infections": scenario.initial_infections,
            "initial_resources": scenario.initial_resources,
            "difficulty": scenario.difficulty,
        }
        
        file_path = os.path.join(self.storage_dir, "scenarios", f"{scenario.id}.json")
        with open(file_path, "w") as f:
            json.dump(scenario_data, f, indent=2)
    
    def _save_attempt(self, attempt: Attempt) -> None:
        """Save attempt data to storage."""
        if not attempt.result:
            return
            
        attempt_data = {
            "id": attempt.id,
            "player_id": attempt.player_id,
            "scenario_id": attempt.scenario_id,
            "timestamp": attempt.timestamp.isoformat(),
            "is_practice": attempt.is_practice,
            "result": {
                "population_survived": attempt.result.population_survived,
                "gdp_preserved": attempt.result.gdp_preserved,
                "infection_control": attempt.result.infection_control,
                "resource_efficiency": attempt.result.resource_efficiency,
                "time_to_containment": attempt.result.time_to_containment,
                "final_score": attempt.result.final_score,
            }
        }
        
        file_path = os.path.join(self.storage_dir, "attempts", f"{attempt.id}.json")
        with open(file_path, "w") as f:
            json.dump(attempt_data, f, indent=2) 