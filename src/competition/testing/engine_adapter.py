"""
Engine adapter for testing the competition system.

This module provides a simplified adapter for the EngineV1 class
that can be used for testing purposes without requiring all the
parameters of the actual engine.
"""
import random
import math
from typing import List, Dict, Any, Callable, Optional, Tuple, Set
from datetime import datetime
from dataclasses import dataclass, field
from collections import namedtuple

# Define state object structures
@dataclass
class MockHealthcare:
    capacity: int
    current_usage: int
    resources_invested: int = 0
    
    @property
    def utilization_rate(self) -> float:
        if self.capacity == 0:
            return 1.0
        return min(1.0, self.current_usage / self.capacity)

@dataclass
class MockEconomy:
    initial_gdp: int
    current_gdp: int
    lockdown_level: float = 0.0
    resources_invested: int = 0
    gdp: int = 0
    
    def __post_init__(self):
        """Initialize gdp to match current_gdp"""
        self.gdp = self.current_gdp
    
    @property
    def gdp_impact(self) -> float:
        return (self.initial_gdp - self.current_gdp) / self.initial_gdp if self.initial_gdp > 0 else 0

@dataclass
class MockPopulation:
    total: int
    healthy: int
    infected: int
    recovered: int
    dead: int

@dataclass
class MockResearch:
    progress: float = 0.0
    resources_invested: int = 0

@dataclass
class MockResources:
    available: int
    total_initial: int
    total_spent: int = 0
    
    @property
    def efficiency(self) -> float:
        if self.total_spent == 0:
            return 1.0
        # Higher values mean more efficient use of resources
        return min(1.0, 0.5 + (self.available / (self.total_initial * 2)))

@dataclass
class MockState:
    """Represents the current state of the simulation."""
    population: MockPopulation
    economy: MockEconomy
    healthcare: MockHealthcare
    research: MockResearch
    resources: MockResources
    day: int = 0
    r0: float = 2.5
    travel_restricted: bool = False
    lockdown_level: float = 0.0

