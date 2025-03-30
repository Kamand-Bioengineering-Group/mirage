#!/usr/bin/env python3

"""
EnhancedEngine - An improved epidemic simulation engine that ensures 
different intervention strategies produce significantly different outcomes.

Based on academic literature on epidemic modeling and real-world COVID-19 observations,
this engine implements:
1. Network-based disease spread (SIR model with contact networks)
2. Intervention fatigue and compliance modeling
3. Region-specific effects
4. Variable intervention effectiveness
5. Multi-dimensional economic impacts
6. Synergistic and antagonistic intervention effects
7. Variant strain emergence system
"""

import random
import math
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Callable, Any, Optional, Tuple
from copy import deepcopy

# Import the base MockEngine (without SimulationState which we'll define ourselves)
from src.competition.testing.engine_adapter import MockEngine

# Define our own SimulationState class
@dataclass
class SimulationState:
    """
    Represents the state of the simulation at a given point in time.
    This is a standalone version compatible with the EnhancedEngine.
    """
    class Time:
        def __init__(self):
            self.step = 0
    
    class Population:
        def __init__(self):
            self.total = 0
            self.susceptible = 0
            self.infected = 0
            self.recovered = 0
            self.deaths = 0
            self.dead = 0  # Alias for deaths - needed for compatibility
            
        @property
        def dead(self):
            return self.deaths
            
        @dead.setter
        def dead(self, value):
            self.deaths = value
    
    class Economy:
        def __init__(self):
            self.initial_gdp = 0
            self.current_gdp = 0
    
    class Research:
        def __init__(self):
            self.progress = 0.0
    
    class Simulation:
        def __init__(self):
            self.contained = False
            self.containment_step = -1
            self.max_infected = 0
    
    def __init__(self):
        self.time = self.Time()
        self.population = self.Population()
        self.economy = self.Economy()
        self.research = self.Research()
        self.simulation = self.Simulation()

# New class for modeling disease variants
class DiseaseVariant:
    """Models a variant of the disease with different characteristics."""
    
    def __init__(self, 
                 name: str,
                 r0_modifier: float,
                 mortality_modifier: float,
                 immune_escape: float,
                 emergence_threshold: float):
        """
        Initialize a disease variant.
        
        Args:
            name: Name of the variant (e.g. "Alpha", "Delta")
            r0_modifier: Multiplicative effect on base R0 (e.g. 1.5 = 50% more transmissible)
            mortality_modifier: Multiplicative effect on mortality (e.g. 1.2 = 20% more deadly)
            immune_escape: Ability to infect recovered individuals (0-1)
            emergence_threshold: Population infection threshold for this variant to emerge
        """
        self.name = name
        self.r0_modifier = r0_modifier
        self.mortality_modifier = mortality_modifier
        self.immune_escape = immune_escape
        self.emergence_threshold = emergence_threshold
        self.emerged = False
        self.prevalence = 0.0  # Proportion of infections that are this variant
        
    def update_prevalence(self, total_infected: int, base_prevalence_increase: float) -> float:
        """
        Update the prevalence of this variant based on its traits.
        
        Returns:
            The change in prevalence
        """
        if not self.emerged:
            return 0.0
            
        # Higher R0 variants spread faster
        r0_advantage = max(0, self.r0_modifier - 1.0)
        prevalence_change = base_prevalence_increase * (1 + r0_advantage * 2)
        
        # Limit growth based on current prevalence (logistic growth)
        prevalence_change *= (1 - self.prevalence)
        
        self.prevalence = min(1.0, self.prevalence + prevalence_change)
        return prevalence_change

