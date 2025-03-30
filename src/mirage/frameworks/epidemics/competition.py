"""
Competition module for the Epidemic 2.0 simulation.

This module provides functionality for:
1. Standardizing initial conditions for all players
2. Implementing a scoring system to evaluate player performance
3. Tracking and storing player results for comparison
4. Providing different strategic paths for players to explore
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd
import os
import json
import datetime
from pathlib import Path
from ...engines import firefly

class CompetitionManager:
    """
    Manages the competitive aspects of the epidemic simulation.
    
    This class handles:
    - Standardized initialization for fair competition
    - Scoring and evaluation of player strategies
    - Result tracking and comparison
    """
    
    def __init__(
        self, 
        engine: 'firefly.FireflyV1',
        countries: Dict[str, Any],
        base_score_weights: Optional[Dict[str, float]] = None,
        results_dir: str = None
    ):
        """
        Initialize the competition manager.
        
        Parameters
        ----------
        engine : firefly.FireflyV1
            The simulation engine
        countries : Dict[str, Any]
            Dictionary of country objects
        base_score_weights : Dict[str, float], optional
            Weights for different scoring components (default provides balanced weights)
        results_dir : str, optional
            Directory to store competition results
        """
        self.engine = engine
        self.countries = countries
        self.player_name = engine.player_name
        
        # Default scoring weights if none provided
        self.score_weights = base_score_weights or {
            "population_survived": 0.30,  # % of initial population that survived
            "gdp_preserved": 0.20,        # % of GDP preserved/growth
            "infection_control": 0.20,    # How well infections were controlled
            "resource_efficiency": 0.15,  # Efficient use of resources
            "time_to_containment": 0.15,  # How quickly the epidemic was contained
        }
        
        # Setup results directory
        if results_dir is None:
            results_dir = os.path.join(os.getcwd(), "competition_results")
        self.results_dir = results_dir
        Path(self.results_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize metrics tracking
        self.initial_state = self._capture_initial_state()
        self.metrics_history = []
        self.final_score = None
        
        # Register step listeners to track metrics at each step
        self.engine.register_step_callback(self._track_metrics)

    def _capture_initial_state(self) -> Dict[str, Any]:
        """
        Capture the initial state of the simulation for future comparison.
        
        Returns
        -------
        Dict[str, Any]
            Initial state metrics
        """
        initial_state = {
            "timestamp": datetime.datetime.now().isoformat(),
            "countries": {}
        }
        
        total_population = 0
        total_infected = 0
        total_gdp = 0
        
        for country_name, country in self.countries.items():
            country_data = country.model_dump()
            country_state = {
                "gdp": country_data["gdp"],
                "health_resource_stockpile": country_data["health_resource_stockpile"],
                "sanitation_equipment_stockpile": country_data["sanitation_equipment_stockpile"],
                "human_welfare_resource": country_data["human_welfare_resource"],
                "loci": []
            }
            
            country_population = 0
            country_infected = 0
            
            for locus in country_data["loci"]:
                locus_state = {
                    "name": locus["name"],
                    "susceptible": locus["susceptible"],
                    "infected": locus["infected"],
                    "recovered": locus["recovered"],
                    "dead": locus["dead"]
                }
                country_state["loci"].append(locus_state)
                
                locus_population = locus["susceptible"] + locus["infected"] + locus["recovered"]
                country_population += locus_population
                country_infected += locus["infected"]
            
            country_state["total_population"] = country_population
            country_state["total_infected"] = country_infected
            
            initial_state["countries"][country_name] = country_state
            total_population += country_population
            total_infected += country_infected
            total_gdp += country_data["gdp"]
        
        initial_state["total_population"] = total_population
        initial_state["total_infected"] = total_infected
        initial_state["total_gdp"] = total_gdp
        
        return initial_state

    def _track_metrics(self) -> None:
        """
        Track metrics at each simulation step.
        """
        step = self.engine.STEP
        
        metrics = {
            "step": step,
            "timestamp": datetime.datetime.now().isoformat(),
            "countries": {}
        }
        
        total_population = 0
        total_susceptible = 0
        total_infected = 0
        total_recovered = 0
        total_dead = 0
        total_gdp = 0
        
        for country_name, country in self.countries.items():
            country_data = country.model_dump()
            country_metrics = {
                "gdp": country_data["gdp"],
                "health_resource_stockpile": country_data["health_resource_stockpile"],
                "sanitation_equipment_stockpile": country_data["sanitation_equipment_stockpile"],
                "human_welfare_resource": country_data["human_welfare_resource"],
            }
            
            country_susceptible = 0
            country_infected = 0
            country_recovered = 0
            country_dead = 0
            
            for locus in country_data["loci"]:
                country_susceptible += locus["susceptible"]
                country_infected += locus["infected"]
                country_recovered += locus["recovered"]
                country_dead += locus["dead"]
            
            country_metrics["susceptible"] = country_susceptible
            country_metrics["infected"] = country_infected
            country_metrics["recovered"] = country_recovered
            country_metrics["dead"] = country_dead
            country_metrics["total_population"] = country_susceptible + country_infected + country_recovered
            
            metrics["countries"][country_name] = country_metrics
            
            total_susceptible += country_susceptible
            total_infected += country_infected
            total_recovered += country_recovered
            total_dead += country_dead
            total_gdp += country_data["gdp"]
        
        metrics["total_population"] = total_susceptible + total_infected + total_recovered
        metrics["total_susceptible"] = total_susceptible
        metrics["total_infected"] = total_infected
        metrics["total_recovered"] = total_recovered
        metrics["total_dead"] = total_dead
        metrics["total_gdp"] = total_gdp
        
        # Calculate infection rate
        if metrics["total_population"] > 0:
            metrics["infection_rate"] = metrics["total_infected"] / metrics["total_population"]
        else:
            metrics["infection_rate"] = 0
            
        # Calculate death rate
        initial_population = self.initial_state["total_population"]
        if initial_population > 0:
            metrics["death_rate"] = total_dead / initial_population
        else:
            metrics["death_rate"] = 0
            
        # Calculate GDP change
        initial_gdp = self.initial_state["total_gdp"]
        if initial_gdp > 0:
            metrics["gdp_change"] = (total_gdp - initial_gdp) / initial_gdp
        else:
            metrics["gdp_change"] = 0
        
        self.metrics_history.append(metrics)

    def calculate_score(self) -> Dict[str, float]:
        """
        Calculate the final score based on simulation results.
        
        Returns
        -------
        Dict[str, float]
            Component scores and final score
        """
        if not self.metrics_history:
            raise ValueError("No metrics have been recorded. Run the simulation first.")
        
        final_metrics = self.metrics_history[-1]
        initial_state = self.initial_state
        
        # Calculate component scores
        
        # 1. Population survived score (higher is better)
        initial_population = initial_state["total_population"]
        final_population = final_metrics["total_population"]
        dead_population = final_metrics["total_dead"]
        
        if initial_population > 0:
            population_survived_score = (initial_population - dead_population) / initial_population
        else:
            population_survived_score = 0
        
        # 2. GDP preserved score (higher is better)
        initial_gdp = initial_state["total_gdp"]
        final_gdp = final_metrics["total_gdp"]
        
        if initial_gdp > 0:
            gdp_change = (final_gdp - initial_gdp) / initial_gdp
            # Cap GDP growth for scoring purposes
            gdp_preserved_score = min(1.0, max(0.0, (gdp_change + 1.0) / 2.0))
        else:
            gdp_preserved_score = 0
        
        # 3. Infection control score (higher is better)
        # Based on the percentage of population that was never infected
        
        # Get maximum infection rate across all steps
        max_infection_rate = max(metrics["infection_rate"] for metrics in self.metrics_history)
        infection_control_score = 1.0 - max_infection_rate
        
        # 4. Resource efficiency score (higher is better)
        # Evaluate how efficiently resources were used
        
        # Get the sum of all resources spent
        total_resources_spent = 0
        for country_name, country in self.countries.items():
            initial_country = initial_state["countries"][country_name]
            final_country = final_metrics["countries"][country_name]
            
            # Calculate resources spent
            resources_spent = (
                (initial_country["health_resource_stockpile"] - final_country["health_resource_stockpile"]) +
                (initial_country["sanitation_equipment_stockpile"] - final_country["sanitation_equipment_stockpile"]) +
                (initial_country["human_welfare_resource"] - final_country["human_welfare_resource"])
            )
            
            # Account only for positive spending
            total_resources_spent += max(0, resources_spent)
        
        # Normalize resource efficiency (lower spending for same results is better)
        # We use a logarithmic scale to avoid extreme penalties for high spending
        if total_resources_spent > 0:
            # Normalize based on population saved and infections controlled
            lives_saved_per_resource = population_survived_score / np.log1p(total_resources_spent)
            infections_controlled_per_resource = infection_control_score / np.log1p(total_resources_spent)
            
            # Combine both factors
            resource_efficiency_score = (lives_saved_per_resource + infections_controlled_per_resource) / 2
            
            # Normalize to 0-1 range (empirically determined)
            resource_efficiency_score = min(1.0, max(0.0, resource_efficiency_score * 5.0))
        else:
            # If no resources spent but good results, that's ideal efficiency
            resource_efficiency_score = 0.5 * (population_survived_score + infection_control_score)
        
        # 5. Time to containment score (higher is better)
        # Earlier containment is better
        
        # Find the step where the infection rate started consistently decreasing
        containment_step = None
        for i in range(1, len(self.metrics_history)):
            if (self.metrics_history[i]["infection_rate"] < self.metrics_history[i-1]["infection_rate"]):
                # Check if it's a consistent decrease
                consistent_decrease = True
                for j in range(i, min(i+10, len(self.metrics_history))):
                    if j < len(self.metrics_history) - 1:
                        if self.metrics_history[j]["infection_rate"] < self.metrics_history[j+1]["infection_rate"]:
                            consistent_decrease = False
                            break
                
                if consistent_decrease:
                    containment_step = self.metrics_history[i]["step"]
                    break
        
        if containment_step is not None:
            # Earlier containment is better
            total_steps = self.engine.STEP
            if total_steps > 0:
                time_to_containment_score = 1.0 - (containment_step / total_steps)
            else:
                time_to_containment_score = 0
        else:
            # No containment achieved
            time_to_containment_score = 0
        
        # Calculate weighted final score
        scores = {
            "population_survived": population_survived_score,
            "gdp_preserved": gdp_preserved_score,
            "infection_control": infection_control_score,
            "resource_efficiency": resource_efficiency_score,
            "time_to_containment": time_to_containment_score
        }
        
        final_score = sum(scores[key] * self.score_weights[key] for key in scores)
        
        # Add final score to the scores dictionary
        scores["final_score"] = final_score
        
        self.final_score = scores
        return scores

    def save_results(self) -> str:
        """
        Save competition results to disk.
        
        Returns
        -------
        str
            Path to the saved results file
        """
        if self.final_score is None:
            self.calculate_score()
        
        result_data = {
            "player_name": self.player_name,
            "timestamp": datetime.datetime.now().isoformat(),
            "final_score": self.final_score,
            "score_weights": self.score_weights,
            "initial_state": self.initial_state,
            "final_state": self.metrics_history[-1] if self.metrics_history else None,
            # Include a subset of metrics history to keep file size reasonable
            "metrics_history_sample": self.metrics_history[::10] if len(self.metrics_history) > 10 else self.metrics_history
        }
        
        result_file = os.path.join(
            self.results_dir, 
            f"{self.player_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        with open(result_file, 'w') as f:
            json.dump(result_data, f, indent=2)
            
        return result_file

class CompetitionLeaderboard:
    """
    Manages the leaderboard for the epidemic simulation competition.
    """
    
    def __init__(self, results_dir: str = None):
        """
        Initialize the competition leaderboard.
        
        Parameters
        ----------
        results_dir : str, optional
            Directory containing competition results
        """
        if results_dir is None:
            results_dir = os.path.join(os.getcwd(), "competition_results")
        self.results_dir = results_dir
        
    def generate_leaderboard(self) -> pd.DataFrame:
        """
        Generate a leaderboard from all available results.
        
        Returns
        -------
        pd.DataFrame
            Leaderboard with player rankings
        """
        result_files = list(Path(self.results_dir).glob("*.json"))
        
        if not result_files:
            return pd.DataFrame(columns=["Player", "Final Score", "Population Survived", 
                                        "GDP Preserved", "Infection Control", 
                                        "Resource Efficiency", "Time to Containment"])
        
        leaderboard_data = []
        
        for result_file in result_files:
            with open(result_file, 'r') as f:
                result_data = json.load(f)
            
            # Get latest result for each player
            player_entry = {
                "Player": result_data["player_name"],
                "Final Score": result_data["final_score"]["final_score"],
                "Population Survived": result_data["final_score"]["population_survived"],
                "GDP Preserved": result_data["final_score"]["gdp_preserved"],
                "Infection Control": result_data["final_score"]["infection_control"],
                "Resource Efficiency": result_data["final_score"]["resource_efficiency"],
                "Time to Containment": result_data["final_score"]["time_to_containment"],
                "Timestamp": result_data["timestamp"]
            }
            
            leaderboard_data.append(player_entry)
        
        # Create DataFrame and keep only the latest result for each player
        leaderboard_df = pd.DataFrame(leaderboard_data)
        leaderboard_df["Timestamp"] = pd.to_datetime(leaderboard_df["Timestamp"])
        
        # Get the latest entry for each player
        latest_results = leaderboard_df.sort_values("Timestamp").groupby("Player").last().reset_index()
        
        # Sort by final score (descending)
        leaderboard = latest_results.sort_values("Final Score", ascending=False)
        
        # Drop timestamp column for display
        leaderboard = leaderboard.drop(columns=["Timestamp"])
        
        # Add rank column
        leaderboard.insert(0, "Rank", range(1, len(leaderboard) + 1))
        
        return leaderboard
    
    def save_leaderboard(self, output_file: str = None) -> str:
        """
        Generate and save leaderboard to a file.
        
        Parameters
        ----------
        output_file : str, optional
            Path to save the leaderboard (default: leaderboard.csv in results_dir)
            
        Returns
        -------
        str
            Path to the saved leaderboard file
        """
        leaderboard = self.generate_leaderboard()
        
        if output_file is None:
            output_file = os.path.join(self.results_dir, "leaderboard.csv")
        
        leaderboard.to_csv(output_file, index=False)
        return output_file

def add_competition_to_preset(
    countries, 
    core_processes, 
    epidemic_two_engine, 
    tboard, 
    score_weights: Optional[Dict[str, float]] = None,
    results_dir: str = None
) -> Tuple[CompetitionManager, CompetitionLeaderboard]:
    """
    Add competition functionality to an existing preset.
    
    Parameters
    ----------
    countries : dict
        Dictionary of country objects
    core_processes : dict
        Dictionary of core processes
    epidemic_two_engine : firefly.FireflyV1
        The simulation engine
    tboard : TbxTimeseriesLoggerV1
        Tensorboard logger
    score_weights : Dict[str, float], optional
        Weights for different scoring components
    results_dir : str, optional
        Directory to store competition results
        
    Returns
    -------
    Tuple[CompetitionManager, CompetitionLeaderboard]
        Competition manager and leaderboard objects
    """
    competition_manager = CompetitionManager(
        epidemic_two_engine,
        countries,
        score_weights,
        results_dir
    )
    
    leaderboard = CompetitionLeaderboard(results_dir)
    
    return competition_manager, leaderboard

def create_standardized_initial_conditions(base_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create standardized initial conditions for all players.
    
    Parameters
    ----------
    base_config : Dict[str, Any]
        Base configuration to standardize
        
    Returns
    -------
    Dict[str, Any]
        Standardized configuration
    """
    # This function would create a standard starting point for all players
    # by modifying the base configuration to ensure fairness
    
    # For now, we'll return the base configuration unchanged
    # In a real implementation, you might want to modify specific parameters
    # to ensure all players start with the same challenges
    return base_config 