class MockEngine:
    """
    A lightweight mock of the epidemic engine for testing competition features.
    
    This provides a simplified implementation that mimics the behavior of
    the real engine without the full complexity.
    """
    
    # Constants to match EngineV1
    MAX_STEPS = 1000
    STATUS_SET = {"ALIVE", "DORMANT", "DEAD"}
    
    def __init__(self, 
                name: str = "MockEngine",
                state: Any = None,
                processes: List[Any] = None,
                entities: List[Any] = None,
                speed: int = 1,
                history_persistence: int = 100,
                pr_stat_chart: Dict[str, List[List[int]]] = None):
        """
        Initialize the mock engine.
        
        Parameters match EngineV1 but are all optional for easier testing.
        
        Parameters:
        -----------
        name: str
            The name of the engine.
        state: Any
            The state of the engine (simplified in mock version).
        processes: List[Any]
            The processes of the engine (simplified in mock version).
        entities: List[Any]
            The entities of the engine (simplified in mock version).
        speed: int
            The speed of the engine.
        history_persistence: int
            How often to persist history.
        pr_stat_chart: Dict[str, List[List[int]]]
            Process status chart (simplified in mock version).
        """
        # Initialize with parameters matching EngineV1
        self.name = name
        self.processes = processes or []
        self.entities = entities or []
        self.speed = speed
        self.history_persistence = history_persistence
        self.pr_stat_chart = pr_stat_chart or {}
        
        # Status tracking
        self.status = "DORMANT"
        self.STEP = 0
        self.info_history = {}
        self.run_call_history = []
        self.state_sync_mode = "RANK"
        
        self.step_callbacks = []
        
        # Simulation state
        self.current_step = 0
        
        # Track lockdown level and travel restrictions
        self.lockdown_level = 0.0
        self.travel_restricted = False
        
        # Initialize metrics
        self.metrics = {
            "population": {
                "total": 10000,
                "healthy": 9900,
                "infected": 100,
                "recovered": 0,
                "dead": 0,
            },
            "economy": {
                "initial_gdp": 1000,
                "current_gdp": 1000,
            },
            "healthcare": {
                "capacity": 500,
                "current_usage": 0,
            },
            "resources": {
                "available": 5000,
                "total_initial": 5000,
                "total_spent": 0,
                "healthcare": 0,
                "economic": 0,
                "research": 0,
                "testing": 0,
            },
            "research": {
                "progress": 0.0,
            },
            "max_infection_rate": 0.01,  # Initial infected / total
            "containment_achieved": False,
            "containment_step": -1,
        }
        
        # Initialize state with the metrics
        self.state = self._create_initial_state() if state is None else state
        
        # Keep history of metrics for visualization
        self.metric_history = []
        self._record_metrics()
        
        # Disease parameters - match typical values for EngineV1
        self.disease_params = {
            "r0_base": 3.0,  # Basic reproduction number
            "infection_duration": 14,  # Days an infected person remains infectious
            "mortality_rate_base": 0.02,  # Base mortality rate without healthcare
            "recovery_rate": 0.1,  # Base recovery rate per step
            "healthcare_effectiveness": 0.5,  # Effectiveness of healthcare resources
        }
        
        # Intervention effects - match typical EngineV1 response curves
        self.intervention_effects = {
            "lockdown_r0_reduction": 0.85,  # Increased from 0.7 - Maximum R0 reduction from lockdown
            "healthcare_mortality_reduction": 0.9,  # Increased from 0.8 - Maximum reduction in mortality from healthcare
            "economic_support_efficiency": 0.9,  # Increased from 0.8 - Effectiveness of economic support
            "research_effectiveness": 0.008,  # Increased from 0.005 - Per-unit research effectiveness
            "testing_detection_improvement": 0.7,  # Increased from 0.5 - Maximum improvement from testing
        }
        
        # Seed for reproducibility while allowing for randomness
        random.seed(42 + random.randint(0, 100))  # Add some randomness to avoid identical runs
    
    def _create_initial_state(self):
        """Create an initial state object from metrics."""
        return MockState(
            population=MockPopulation(
                total=self.metrics["population"]["total"],
                healthy=self.metrics["population"]["healthy"],
                infected=self.metrics["population"]["infected"],
                recovered=self.metrics["population"]["recovered"],
                dead=self.metrics["population"]["dead"]
            ),
            economy=MockEconomy(
                initial_gdp=self.metrics["economy"]["initial_gdp"],
                current_gdp=self.metrics["economy"]["current_gdp"],
                gdp=self.metrics["economy"]["current_gdp"]  # Initialize gdp explicitly
            ),
            healthcare=MockHealthcare(
                capacity=self.metrics["healthcare"]["capacity"],
                current_usage=self.metrics["healthcare"]["current_usage"]
            ),
            research=MockResearch(
                progress=self.metrics["research"]["progress"]
            ),
            resources=MockResources(
                available=self.metrics["resources"]["available"],
                total_initial=self.metrics["resources"]["total_initial"],
                total_spent=self.metrics["resources"]["total_spent"]
            ),
            lockdown_level=self.lockdown_level,
            travel_restricted=self.travel_restricted
        )
    
    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value: int):
        self._speed = max(1, value)
    
    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value: str):
        assert value in self.STATUS_SET, f"Invalid status: {value}"
        self._status = value
    
    def register_step_callback(self, callback):
        """Register a callback function to be called after each step."""
        if callable(callback):
            self.step_callbacks.append(callback)
        else:
            raise TypeError("Callback must be callable")
    
    def run(self, steps=1):
        """
        Run the simulation for the specified number of steps.
        
        Parameters:
        -----------
        steps: int
            Number of steps to run
            
        Returns:
        --------
        MockState
            The current state after running
        """
        for _ in range(steps):
            self.current_step += 1
            
            # Calculate effective R0 based on lockdown
            effective_r0 = self.disease_params["r0_base"] * (
                1 - self.lockdown_level * self.intervention_effects["lockdown_r0_reduction"]
            )
            
            # Healthcare capacity affects mortality
            healthcare_resources = self.metrics["resources"].get("healthcare", 0)
            healthcare_capacity = min(1.0, healthcare_resources / 1000) 
            healthcare_effect = healthcare_capacity * self.intervention_effects["healthcare_mortality_reduction"]
            effective_mortality = self.disease_params["mortality_rate_base"] * (1 - healthcare_effect)
            
            # Calculate new infections
            current_infected = self.metrics["population"]["infected"]
            total_population = self.metrics["population"]["total"]
            susceptible = self.metrics["population"]["healthy"]
            
            # Travel restrictions reduce infection spread
            travel_modifier = 0.7 if self.travel_restricted else 1.0
            
            # New infections formula (simplified SIR model)
            contact_rate = effective_r0 / self.disease_params["infection_duration"] * travel_modifier
            new_infections = int(contact_rate * current_infected * susceptible / total_population)
            new_infections = min(new_infections, susceptible)  # Can't infect more than susceptible population
            
            # Update healthy and infected
            self.metrics["population"]["healthy"] -= new_infections
            self.metrics["population"]["infected"] += new_infections
            
            # Calculate recoveries and deaths with improved randomness
            recovery_probability = self.disease_params["recovery_rate"] * (1 + healthcare_effect)
            death_probability = effective_mortality * (1 - healthcare_effect * 0.5)  # Healthcare also helps prevent deaths
            
            # Process each infected person
            recoveries = 0
            deaths = 0
            for _ in range(current_infected):
                roll = random.random()
                if roll < recovery_probability:
                    recoveries += 1
                elif roll < recovery_probability + death_probability:
                    deaths += 1
            
            # Ensure recoveries + deaths don't exceed infected
            recoveries = min(recoveries, current_infected - deaths)
            
            # Update GDP based on lockdown level and economic support
            economic_impact = self.lockdown_level * 0.05  # Lockdown reduces GDP by up to 5% per step
            economic_resources = self.metrics["resources"].get("economic", 0)
            economic_support = min(1.0, economic_resources / 500) * self.intervention_effects["economic_support_efficiency"]
            
            # Economic impact is reduced by economic support
            economic_impact = economic_impact * (1 - economic_support)
            
            # Update GDP - smoother impact with some randomness to create differences between strategies
            gdp_randomness = random.uniform(0.95, 1.05)  # +/- 5% randomness
            self.metrics["economy"]["current_gdp"] = int(self.metrics["economy"]["current_gdp"] * (1 - economic_impact) * gdp_randomness)
            
            # Research speeds up recovery and containment
            research_resources = self.metrics["resources"].get("research", 0)
            if research_resources > 0:
                research_progress = research_resources * self.intervention_effects["research_effectiveness"]
                self.metrics["research"]["progress"] += research_progress
                self.metrics["research"]["progress"] = min(1.0, self.metrics["research"]["progress"])
            
            # Testing improves detection and targeted measures
            testing_resources = self.metrics["resources"].get("testing", 0)
            if testing_resources > 0:
                testing_effectiveness = min(0.5, testing_resources / 400) * self.intervention_effects["testing_detection_improvement"]
                # Testing reduces new infections by enabling targeted isolation
                new_infections = int(new_infections * (1 - testing_effectiveness))
            
            # Update healthcare usage
            self.metrics["healthcare"]["current_usage"] = min(self.metrics["healthcare"]["capacity"], 
                                                           int(current_infected * 0.2))  # Assume 20% need healthcare
            
            # Check if containment has been achieved (less than 0.1% of population infected and research progress > 80%)
            infection_rate = self.metrics["population"]["infected"] / self.metrics["population"]["total"]
            if infection_rate < 0.001 and self.metrics["research"]["progress"] > 0.8 and not self.metrics["containment_achieved"]:
                self.metrics["containment_achieved"] = True
                self.metrics["containment_step"] = self.current_step
            
            # Track maximum infection rate
            if infection_rate > self.metrics["max_infection_rate"]:
                self.metrics["max_infection_rate"] = infection_rate
            
            # Update infected, recovered, dead counts
            self.metrics["population"]["infected"] = current_infected + new_infections - recoveries - deaths
            self.metrics["population"]["recovered"] += recoveries
            self.metrics["population"]["dead"] += deaths
            
            # Update state and record metrics
            self._update_state()
            self._record_metrics()
            
            # Execute callbacks
            for callback in self.step_callbacks:
                try:
                    callback(self.current_step, self.state)
                except TypeError:
                    # Handle the case where callback doesn't accept parameters
                    # This is for compatibility with both signatures
                    callback()
        
        return self.state
    
    def _update_state(self):
        """Update the state object with current metrics."""
        self.state.day = self.current_step
        self.state.population.total = self.metrics["population"]["total"]
        self.state.population.healthy = self.metrics["population"]["healthy"]
        self.state.population.infected = self.metrics["population"]["infected"]
        self.state.population.recovered = self.metrics["population"]["recovered"]
        self.state.population.dead = self.metrics["population"]["dead"]
        
        self.state.economy.initial_gdp = self.metrics["economy"]["initial_gdp"]
        self.state.economy.current_gdp = self.metrics["economy"]["current_gdp"]
        self.state.economy.gdp = self.metrics["economy"]["current_gdp"]  # Keep gdp in sync
        
        self.state.healthcare.capacity = self.metrics["healthcare"]["capacity"]
        self.state.healthcare.current_usage = self.metrics["healthcare"]["current_usage"]
        
        self.state.resources.available = self.metrics["resources"]["available"]
        self.state.resources.total_initial = self.metrics["resources"]["total_initial"]
        self.state.resources.total_spent = self.metrics["resources"]["total_spent"]
        
        self.state.research.progress = self.metrics["research"]["progress"]
        
        self.state.r0 = self.disease_params["r0_base"]
        self.state.lockdown_level = self.lockdown_level
        self.state.travel_restricted = self.travel_restricted
    
    def _record_metrics(self):
        """Record current metrics for analysis."""
        metrics = {
            "step": self.current_step,
            "population": self.metrics["population"].copy(),
            "economy": self.metrics["economy"].copy(),
            "healthcare": self.metrics["healthcare"].copy(),
            "resources": self.metrics["resources"].copy(),
            "research": self.metrics["research"].copy(),
            "lockdown_level": self.lockdown_level,
            "travel_restricted": self.travel_restricted,
            "containment_achieved": self.metrics["containment_achieved"],
            "max_infection_rate": self.metrics["max_infection_rate"]
        }
        
        self.metric_history.append(metrics)
    
    def set_lockdown_level(self, level):
        """
        Set the lockdown level (0-1).
        
        Parameters:
        -----------
        level: float
            Lockdown level from 0 (no restrictions) to 1 (complete lockdown)
        """
        self.lockdown_level = max(0, min(1, level))
    
    def get_lockdown_level(self):
        """
        Get the current lockdown level.
        
        Returns:
        --------
        float
            Current lockdown level
        """
        return self.lockdown_level
    
    def allocate_resources(self, category, amount):
        """
        Allocate resources to a specific category.
        
        Parameters:
        -----------
        category: str
            Category to allocate resources to ('healthcare', 'economic', 'research', 'testing')
        amount: int
            Amount of resources to allocate
        """
        # Ensure we only spend available resources
        amount = min(amount, self.metrics["resources"]["available"])
        
        if amount <= 0:
            return
            
        # Update category allocation
        self.metrics["resources"][category] = self.metrics["resources"].get(category, 0) + amount
            
        # Update resource totals
        self.metrics["resources"]["available"] -= amount
        self.metrics["resources"]["total_spent"] += amount
    
    def get_allocated_resources(self, category):
        """
        Get the resources allocated to a specific category.
        
        Parameters:
        -----------
        category: str
            Category to get resources for
            
        Returns:
        --------
        int
            Amount of resources allocated to the category
        """
        return self.metrics["resources"].get(category, 0)
    
    def restrict_travel(self, restricted):
        """
        Set whether travel is restricted.
        
        Parameters:
        -----------
        restricted: bool
            Whether travel should be restricted
        """
        self.travel_restricted = bool(restricted)
    
    def is_travel_restricted(self):
        """
        Check if travel is currently restricted.
        
        Returns:
        --------
        bool
            Whether travel is restricted
        """
        return self.travel_restricted
    
    def get_metrics(self):
        """
        Get the current metrics.
        
        Returns:
        --------
        dict
            Current metrics dictionary
        """
        return self.metrics
    
    def get_metrics_history(self):
        """
        Get the history of metrics.
        
        Returns:
        --------
        list
            List of metric snapshots
        """
        return self.metric_history
    
    # Additional EngineV1 compatible methods
    def pause(self):
        """Pause the engine."""
        self.status = "DORMANT"
    
    def play(self):
        """Play the engine."""
        self.status = "ALIVE"
    
    def stop(self):
        """Stop the engine."""
        self.status = "DEAD"
    
    def list_processes(self):
        """
        List process IDs (simplified for mock).
        
        Returns:
        --------
        List[str]
            List of process IDs
        """
        return [f"mock_process_{i}" for i in range(len(self.processes))] 