"""
Competition service for handling business logic.
This service coordinates operations between data storage and application.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import math

from ..core.models import Player, PlayerAttempt, Scenario, SimulationResults, LeaderboardEntry
from ..data.storage import StorageProvider


class CompetitionService:
    """Handles competition business logic."""
    
    def __init__(self, storage_provider: StorageProvider):
        """Initialize with a storage provider."""
        self.storage = storage_provider
        self._initialize_scenarios()
    
    def _initialize_scenarios(self):
        """Initialize standard scenarios if they don't exist."""
        # Check if scenarios exist
        scenarios = self.storage.list_scenarios()
        if not scenarios:
            # Create standard scenario
            standard = Scenario(
                id="standard",
                name="Standard Outbreak",
                description="A standard epidemic outbreak scenario with normal parameters.",
                seed="standard_2023",
                r0=2.5,
                initial_infections={"capital": 100},
                initial_resources=1000,
                difficulty="standard",
                parameters={
                    "disease_mortality": 0.02,
                    "treatment_effectiveness": 0.7,
                    "vaccine_development_time": 120,  # steps
                    "economic_impact_factor": 1.0
                }
            )
            
            # Create challenging scenario
            challenging = Scenario(
                id="challenging",
                name="Challenging Outbreak",
                description="A more difficult scenario with multiple infection sites and higher R0.",
                seed="challenging_2023",
                r0=3.5,
                initial_infections={"capital": 50, "major_city_1": 30, "major_city_2": 20},
                initial_resources=700,
                difficulty="challenging",
                parameters={
                    "disease_mortality": 0.03,
                    "treatment_effectiveness": 0.6,
                    "vaccine_development_time": 150,  # steps
                    "economic_impact_factor": 1.2
                }
            )
            
            # Save scenarios
            self.storage.save_scenario(standard)
            self.storage.save_scenario(challenging)
    
    def register_player(self, name: str, email: str) -> Player:
        """Register a new player."""
        player = Player(name=name, email=email)
        self.storage.save_player(player)
        return player
    
    def get_player(self, player_id: str) -> Optional[Player]:
        """Get player by ID."""
        return self.storage.get_player(player_id)
    
    def update_player_strategy(self, player_id: str, strategy_doc: str) -> bool:
        """Update a player's strategy document."""
        player = self.get_player(player_id)
        if not player:
            return False
            
        player.strategy_document = strategy_doc
        return self.storage.save_player(player)
    
    def get_scenario(self, scenario_id: str) -> Optional[Scenario]:
        """Get scenario by ID."""
        return self.storage.get_scenario(scenario_id)
    
    def list_scenarios(self) -> List[Scenario]:
        """List all available scenarios."""
        return self.storage.list_scenarios()
    
    def record_attempt(self, player_id: str, player_name: str, scenario_id: str, 
                      results: SimulationResults, is_official: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Record a player's attempt.
        
        Returns:
            Tuple[bool, Optional[str]]: Success status and error message if any
        """
        # Validate player
        player = self.get_player(player_id)
        if not player and player_id != "guest":
            return False, "Player not found"
            
        # Validate scenario
        scenario = self.get_scenario(scenario_id)
        if not scenario:
            return False, "Scenario not found"
            
        # Check if player has reached attempt limit (if official)
        if is_official:
            official_attempts = self.storage.list_attempts(
                player_id=player_id, 
                scenario_id=scenario_id,
                is_official=True
            )
            
            if len(official_attempts) >= 3:
                return False, "Maximum official attempts (3) reached for this scenario"
                
        # Record attempt
        attempt = PlayerAttempt(
            player_id=player_id,
            player_name=player_name,
            scenario_id=scenario_id,
            results=results,
            is_official=is_official
        )
        
        success = self.storage.save_attempt(attempt)
        if success:
            # Potentially update leaderboard
            if is_official:
                self._update_leaderboard()
            return True, None
        
        return False, "Failed to save attempt"
    
    def get_player_attempts(self, player_id: str, scenario_id: Optional[str] = None, 
                           is_official: Optional[bool] = None) -> List[PlayerAttempt]:
        """Get all attempts for a player."""
        return self.storage.list_attempts(
            player_id=player_id,
            scenario_id=scenario_id,
            is_official=is_official
        )
    
    def get_best_attempt(self, player_id: str, scenario_id: str, is_official: bool = True) -> Optional[PlayerAttempt]:
        """Get the best attempt for a player in a scenario."""
        attempts = self.get_player_attempts(player_id, scenario_id, is_official)
        if not attempts:
            return None
            
        # Find attempt with highest score
        return max(attempts, key=lambda a: a.results.final_score if a.results else 0)
    
    def calculate_score(self, 
                        population_survived: float,
                        gdp_preserved: float,
                        infection_control: float,
                        resource_efficiency: float,
                        time_to_containment: float) -> float:
        """
        Calculate final score from components.
        Each component is expected to be a 0-1 value.
        """
        # Apply weights
        weighted_score = (
            population_survived * 0.30 +
            gdp_preserved * 0.20 +
            infection_control * 0.20 +
            resource_efficiency * 0.15 +
            time_to_containment * 0.15
        )
        
        return round(weighted_score, 4)
    
    def get_leaderboard(self) -> List[LeaderboardEntry]:
        """Get the current leaderboard."""
        return self.storage.get_leaderboard()
    
    def _update_leaderboard(self) -> bool:
        """
        Update the leaderboard based on current best attempts.
        This should be called whenever a new official attempt is recorded.
        """
        players = self.storage.list_players()
        entries = []
        
        for player in players:
            # Get best scores for each scenario
            standard_attempt = self.get_best_attempt(player.id, "standard", True)
            challenging_attempt = self.get_best_attempt(player.id, "challenging", True)
            
            # Only include players who have completed both scenarios
            if standard_attempt and standard_attempt.results and \
               challenging_attempt and challenging_attempt.results:
                standard_score = standard_attempt.results.final_score
                challenging_score = challenging_attempt.results.final_score
                
                # Calculate average score
                average_score = (standard_score + challenging_score) / 2
                
                # Create leaderboard entry
                entry = LeaderboardEntry(
                    rank=0,  # Will be set later
                    player_id=player.id,
                    player_name=player.name,
                    standard_score=standard_score,
                    challenging_score=challenging_score,
                    average_score=average_score,
                    timestamps={
                        "standard": standard_attempt.timestamp.isoformat(),
                        "challenging": challenging_attempt.timestamp.isoformat()
                    }
                )
                
                entries.append(entry)
        
        # Sort by average score and assign ranks
        entries.sort(key=lambda e: e.average_score, reverse=True)
        for i, entry in enumerate(entries):
            entry.rank = i + 1
        
        # Save updated leaderboard
        return self.storage.save_leaderboard(entries)
    
    def calculate_population_survived_score(self, initial_pop: int, final_pop: int) -> float:
        """Calculate population survived score (0-1)."""
        if initial_pop == 0:
            return 0.0
        
        survival_rate = (initial_pop - final_pop) / initial_pop
        return max(0.0, min(1.0, survival_rate))
    
    def calculate_gdp_preserved_score(self, initial_gdp: float, final_gdp: float) -> float:
        """Calculate GDP preserved score (0-1)."""
        if initial_gdp == 0:
            return 0.0
        
        gdp_change = (final_gdp - initial_gdp) / initial_gdp
        # Transform to 0-1 scale (where 0 = -100% change, 0.5 = 0% change, 1 = +100% change)
        return max(0.0, min(1.0, (gdp_change + 1.0) / 2.0))
    
    def calculate_infection_control_score(self, max_infection_rate: float) -> float:
        """Calculate infection control score (0-1)."""
        # Lower infection rate is better
        return max(0.0, min(1.0, 1.0 - max_infection_rate))
    
    def calculate_resource_efficiency_score(self, 
                                          population_survived: float, 
                                          infection_control: float,
                                          total_resources_spent: float) -> float:
        """Calculate resource efficiency score (0-1)."""
        if total_resources_spent <= 0:
            # No resources spent, base score on other metrics
            return (population_survived + infection_control) / 2
        
        # Calculate efficiency as results per resources spent
        # Using log to avoid extreme differences
        lives_saved_per_resource = population_survived / math.log(1 + total_resources_spent)
        infections_controlled_per_resource = infection_control / math.log(1 + total_resources_spent)
        
        # Combine and normalize
        normalized_efficiency = (lives_saved_per_resource + infections_controlled_per_resource) / 2 * 5.0
        
        return max(0.0, min(1.0, normalized_efficiency))
    
    def calculate_time_to_containment_score(self, containment_step: int, total_steps: int) -> float:
        """Calculate time to containment score (0-1)."""
        if containment_step >= total_steps or containment_step <= 0:
            return 0.0
        
        # Earlier containment is better
        return max(0.0, min(1.0, 1.0 - (containment_step / total_steps)))
    
    def process_simulation_results(self, 
                                  player_id: str,
                                  scenario_id: str,
                                  simulation_data: Dict[str, Any]) -> SimulationResults:
        """
        Process raw simulation data into structured results with scores.
        
        Args:
            player_id: Player ID
            scenario_id: Scenario ID
            simulation_data: Raw data from simulation
            
        Returns:
            SimulationResults object with calculated scores
        """
        # Extract metrics from simulation data
        initial_pop = simulation_data.get("initial_population", 0)
        final_pop = simulation_data.get("final_population", 0)
        dead_pop = simulation_data.get("dead_population", 0)
        
        initial_gdp = simulation_data.get("initial_gdp", 0)
        final_gdp = simulation_data.get("final_gdp", 0)
        
        max_infection_rate = simulation_data.get("max_infection_rate", 0)
        total_resources_spent = simulation_data.get("total_resources_spent", 0)
        containment_step = simulation_data.get("containment_step", 0)
        total_steps = simulation_data.get("total_steps", 730)
        
        # Calculate component scores
        population_survived = self.calculate_population_survived_score(initial_pop, dead_pop)
        gdp_preserved = self.calculate_gdp_preserved_score(initial_gdp, final_gdp)
        infection_control = self.calculate_infection_control_score(max_infection_rate)
        resource_efficiency = self.calculate_resource_efficiency_score(
            population_survived, infection_control, total_resources_spent
        )
        time_to_containment = self.calculate_time_to_containment_score(containment_step, total_steps)
        
        # Calculate final score
        final_score = self.calculate_score(
            population_survived, 
            gdp_preserved,
            infection_control,
            resource_efficiency,
            time_to_containment
        )
        
        # Create and return results object
        return SimulationResults(
            player_id=player_id,
            scenario_id=scenario_id,
            total_steps=total_steps,
            population_survived=population_survived,
            gdp_preserved=gdp_preserved,
            infection_control=infection_control,
            resource_efficiency=resource_efficiency,
            time_to_containment=time_to_containment,
            final_score=final_score,
            metadata=simulation_data.get("metadata", {}),
            raw_metrics=simulation_data
        ) 