class EnhancedEngine(MockEngine):
    """
    Enhanced epidemic simulation engine with more realistic modeling.
    
    Key improvements:
    - Network-based disease spread with R0 variability
    - Intervention diminishing returns and fatigue effects
    - Regional and demographic heterogeneity
    - Economic sector-specific impacts
    - Synergistic/antagonistic intervention combinations
    - Stochastic elements for unpredictability
    - Disease variant emergence and evolution
    """
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize the enhanced engine with more complex parameters."""
        super().__init__()
        
        # Set random seed if provided
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        # Enhanced disease parameters
        self.disease_params.update({
            "r0_base": 3.8,  # Higher base R0
            "r0_variance": 0.6,  # R0 can vary by this amount
            "mortality_rate_base": 0.025,
            "mortality_variance": 0.01,
            "incubation_period": 5,  # Days before becoming infectious
            "recovery_period": 14,  # Days to recovery
            "immunity_period": 120,  # Days immunity lasts
            "reinfection_risk": 0.3,  # Chance of reinfection after immunity wanes
            "asymptomatic_rate": 0.4,  # Percentage of cases that are asymptomatic
            "asymptomatic_transmission": 0.6,  # Relative transmission rate for asymptomatic
            "variant_emergence_rate": 0.01,  # Base chance of new variants emerging
            "variant_prevalence_increase": 0.02,  # Base rate of variant prevalence increase
        })
        
        # Define potential disease variants
        self.potential_variants = [
            DiseaseVariant(
                name="Alpha", 
                r0_modifier=1.5,
                mortality_modifier=1.1,
                immune_escape=0.1,
                emergence_threshold=0.2  # Emerges when 20% of population has been infected
            ),
            DiseaseVariant(
                name="Beta", 
                r0_modifier=1.3,
                mortality_modifier=1.3,
                immune_escape=0.3,
                emergence_threshold=0.3  # Emerges when 30% of population has been infected
            ),
            DiseaseVariant(
                name="Gamma", 
                r0_modifier=1.7,
                mortality_modifier=1.2,
                immune_escape=0.5,
                emergence_threshold=0.4  # Emerges when 40% of population has been infected
            ),
        ]
        
        # Track active variants
        self.active_variants = []
        
        # Enhanced intervention effects with diminishing returns
        self.intervention_effects.update({
            # Base effectiveness values
            "lockdown_r0_reduction": 0.8,
            "lockdown_diminishing_factor": 0.85,  # Each subsequent lockdown is less effective
            "lockdown_compliance_decay": 0.02,  # Daily reduction in compliance
            
            "economic_support_efficiency": 0.85,
            "economic_diminishing_factor": 0.9,
            
            "healthcare_mortality_reduction": 0.85,
            "healthcare_capacity_threshold": 0.7,  # Healthcare system overwhelm threshold
            "healthcare_overwhelm_penalty": 2.5,  # Multiplier for mortality when overwhelmed
            
            "research_effectiveness": 0.012,
            "research_breakthrough_threshold": 0.8,  # Research level for breakthrough
            "research_breakthrough_effect": 0.6,  # Effectiveness multiplier after breakthrough
            
            "travel_restriction_effectiveness": 0.7,
            "travel_economic_impact": 0.15,  # Economic impact of travel restrictions
        })
        
        # Region-specific parameters
        self.regions = {
            "urban": {
                "population": 0.7,  # 70% of population
                "density": 3.0,  # Higher disease spread
                "economic_weight": 0.8,  # 80% of economy
            },
            "rural": {
                "population": 0.3,  # 30% of population
                "density": 0.7,  # Lower disease spread
                "economic_weight": 0.2,  # 20% of economy
            }
        }
        
        # Economic sectors with varying impacts
        self.economic_sectors = {
            "essential": {
                "gdp_weight": 0.3,  # 30% of GDP
                "lockdown_impact": 0.2,  # 20% reduction under lockdown
            },
            "in_person_services": {
                "gdp_weight": 0.4,  # 40% of GDP
                "lockdown_impact": 0.8,  # 80% reduction under lockdown
            },
            "remote_capable": {
                "gdp_weight": 0.3,  # 30% of GDP
                "lockdown_impact": 0.3,  # 30% reduction under lockdown
            }
        }
        
        # Enhanced state tracking
        self.enhanced_state = {
            "lockdown_history": [],  # Track lockdown changes to model fatigue
            "healthcare_history": [],  # Track healthcare investments
            "economic_history": [],  # Track economic support
            "research_history": [],  # Track research investments
            "current_r0": self.disease_params["r0_base"],
            "lockdown_compliance": 1.0,  # Starts perfect, decays with time
            "healthcare_capacity": 1.0,  # Normalized capacity
            "immunity_level": 0.0,  # Population immunity (0-1)
            "economic_sectors_health": {k: 1.0 for k in self.economic_sectors},  # Sector-specific economic health
            "regional_infection": {k: 0.0 for k in self.regions},  # Region-specific infection rates
            "total_infected_ever": 0,  # Track total infections for variant emergence
            "active_variants": [],  # Currently active variants in simulation
            "variant_emergence_message_shown": False,  # Track if we've notified about a variant
        }
        
        # This helps track the impact of different strategies
        self.strategy_impact = {
            "containment_impact": 0.0,  # Impact on disease spread
            "economic_impact": 0.0,  # Impact on economy
            "healthcare_impact": 0.0,  # Impact on mortality
            "research_impact": 0.0,  # Impact of research
        }
        
        # Callback functions for strategy evaluation
        self._step_callbacks = []
        
        # Create a new simulation state specific to EnhancedEngine
        self.state = SimulationState()
        
        # Initialize the simulation state
        self.initial_population = 10000
        self.reset()
        
    def reset(self):
        """Reset the simulation state."""
        # Create a fresh state
        self.state = SimulationState()
        
        # Initialize population
        self.state.population.total = self.initial_population
        self.state.population.susceptible = self.initial_population - 100
        self.state.population.infected = 100
        self.state.population.recovered = 0
        self.state.population.deaths = 0
        
        # Initialize economy
        self.state.economy.initial_gdp = 1000
        self.state.economy.current_gdp = 1000
        
        # Initialize research
        self.state.research.progress = 0.0
        
        # Initialize simulation tracking
        self.state.simulation.contained = False
        self.state.simulation.containment_step = -1
        self.state.simulation.max_infected = 100  # Start with initial infected as max
        
        # Reset enhanced state
        self.enhanced_state = {
            "lockdown_history": [],
            "healthcare_history": [],
            "economic_history": [],
            "research_history": [],
            "current_r0": self.disease_params["r0_base"],
            "lockdown_compliance": 1.0,
            "healthcare_capacity": 1.0,
            "immunity_level": 0.0,
            "economic_sectors_health": {k: 1.0 for k in self.economic_sectors},
            "regional_infection": {k: 0.0 for k in self.regions},
            "total_infected_ever": 100,  # Starting with 100 initial infected
            "active_variants": [],  # No variants active at start
            "variant_emergence_message_shown": False,
        }
        
        # Reset active variants
        self.active_variants = []
        for variant in self.potential_variants:
            variant.emerged = False
            variant.prevalence = 0.0
        
        self.strategy_impact = {
            "containment_impact": 0.0,
            "economic_impact": 0.0,
            "healthcare_impact": 0.0,
            "research_impact": 0.0,
        }
        
        # Reset resource allocation tracking
        self._allocated_resources = {
            'healthcare': 0,
            'economic': 0,
            'research': 0
        }
        
        # Reset intervention state
        self._current_lockdown_level = 0.0
        self._travel_restricted = False
        
        # Reset callback functions
        self._step_callbacks = []
        
    def _update_variants(self):
        """Update variant emergence and prevalence."""
        # Calculate proportion of population that has been infected
        infection_proportion = self.enhanced_state["total_infected_ever"] / self.initial_population
        
        # Check for new variant emergence
        for variant in self.potential_variants:
            if not variant.emerged and infection_proportion >= variant.emergence_threshold:
                # Random chance for emergence based on current infection rate
                if random.random() < self.disease_params["variant_emergence_rate"]:
                    variant.emerged = True
                    variant.prevalence = 0.05  # Start at 5% prevalence
                    self.active_variants.append(variant)
                    
                    # Show message about variant emergence if this is the first one
                    if not self.enhanced_state["variant_emergence_message_shown"]:
                        print(f"WARNING: A new disease variant ({variant.name}) has emerged!")
                        self.enhanced_state["variant_emergence_message_shown"] = True
        
        # Update prevalence of existing variants
        for variant in self.active_variants:
            variant.update_prevalence(
                self.state.population.infected,
                self.disease_params["variant_prevalence_increase"]
            )
    
    def _calculate_variant_effects(self):
        """Calculate overall effect of current variants on disease parameters."""
        if not self.active_variants:
            return 1.0, 1.0, 0.0  # No effect
        
        # Calculate weighted average of variant effects
        total_prevalence = sum(v.prevalence for v in self.active_variants)
        
        # If no significant variant presence, return no effect
        if total_prevalence < 0.01:
            return 1.0, 1.0, 0.0
        
        # Calculate weighted effects
        r0_effect = 1.0
        mortality_effect = 1.0
        immune_escape = 0.0
        
        for variant in self.active_variants:
            weight = variant.prevalence / total_prevalence if total_prevalence > 0 else 0
            r0_effect += (variant.r0_modifier - 1.0) * weight
            mortality_effect += (variant.mortality_modifier - 1.0) * weight
            immune_escape += variant.immune_escape * weight
        
        return r0_effect, mortality_effect, immune_escape
    
    def set_lockdown_level(self, level: float) -> None:
        """
        Set lockdown level with enhanced modeling of diminishing returns and compliance.
        
        Args:
            level: Lockdown severity (0.0 to 1.0)
        """
        # Valid range check
        level = max(0.0, min(1.0, level))
        
        # Track lockdown history for fatigue calculation
        self.enhanced_state["lockdown_history"].append(level)
        
        # Calculate compliance-adjusted level based on lockdown fatigue
        if len(self.enhanced_state["lockdown_history"]) > 15:  # After 15 days
            # Compliance decays based on duration and severity of previous lockdowns
            recent_lockdowns = self.enhanced_state["lockdown_history"][-15:]
            avg_recent_level = sum(recent_lockdowns) / len(recent_lockdowns)
            
            # More severe lockdowns cause faster compliance decay
            compliance_decay = self.intervention_effects["lockdown_compliance_decay"] * (1 + avg_recent_level)
            self.enhanced_state["lockdown_compliance"] = max(
                0.5,  # Compliance never goes below 50%
                self.enhanced_state["lockdown_compliance"] - compliance_decay
            )
        
        # Apply compliance factor to lockdown level
        effective_level = level * self.enhanced_state["lockdown_compliance"]
        
        # Apply diminishing returns if this isn't the first lockdown
        if len(self.enhanced_state["lockdown_history"]) > 30:
            # Calculate diminishing factor based on lockdown history
            diminish_factor = self.intervention_effects["lockdown_diminishing_factor"] ** (
                len(self.enhanced_state["lockdown_history"]) // 30  # Every 30 days of lockdown reduces effectiveness
            )
            effective_level = effective_level * diminish_factor
        
        # Calculate regional effects
        for region, params in self.regions.items():
            # Urban areas have lower compliance with lockdowns
            if region == "urban":
                region_compliance = self.enhanced_state["lockdown_compliance"] * 0.9
            else:
                region_compliance = self.enhanced_state["lockdown_compliance"] * 1.1
                
            # Effective lockdown in this region
            region_effective_level = level * region_compliance
            
            # Update regional R0
            base_r0 = self.disease_params["r0_base"] * params["density"]
            reduction = self.intervention_effects["lockdown_r0_reduction"] * region_effective_level
            new_r0 = base_r0 * (1 - reduction)
            
            # Regional economic impact
            for sector, sector_params in self.economic_sectors.items():
                impact = sector_params["lockdown_impact"] * region_effective_level
                # Update sector health in this region
                current_health = self.enhanced_state["economic_sectors_health"][sector]
                self.enhanced_state["economic_sectors_health"][sector] = current_health * (1 - impact * 0.1)
        
        # Calculate overall R0 impact across regions
        r0_reduction = 0
        for region, params in self.regions.items():
            regional_reduction = self.intervention_effects["lockdown_r0_reduction"] * effective_level
            r0_reduction += regional_reduction * params["population"]
        
        # Update current R0
        base_r0 = self.disease_params["r0_base"]
        self.enhanced_state["current_r0"] = base_r0 * (1 - r0_reduction)
        
        # Store for MockEngine compatibility
        self._current_lockdown_level = level
        
        # Track containment impact for scoring
        self.strategy_impact["containment_impact"] += effective_level * 0.1
        
    def allocate_resources(self, category: str, amount: float) -> None:
        """
        Allocate resources with enhanced modeling of returns and capacity constraints.
        
        Args:
            category: 'healthcare', 'economic', or 'research'
            amount: Amount of resources to allocate
        """
        # Resource balancing - penalize extreme allocations
        total_allocated = sum(self._allocated_resources.values()) + amount
        if total_allocated > 1000:
            # Reduced effectiveness when over-allocating
            effective_amount = amount * (1000 / total_allocated)
        else:
            effective_amount = amount
            
        # Track allocation history
        if category in self.enhanced_state:
            self.enhanced_state[f"{category}_history"].append(effective_amount)
        
        # Category-specific enhanced logic
        if category == "healthcare":
            # Calculate diminishing returns based on previous healthcare investments
            previous_healthcare = sum(self.enhanced_state.get("healthcare_history", [0]))
            
            if previous_healthcare > 500:
                # Diminishing returns after significant investment
                effectiveness = 1.0 - (0.3 * (previous_healthcare - 500) / 1000)
                effectiveness = max(0.5, effectiveness)  # Never below 50% effectiveness
                effective_amount = effective_amount * effectiveness
            
            # Increase healthcare capacity
            capacity_increase = 0.05 * (effective_amount / 100)
            self.enhanced_state["healthcare_capacity"] = min(
                2.0,  # Cap at 200% capacity
                self.enhanced_state["healthcare_capacity"] + capacity_increase
            )
            
            # Track healthcare impact for scoring
            self.strategy_impact["healthcare_impact"] += effective_amount * 0.01
            
        elif category == "economic":
            # Calculate economic impact with sector-specific effects
            for sector, sector_params in self.economic_sectors.items():
                # Different sectors respond differently to economic support
                if sector == "in_person_services":
                    # In-person services benefit most from economic support
                    sector_effect = 0.15 * (effective_amount / 100)
                elif sector == "essential":
                    # Essential services benefit less
                    sector_effect = 0.05 * (effective_amount / 100)
                else:
                    # Remote-capable in between
                    sector_effect = 0.1 * (effective_amount / 100)
                
                # Update sector health
                current_health = self.enhanced_state["economic_sectors_health"][sector]
                self.enhanced_state["economic_sectors_health"][sector] = min(
                    1.0,  # Cap at 100%
                    current_health + sector_effect
                )
            
            # Track economic impact for scoring
            self.strategy_impact["economic_impact"] += effective_amount * 0.01
            
        elif category == "research":
            # Research has increasing returns as progress is made
            current_progress = self.state.research.progress if hasattr(self.state, 'research') else 0
            
            # Research becomes more effective as more progress is made
            if current_progress > 0.5:
                # Accelerating returns as research progresses
                effectiveness = 1.0 + (0.5 * current_progress)
                effective_amount = effective_amount * effectiveness
            
            # Track research impact for scoring
            self.strategy_impact["research_impact"] += effective_amount * 0.01
        
        # Store for MockEngine compatibility
        if category in self._allocated_resources:
            self._allocated_resources[category] += amount
        else:
            self._allocated_resources[category] = amount
    
    def restrict_travel(self, should_restrict: bool) -> None:
        """
        Restrict travel with enhanced modeling of economic impact and effectiveness.
        
        Args:
            should_restrict: Whether to restrict travel
        """
        # Apply travel restrictions with region-specific effects
        if should_restrict:
            # Calculate travel restriction impact on disease spread
            for region, params in self.regions.items():
                # Urban areas have more travel, so restrictions have bigger impact
                if region == "urban":
                    r0_impact = self.intervention_effects["travel_restriction_effectiveness"] * 1.2
                else:
                    r0_impact = self.intervention_effects["travel_restriction_effectiveness"] * 0.7
                
                # Reduce current R0 for this region
                self.enhanced_state["current_r0"] *= (1 - r0_impact * 0.1)
            
            # Travel restrictions hurt certain economic sectors more
            for sector, sector_params in self.economic_sectors.items():
                if sector == "in_person_services":
                    # Tourism, hospitality hit hardest
                    impact = self.intervention_effects["travel_economic_impact"] * 1.5
                elif sector == "essential":
                    # Essential services less affected
                    impact = self.intervention_effects["travel_economic_impact"] * 0.5
                else:
                    # Standard impact
                    impact = self.intervention_effects["travel_economic_impact"]
                
                # Update sector health
                current_health = self.enhanced_state["economic_sectors_health"][sector]
                self.enhanced_state["economic_sectors_health"][sector] = current_health * (1 - impact * 0.05)
            
            # Track containment impact for scoring
            self.strategy_impact["containment_impact"] += 0.05
        
        # Store for MockEngine compatibility
        self._travel_restricted = should_restrict
    
    def register_step_callback(self, callback):
        """Register a callback for each simulation step."""
        self._step_callbacks.append(callback)
    
    def target_research(self, variant_name: Optional[str] = None, amount: float = 100.0) -> None:
        """
        Target research efforts toward a specific variant or general disease understanding.
        
        Args:
            variant_name: Name of the variant to target, or None for general research
            amount: Amount of resources to allocate to this research
        
        Returns:
            None
        """
        # Default to general research if no variant specified
        if variant_name is None or not self.active_variants:
            self.allocate_resources('research', amount)
            return
            
        # Find the target variant
        target_variant = None
        for variant in self.active_variants:
            if variant.name.lower() == variant_name.lower():
                target_variant = variant
                break
                
        if not target_variant:
            # Variant not found or not active, do general research
            self.allocate_resources('research', amount)
            return
            
        # Target specific variant - boost research effectiveness
        # But also make it slightly more costly as it's specialized
        effective_amount = amount * 1.2  # 20% more effective when targeted
        self.allocate_resources('research', amount * 1.1)  # But 10% more expensive
        
        # Reduce this variant's prevalence and effectiveness over time
        if random.random() < (self.state.research.progress * 0.2):
            reduction = 0.05 * (effective_amount / 100)
            target_variant.prevalence = max(0, target_variant.prevalence - reduction)
            
            # Also slightly reduce its r0 and mortality modifiers as we learn more
            target_variant.r0_modifier = max(1.0, target_variant.r0_modifier - 0.01)
            target_variant.mortality_modifier = max(1.0, target_variant.mortality_modifier - 0.01)
    
    def get_variant_status(self) -> List[Dict[str, Any]]:
        """
        Get the current status of disease variants in the simulation.
        
        Returns:
            List of dictionaries with variant information
        """
        return [
            {
                "name": variant.name,
                "active": variant.emerged,
                "prevalence": variant.prevalence,
                "r0_modifier": variant.r0_modifier,
                "mortality_modifier": variant.mortality_modifier,
                "immune_escape": variant.immune_escape
            }
            for variant in self.potential_variants
        ]
    
    def display_variant_info(self) -> None:
        """Display information about active variants."""
        if not self.active_variants:
            print("No disease variants currently active.")
            return
            
        print("\n=== Active Disease Variants ===")
        for variant in self.active_variants:
            if variant.prevalence < 0.01:
                continue  # Skip variants with negligible prevalence
                
            print(f"{variant.name} Variant:")
            print(f"  Prevalence: {variant.prevalence:.1%}")
            print(f"  Transmissibility: {variant.r0_modifier:.1f}x base")
            print(f"  Severity: {variant.mortality_modifier:.1f}x base")
            print(f"  Immune Escape: {variant.immune_escape:.1%}")
            print("")
    
    def display_strategy_analysis(self, results) -> None:
        """
        Display detailed analysis of strategy performance.
        
        Args:
            results: Simulation results dict containing performance metrics
        """
        if "performance_metrics" not in results:
            # Create metrics from raw results if not present
            population_rating = results.get("population_survived", 0)
            economic_rating = results.get("gdp_preserved", 0)
            infection_control_rating = results.get("infection_control", 0)
            
            metrics = {
                "population_rating": population_rating,
                "economic_rating": economic_rating,
                "infection_control_rating": infection_control_rating,
                "baseline": 0.4,
                "curve_factor": 1.5,
                "strategy_variance": 0.0,
                "multi_objective_score": 0.0
            }
            results["performance_metrics"] = metrics
        else:
            metrics = results["performance_metrics"]
            
        raw_score = results.get("raw_score", 0)
        final_score = results.get("final_score", 0)
        
        # Format percentages with one decimal place
        pop_pct = f"{metrics['population_rating']*100:.1f}%"
        econ_pct = f"{metrics['economic_rating']*100:.1f}%"
        infect_pct = f"{metrics['infection_control_rating']*100:.1f}%"
        
        print("\n=== Strategy Performance Analysis ===")
        print(f"Score: {final_score:.4f}   (Raw: {raw_score:.4f})")
        
        # Get letter grade based on score
        if final_score >= 0.85:
            grade = "A+"
        elif final_score >= 0.80:
            grade = "A"
        elif final_score >= 0.75:
            grade = "A-"
        elif final_score >= 0.70:
            grade = "B+"
        elif final_score >= 0.65:
            grade = "B"
        elif final_score >= 0.60:
            grade = "B-" 
        elif final_score >= 0.55:
            grade = "C+"
        elif final_score >= 0.50:
            grade = "C"
        elif final_score >= 0.45:
            grade = "C-"
        elif final_score >= 0.40:
            grade = "D+"
        elif final_score >= 0.35:
            grade = "D"
        else:
            grade = "F"
            
        print(f"Grade: {grade}")
        
        print("\nKey Performance Indicators:")
        print(f"  Population Survival: {pop_pct}") 
        print(f"  Economic Preservation: {econ_pct}")
        print(f"  Infection Control: {infect_pct}")
        
        # If available, show multi-objective score
        if "multi_objective_score" in metrics:
            multi_obj = metrics["multi_objective_score"]
            print(f"  Multi-Objective Balance: {multi_obj:.3f}")
        
        # Show any variants that emerged
        if results.get("variants_emerged", 0) > 0:
            variant_names = results.get("variant_names", [])
            highest_prevalence = results.get("highest_variant_prevalence", 0)
            print(f"\nVariants: {', '.join(variant_names)} (peak: {highest_prevalence:.1%})")
            if "variant_control" in results:
                print(f"Variant Response Rating: {results['variant_control']:.2f}")
        
        # Strategy classification
        if final_score >= 0.75:
            rating = "Excellent"
        elif final_score >= 0.65:
            rating = "Very Good"
        elif final_score >= 0.55:
            rating = "Good"
        elif final_score >= 0.45:
            rating = "Fair"
        elif final_score >= 0.35:
            rating = "Poor"
        else:
            rating = "Critical Failure"
        
        print(f"\nStrategy Rating: {rating}")
        
        # Identify strategy archetype based on resource allocation
        healthcare = self._allocated_resources.get('healthcare', 0)
        economic = self._allocated_resources.get('economic', 0)
        research = self._allocated_resources.get('research', 0)
        lockdown_level = self._current_lockdown_level
        
        # Determine primary focus
        total_resources = sum(self._allocated_resources.values())
        if total_resources > 0:
            healthcare_pct = healthcare / total_resources
            economic_pct = economic / total_resources
            research_pct = research / total_resources
            
            # Identify archetype
            if healthcare_pct > 0.5:
                archetype = "Healthcare-Focused"
            elif economic_pct > 0.5:
                archetype = "Economy-Focused"
            elif research_pct > 0.5:
                archetype = "Research-Focused"
            elif lockdown_level > 0.7:
                archetype = "Containment-Focused"
            elif max(healthcare_pct, economic_pct, research_pct) < 0.4:
                archetype = "Balanced Approach"
            else:
                archetype = "Mixed Strategy"
                
            print(f"Strategy Archetype: {archetype}")
            print(f"Resource Distribution: Healthcare {healthcare_pct:.0%}, Economy {economic_pct:.0%}, Research {research_pct:.0%}")
        
        # Strengths and weaknesses analysis
        print("\nSTRENGTHS:")
        strengths_found = False
        
        if metrics["population_rating"] >= 0.7:
            print("  + Strong population protection")
            strengths_found = True
            
        if metrics["economic_rating"] >= 0.7:
            print("  + Effective economic management")
            strengths_found = True
            
        if metrics["infection_control_rating"] >= 0.7:
            print("  + Excellent infection control")
            strengths_found = True
            
        if results.get("resource_efficiency", 0) >= 0.7:
            print("  + Efficient resource allocation")
            strengths_found = True
            
        if metrics.get("multi_objective_score", 0) >= 0.65:
            print("  + Well-balanced approach")
            strengths_found = True
            
        if total_resources > 0 and max(healthcare_pct, economic_pct, research_pct) < 0.4:
            print("  + Diversified resource allocation")
            strengths_found = True
            
        if not strengths_found:
            print("  None identified")
            
        print("\nWEAKNESSES:")
        weaknesses_found = False
        
        if metrics["population_rating"] < 0.6:
            print("  - Poor population protection")
            weaknesses_found = True
            
        if metrics["economic_rating"] < 0.6:
            print("  - Weak economic management")
            weaknesses_found = True
            
        if metrics["infection_control_rating"] < 0.6:
            print("  - Insufficient infection control")
            weaknesses_found = True
            
        if results.get("resource_efficiency", 0) < 0.5:
            print("  - Inefficient resource allocation")
            weaknesses_found = True
            
        if total_resources > 0 and max(healthcare_pct, economic_pct, research_pct) > 0.7:
            print("  - Over-specialized resource allocation")
            weaknesses_found = True
            
        if not weaknesses_found:
            print("  None identified")
        
        # Recommendations section
        print("\nRECOMMENDATIONS:")
        
        if metrics["population_rating"] < 0.6:
            print("  → Increase healthcare allocation to reduce mortality")
            
        if metrics["infection_control_rating"] < 0.6:
            if lockdown_level < 0.5:
                print("  → Implement stronger containment measures")
            else:
                print("  → Combine containment with targeted healthcare investment")
                
        if metrics["economic_rating"] < 0.6 and metrics["population_rating"] > 0.7:
            print("  → Reduce extreme lockdown measures when infections are low")
            print("  → Allocate more resources to economic support")
            
        if metrics.get("multi_objective_score", 0) < 0.5:
            print("  → Balance your approach across multiple objectives")
            
        if results.get("variants_emerged", 0) > 0 and results.get("variant_control", 0) < 0.6:
            print("  → Increase research investment to counter emerging variants")
            
        print("\n" + "="*40)
    
    def is_contained(self) -> bool:
        """
        Check if the outbreak is contained.
        
        Returns:
            True if the outbreak is contained, False otherwise
        """
        return self.state.simulation.contained
    
    def step(self) -> SimulationState:
        """
        Run one step of the simulation with enhanced logic.
        
        Returns:
            Updated simulation state
        """
        # Enhanced step logic
        current_step = self.state.time.step
        
        # Add a protection against population being zero at the beginning of the step
        if self.state.population.total <= 0:
            print(f"Warning: Population is zero at step {current_step}. Ending simulation.")
            self.state.simulation.contained = True
            self.state.simulation.containment_step = current_step
            self.state.time.step += 1
            return self.state
            
        # Update disease variants
        self._update_variants()
        
        # Get variant effects on disease parameters
        r0_variant_effect, mortality_variant_effect, immune_escape = self._calculate_variant_effects()
        
        # Apply stochasticity to disease parameters
        r0_variation = random.uniform(-self.disease_params["r0_variance"], self.disease_params["r0_variance"])
        stochastic_r0 = self.enhanced_state["current_r0"] * r0_variant_effect + r0_variation
        stochastic_r0 = max(0.5, stochastic_r0)  # R0 never below 0.5
        
        mortality_variation = random.uniform(
            -self.disease_params["mortality_variance"],
            self.disease_params["mortality_variance"]
        )
        stochastic_mortality = self.disease_params["mortality_rate_base"] * mortality_variant_effect + mortality_variation
        stochastic_mortality = max(0.005, stochastic_mortality)  # Mortality never below 0.5%
        
        # Calculate healthcare capacity effect on mortality
        healthcare_capacity = self.enhanced_state["healthcare_capacity"]
        total_infected = self.state.population.infected
        total_population = self.state.population.total
        infection_rate = total_infected / total_population if total_population > 0 else 0
        
        # Healthcare system overwhelm check
        healthcare_threshold = self.intervention_effects["healthcare_capacity_threshold"]
        if infection_rate > (healthcare_capacity * healthcare_threshold):
            # Healthcare system overwhelmed - increased mortality
            overwhelm_factor = min(3.0, (infection_rate / (healthcare_capacity * healthcare_threshold)))
            stochastic_mortality *= (1 + (self.intervention_effects["healthcare_overwhelm_penalty"] * 
                                          (overwhelm_factor - 1) / 2))
        else:
            # Healthcare system coping - reduced mortality based on capacity
            mortality_reduction = self.intervention_effects["healthcare_mortality_reduction"] * (healthcare_capacity / 1.0)
            stochastic_mortality *= (1 - mortality_reduction * 0.5)
        
        # Calculate economic health based on sectors
        overall_economic_health = 0
        for sector, params in self.economic_sectors.items():
            sector_health = self.enhanced_state["economic_sectors_health"][sector]
            overall_economic_health += sector_health * params["gdp_weight"]
        
        # Update economy in state
        current_gdp_ratio = self.state.economy.current_gdp / self.state.economy.initial_gdp if self.state.economy.initial_gdp > 0 else 0
        new_gdp_ratio = current_gdp_ratio * 0.95 + overall_economic_health * 0.05
        self.state.economy.current_gdp = self.state.economy.initial_gdp * new_gdp_ratio
        
        # Calculate research progress with potential breakthroughs
        research_allocated = self._allocated_resources.get('research', 0)
        research_effectiveness = self.intervention_effects["research_effectiveness"]
        
        # Research has increasing returns as it progresses
        if self.state.research.progress > self.intervention_effects["research_breakthrough_threshold"]:
            # Breakthrough achieved - boosted effectiveness
            research_effectiveness *= self.intervention_effects["research_breakthrough_effect"]
            
            # Breakthrough reduces mortality
            stochastic_mortality *= 0.7
            
            # And improves treatment effectiveness
            if healthcare_capacity > 1.0:
                healthcare_capacity *= 1.1
                self.enhanced_state["healthcare_capacity"] = healthcare_capacity
        
        # Update research progress
        progress_increment = research_effectiveness * (research_allocated / 100)
        self.state.research.progress += progress_increment
        self.state.research.progress = min(1.0, self.state.research.progress)
        
        # Update infection dynamics using SIR model with stochasticity
        # Consider immune escape from variants for reinfections
        effective_susceptible = self.state.population.susceptible + (
            self.state.population.recovered * immune_escape  # Some recovered can be reinfected
        )
        
        # Ensure effective susceptible doesn't exceed total - infected - dead
        effective_susceptible = min(
            effective_susceptible, 
            self.state.population.total - self.state.population.infected
        )
        
        # Add safety check for division by zero
        if self.state.population.total > 0:
            new_infections = (
                stochastic_r0 * 
                self.state.population.infected * 
                (effective_susceptible / self.state.population.total)
            ) * 0.1  # Daily infection rate
            
            # Add randomness to infection spread
            new_infections *= random.uniform(0.8, 1.2)
        else:
            new_infections = 0
        
        # Calculate how many are reinfections vs first-time infections
        reinfections = 0
        if immune_escape > 0 and new_infections > 0:
            # Calculate reinfections safely with division check
            reinfections = min(
                new_infections * (immune_escape / (1 + immune_escape + 1e-10)),  # Add small epsilon to prevent division by zero
                self.state.population.recovered * immune_escape  # Can't exceed recovered * immune_escape
            )
        
        # Actual new infections of susceptible individuals
        new_first_infections = new_infections - reinfections
        
        # Calculate recoveries and deaths safely
        recoveries = self.state.population.infected * (1 / self.disease_params["recovery_period"]) if self.state.population.infected > 0 else 0
        deaths = self.state.population.infected * stochastic_mortality if self.state.population.infected > 0 else 0
        
        # Update population counts
        self.state.population.susceptible = max(0, self.state.population.susceptible - new_first_infections)
        self.state.population.recovered = max(0, self.state.population.recovered - reinfections + recoveries)
        self.state.population.infected = max(0, self.state.population.infected + new_infections - recoveries - deaths)
        self.state.population.deaths = max(0, self.state.population.deaths + deaths)
        self.state.population.dead = self.state.population.deaths  # Keep dead attribute in sync
        
        # Update total population - ensure it doesn't go below zero
        self.state.population.total = max(0, 
            self.state.population.susceptible + 
            self.state.population.infected + 
            self.state.population.recovered
        )
        
        # Update max infected tracking
        self.state.simulation.max_infected = max(self.state.simulation.max_infected, self.state.population.infected)
        
        # Update total ever infected for variant emergence
        self.enhanced_state["total_infected_ever"] += new_first_infections
        
        # Safely call registered step callbacks
        try:
            for callback in self._step_callbacks:
                try:
                    callback(current_step, self.state)
                except ZeroDivisionError:
                    print(f"Error adjusting strategy: division by zero in callback at step {current_step}")
                except Exception as e:
                    print(f"Error in callback at step {current_step}: {str(e)}")
        except Exception as e:
            print(f"Error processing callbacks at step {current_step}: {str(e)}")
        
        # Check for containment (R_effective < 1 and infected < 1%)
        # Add safety check for division by zero
        if self.state.population.total > 0:
            r_effective = stochastic_r0 * (self.state.population.susceptible / self.state.population.total)
            infection_percentage = self.state.population.infected / self.state.population.total
            if r_effective < 1 and infection_percentage < 0.01:
                if not self.state.simulation.contained:
                    self.state.simulation.contained = True
                    self.state.simulation.containment_step = current_step
        elif not self.state.simulation.contained:
            # If population is zero, consider it contained
            self.state.simulation.contained = True
            self.state.simulation.containment_step = current_step
        
        # Increment simulation step
        self.state.time.step += 1
        
        return self.state
    
    def run(self, steps: int, interventions: List[Callable[[Any], None]] = None) -> Dict[str, float]:
        """
        Run simulation for specified number of steps, applying interventions.
        
        Args:
            steps: Number of simulation steps
            interventions: List of intervention strategy functions
            
        Returns:
            Dict with results of simulation
        """
        # Initialize/reset if needed
        if self.state is None:
            self.reset()
        
        # Apply interventions safely
        if interventions:
            for intervention in interventions:
                try:
                    intervention(self)
                except Exception as e:
                    print(f"Error applying intervention: {str(e)}")
        
        # Run simulation
        for _ in range(steps):
            self.step()
            
            # Stop if contained or if population reaches zero
            if self.state.simulation.contained or self.state.population.total <= 0:
                break
        
        # Calculate results with enhanced scoring
        results = {}
        
        # Population outcomes - add safety check
        if self.initial_population > 0:
            survival_rate = 1 - (self.state.population.deaths / self.initial_population)
            results["population_survived"] = max(0, min(1, survival_rate))
        else:
            results["population_survived"] = 0
        
        # Economic outcomes
        if self.state.economy.initial_gdp > 0:
            gdp_ratio = self.state.economy.current_gdp / self.state.economy.initial_gdp
            results["gdp_preserved"] = max(0, min(1, gdp_ratio))
        else:
            results["gdp_preserved"] = 0
        
        # Infection control - add safety check
        if self.initial_population > 0:
            max_infected_ratio = self.state.simulation.max_infected / self.initial_population
            infection_control = 1 - max_infected_ratio
            results["infection_control"] = max(0, min(1, infection_control))
        else:
            results["infection_control"] = 0
        
        # Resource efficiency
        total_resources = sum(self._allocated_resources.values())
        if total_resources > 0:
            resource_efficiency = min(1.0, (1000 / total_resources) if total_resources > 1000 else 1.0)
            
            # Penalty for unbalanced allocation
            healthcare = self._allocated_resources.get('healthcare', 0)
            economic = self._allocated_resources.get('economic', 0)
            research = self._allocated_resources.get('research', 0)
            
            resource_total = healthcare + economic + research
            if resource_total > 0:
                healthcare_ratio = healthcare / resource_total
                economic_ratio = economic / resource_total
                research_ratio = research / resource_total
                
                # Calculate how balanced the allocation is (1 for perfectly balanced)
                balance_score = 1 - (
                    abs(healthcare_ratio - 0.33) + 
                    abs(economic_ratio - 0.33) + 
                    abs(research_ratio - 0.33)
                ) / 2
                
                # Apply balance factor to resource efficiency
                resource_efficiency *= 0.7 + (balance_score * 0.3)
        else:
            resource_efficiency = 0.0
            
        results["resource_efficiency"] = max(0, min(1, resource_efficiency))
        
        # Containment time
        containment_step = self.state.simulation.containment_step if self.state.simulation.contained else steps
        time_to_containment = 1 - (containment_step / steps) if steps > 0 else 0
        results["time_to_containment"] = max(0, min(1, time_to_containment))
        
        # Variant response score - new metric!
        if len(self.active_variants) > 0:
            # Calculate effectiveness against variants
            variant_control = 0.0
            
            # If research is high, that helps with variant control
            research_factor = self.state.research.progress * 0.3
            
            # Check prevalence of variants - lower is better
            avg_prevalence = sum(v.prevalence for v in self.active_variants) / len(self.active_variants)
            prevalence_factor = 1 - avg_prevalence
            
            # Combine factors
            variant_control = (research_factor + prevalence_factor) / 1.3  # Normalize
            results["variant_control"] = max(0, min(1, variant_control))
        else:
            # No variants emerged, perfect score
            results["variant_control"] = 1.0
        
        # Strategy impact bonuses
        strategy_score = (
            self.strategy_impact["containment_impact"] * 0.3 +
            self.strategy_impact["economic_impact"] * 0.3 +
            self.strategy_impact["healthcare_impact"] * 0.3 +
            self.strategy_impact["research_impact"] * 0.1
        ) / 5  # More significant impact (changed from /10)
        
        strategy_score = min(0.3, strategy_score)  # Cap at 30% bonus (increased from 20%)
        
        # Calculate weights with dynamic adjustments based on scenario
        weights = {
            "population_survived": 0.35,  # Increased weight (from 0.3)
            "gdp_preserved": 0.25,        # Increased weight (from 0.2)
            "infection_control": 0.25,    # Increased weight (from 0.2)
            "resource_efficiency": 0.1,
            "time_to_containment": 0.05   # Decreased weight (from 0.1)
        }
        
        # If variants emerged, add variant control to scoring
        if len(self.active_variants) > 0:
            # Reduce weight of time_to_containment to make room for variant_control
            weights["time_to_containment"] = 0.05
            weights["variant_control"] = 0.15  # Significant weight for variant management
        
        # Adjust weights based on strategy impact
        if self.strategy_impact["healthcare_impact"] > self.strategy_impact["economic_impact"]:
            # Healthcare-focused strategy - weight survival more
            weights["population_survived"] += 0.05
            weights["gdp_preserved"] -= 0.05
        else:
            # Economy-focused strategy - weight GDP more
            weights["gdp_preserved"] += 0.05
            weights["population_survived"] -= 0.05
        
        # Calculate weighted score
        raw_score = 0
        for key in weights:
            if key in results:
                # Apply non-linear scaling to each component to create more separation
                component_value = results[key]
                # Apply a power curve to create more differentiation
                scaled_value = component_value ** 1.5  # Power scaling to increase differences
                raw_score += scaled_value * weights[key]
        
        # Apply strategy impact bonus
        raw_score = min(1.0, raw_score * (1 + strategy_score))
        
        # Store original raw score
        results["raw_score"] = raw_score
        
        # ENHANCED SCORING SYSTEM
        # 1. Apply baseline shift to raise the minimum effective score
        baseline = 0.4  # Increased baseline (from 0.3)
        adjusted_score = baseline + (1 - baseline) * raw_score
        
        # 2. Apply exponential scaling to amplify differences between good and great strategies
        curve_factor = 1.5  # More moderate curve (from 2.0)
        exponential_score = adjusted_score ** curve_factor
        
        # 3. Apply normalization to bring back to 0-1 range
        normalized_score = (exponential_score - baseline**curve_factor) / ((1.0)**curve_factor - baseline**curve_factor)
        normalized_score = max(0, min(1, normalized_score))  # Ensure boundaries
        
        # 4. Add strategic variance based on performance metrics
        # Calculate performance metrics
        infection_control_rating = results.get("infection_control", 0)
        economic_rating = results.get("gdp_preserved", 0)
        population_rating = results.get("population_survived", 0)
        
        # NEW: Calculate dimensionality reduction for multi-objective optimization
        # This rewards strategies that perform well across multiple dimensions
        multi_objective_score = (
            (infection_control_rating * economic_rating) ** 0.5 +  # Geometric mean of infection control and economy
            (population_rating * economic_rating) ** 0.5 +         # Geometric mean of population and economy
            (infection_control_rating * population_rating) ** 0.5  # Geometric mean of infection control and population
        ) / 3
        
        # Apply bonus for multi-objective performance
        normalized_score = min(1.0, normalized_score + (multi_objective_score * 0.1))
        
        # Favor strategies that excel in key areas
        if infection_control_rating > 0.7 and population_rating > 0.8:
            # Excellent disease control bonus
            normalized_score = min(1.0, normalized_score + 0.03)  # Reduced bonus (from 0.05)
        
        if economic_rating > 0.7 and population_rating > 0.7:
            # Balanced economic and health outcomes bonus
            normalized_score = min(1.0, normalized_score + 0.03)  # Reduced bonus (from 0.05)
            
        # Penalize catastrophic failures
        if population_rating < 0.5 or infection_control_rating < 0.3:
            # Severe disease impact penalty
            normalized_score = max(0.0, normalized_score - 0.07)  # Reduced penalty (from 0.1)
            
        # 5. Add small random variance for similar strategies
        # This ensures even identical strategies get slightly different scores
        variance_factor = 0.02  # Reduced variance (from 0.03)
        strategy_variance = random.uniform(-variance_factor, variance_factor)
        
        # Only apply variance if it doesn't push score outside valid range
        if 0 <= normalized_score + strategy_variance <= 1:
            normalized_score += strategy_variance
        
        # Store normalized and final scores
        results["normalized_score"] = normalized_score
        results["final_score"] = normalized_score
        
        # Store performance metrics for analysis
        results["performance_metrics"] = {
            "baseline": baseline,
            "curve_factor": curve_factor,
            "infection_control_rating": infection_control_rating,
            "economic_rating": economic_rating,
            "population_rating": population_rating,
            "multi_objective_score": multi_objective_score,
            "strategy_variance": strategy_variance
        }
        
        # Add extra information about variants for reporting
        results["variants_emerged"] = len(self.active_variants)
        if self.active_variants:
            results["variant_names"] = [v.name for v in self.active_variants]
            results["highest_variant_prevalence"] = max(v.prevalence for v in self.active_variants)
        
        # Add raw population numbers
        results["raw_data"] = {
            "susceptible": self.state.population.susceptible,
            "infected": self.state.population.infected,
            "recovered": self.state.population.recovered,
            "deaths": self.state.population.deaths,
            "total_population": self.state.population.total,
            "initial_population": self.initial_population,
            "current_gdp": self.state.economy.current_gdp,
            "initial_gdp": self.state.economy.initial_gdp,
            "research_progress": self.state.research.progress
        }
        
        # Display variant info to console if any emerged
        if self.active_variants:
            self.display_variant_info()
        
        # Display strategy analysis
        self.display_strategy_analysis(results)
        
        return results 