"""
Utility functions for the XPECTO Epidemic 2.0 competition system.

These functions help with common tasks like creating engines with 
appropriate randomization to ensure strategy differentiation.
"""
import random
from typing import Dict, Any, Optional, List

from src.competition.testing.engine_adapter import MockEngine

def create_randomized_engine(seed: Optional[int] = None, 
                           difficulty: str = "standard") -> MockEngine:
    """
    Create a MockEngine with randomized parameters for better strategy differentiation.
    
    Parameters:
    -----------
    seed: Optional[int]
        Random seed for reproducibility. If None, a random seed is generated.
    difficulty: str
        Difficulty level affecting base parameters. Options: "standard", "challenging", "expert"
    
    Returns:
    --------
    MockEngine
        A properly initialized MockEngine with randomized parameters
    """
    # Set up randomization
    if seed is None:
        seed = random.randint(1000, 9999)
    random.seed(seed)
    
    # Create engine with unique name
    engine = MockEngine(name=f"Engine-{seed}")
    
    # Apply difficulty settings
    if difficulty == "challenging":
        base_r0 = 3.5
        mortality_rate = 0.03
        resources_mult = 0.7
    elif difficulty == "expert":
        base_r0 = 4.0
        mortality_rate = 0.04
        resources_mult = 0.5
    else:  # standard
        base_r0 = 2.5
        mortality_rate = 0.02
        resources_mult = 1.0
    
    # Randomize initial conditions within appropriate ranges
    # This creates enough variability for different strategy runs to have different outcomes
    engine.metrics["population"]["infected"] = int(random.uniform(0.8, 1.2) * 100)
    engine.metrics["economy"]["initial_gdp"] = int(random.uniform(0.95, 1.05) * 1000)
    engine.metrics["economy"]["current_gdp"] = engine.metrics["economy"]["initial_gdp"]
    engine.metrics["healthcare"]["capacity"] = int(random.uniform(0.9, 1.1) * 500)
    
    # Set disease parameters with slight randomization
    engine.disease_params["r0_base"] = random.uniform(0.95, 1.05) * base_r0
    engine.disease_params["mortality_rate_base"] = random.uniform(0.9, 1.1) * mortality_rate
    engine.disease_params["recovery_rate"] = random.uniform(0.09, 0.11)
    
    # Randomize intervention effects to make strategies have different outcomes
    engine.intervention_effects["lockdown_r0_reduction"] = random.uniform(0.65, 0.75)
    engine.intervention_effects["healthcare_mortality_reduction"] = random.uniform(0.75, 0.85)
    engine.intervention_effects["economic_support_efficiency"] = random.uniform(0.75, 0.85)
    engine.intervention_effects["research_effectiveness"] = random.uniform(0.004, 0.006)
    
    # Update state to match metrics
    engine._update_state()
    
    return engine

# Strategy 1: Aggressive containment
def aggressive_containment(engine):
    """
    A strategy focused on aggressive containment of the epidemic.
    
    This strategy implements strict lockdown measures and healthcare investments
    early to prevent the spread of the disease.
    
    Parameters:
    -----------
    engine: The simulation engine to apply strategy to
    """
    # Initial strict measures
    engine.set_lockdown_level(0.8)
    engine.allocate_resources('healthcare', 300)
    engine.restrict_travel(True)
    
    def step_callback(step, state):
        infection_rate = state.population.infected / state.population.total
        
        # Maintain strict measures until infection rate is very low
        if infection_rate < 0.01:
            engine.set_lockdown_level(0.5)
            engine.allocate_resources('economic', 200)
        elif infection_rate < 0.005:
            engine.set_lockdown_level(0.3)
            engine.allocate_resources('economic', 300)
            engine.restrict_travel(False)
    
    engine.register_step_callback(step_callback)

# Strategy 2: Economic focus
def economic_focus(engine):
    """
    A strategy that prioritizes economic stability over strict containment.
    
    This strategy maintains a more open economy with minimal restrictions
    until infections reach a critical level.
    
    Parameters:
    -----------
    engine: The simulation engine to apply strategy to
    """
    # Minimal restrictions to preserve economy
    engine.set_lockdown_level(0.3)
    engine.allocate_resources('economic', 300)
    engine.allocate_resources('healthcare', 100)
    
    def step_callback(step, state):
        infection_rate = state.population.infected / state.population.total
        
        # Only increase restrictions if infections get very high
        if infection_rate > 0.15:
            engine.set_lockdown_level(0.6)
            engine.allocate_resources('healthcare', 200)
            engine.restrict_travel(True)
        elif infection_rate < 0.05:
            engine.set_lockdown_level(0.2)
            engine.allocate_resources('economic', 400)
            engine.restrict_travel(False)
    
    engine.register_step_callback(step_callback)

# Strategy 3: Balanced approach
def balanced_approach(engine):
    """
    A strategy that balances health concerns with economic impacts.
    
    This strategy adapts based on both infection rates and economic health.
    
    Parameters:
    -----------
    engine: The simulation engine to apply strategy to
    """
    # Moderate initial measures
    engine.set_lockdown_level(0.5)
    engine.allocate_resources('healthcare', 150)
    engine.allocate_resources('economic', 150)
    engine.restrict_travel(True)
    
    def step_callback(step, state):
        infection_rate = state.population.infected / state.population.total
        economic_health = state.economy.current_gdp / state.economy.initial_gdp
        
        # Adapt based on both health and economic concerns
        if infection_rate > 0.1:
            engine.set_lockdown_level(0.7)
            engine.allocate_resources('healthcare', 250)
        elif infection_rate > 0.05:
            if economic_health < 0.7:
                engine.set_lockdown_level(0.4)
                engine.allocate_resources('economic', 200)
            else:
                engine.set_lockdown_level(0.6)
                engine.allocate_resources('healthcare', 200)
        else:
            engine.set_lockdown_level(0.3)
            engine.allocate_resources('economic', 250)
            engine.restrict_travel(False)
    
    engine.register_step_callback(step_callback)

# Strategy 4: Research focus
def research_focus(engine):
    """
    A strategy focused on accelerating research and treatment development.
    
    This strategy invests heavily in research while maintaining moderate containment.
    
    Parameters:
    -----------
    engine: The simulation engine to apply strategy to
    """
    # Heavy investment in research
    engine.set_lockdown_level(0.6)
    engine.allocate_resources('research', 300)
    engine.allocate_resources('healthcare', 100)
    engine.restrict_travel(True)
    
    def step_callback(step, state):
        infection_rate = state.population.infected / state.population.total
        
        # Continue research focus throughout
        if step < 100:
            engine.allocate_resources('research', 50)
        else:
            if infection_rate < 0.05:
                engine.set_lockdown_level(0.4)
                engine.allocate_resources('economic', 200)
                engine.restrict_travel(False)
    
    engine.register_step_callback(step_callback)

# Strategy 5: Testing focus
def testing_focus(engine):
    """
    A strategy emphasizing early detection through testing.
    
    This strategy allocates significant resources to testing while
    maintaining moderate restrictions.
    
    Parameters:
    -----------
    engine: The simulation engine to apply strategy to
    """
    # Heavy investment in testing and targeted measures
    engine.set_lockdown_level(0.4)
    engine.allocate_resources('testing', 300)
    engine.allocate_resources('healthcare', 150)
    
    def step_callback(step, state):
        infection_rate = state.population.infected / state.population.total
        
        # Maintain testing focus while adapting other measures
        engine.allocate_resources('testing', 50)
        
        if infection_rate > 0.1:
            engine.set_lockdown_level(0.6)
            engine.restrict_travel(True)
        elif infection_rate < 0.03:
            engine.set_lockdown_level(0.3)
            engine.allocate_resources('economic', 150)
            engine.restrict_travel(False)
    
    engine.register_step_callback(step_callback)

def create_varied_strategies() -> Dict[str, callable]:
    """
    Create a dictionary of distinctly different strategies for testing.
    
    Returns:
    --------
    Dict[str, callable]
        Dictionary mapping strategy names to strategy functions
    """
    strategies = {}
    
    # Add all strategies to dictionary
    strategies["Aggressive Containment"] = aggressive_containment
    strategies["Economic Focus"] = economic_focus
    strategies["Balanced Approach"] = balanced_approach
    strategies["Research Focus"] = research_focus
    strategies["Testing Focus"] = testing_focus
    
    return strategies

def compare_strategies(engine: MockEngine, strategies: Dict[str, callable], 
                     steps: int = 200) -> Dict[str, Dict[str, float]]:
    """
    Run multiple strategies on the same engine configuration and compare results.
    
    Parameters:
    -----------
    engine: MockEngine
        The engine to use for simulation
    strategies: Dict[str, callable]
        Dictionary of strategies to test
    steps: int
        Number of simulation steps to run
        
    Returns:
    --------
    Dict[str, Dict[str, float]]
        Results for each strategy
    """
    import copy
    
    # Store results for each strategy
    results = {}
    
    # Run each strategy on a fresh copy of the engine
    for name, strategy in strategies.items():
        # Create a deep copy of the engine to ensure fair comparison
        engine_copy = copy.deepcopy(engine)
        
        # Apply the strategy
        strategy(engine_copy)
        
        # Run the simulation
        engine_copy.run(steps)
        
        # Calculate and store results
        population_survived = (engine_copy.metrics["population"]["total"] - engine_copy.metrics["population"]["dead"]) / engine_copy.metrics["population"]["total"]
        gdp_preserved = engine_copy.metrics["economy"]["current_gdp"] / engine_copy.metrics["economy"]["initial_gdp"]
        infection_control = 1.0 - (engine_copy.metrics["max_infection_rate"])
        
        # Calculate resource efficiency
        total_resources = engine_copy.metrics["resources"]["total_spent"]
        # Avoid division by zero
        resource_efficiency = 1.0 - (total_resources / 5000) if total_resources > 0 else 1.0
        
        # Calculate time to containment
        if engine_copy.metrics["containment_achieved"]:
            time_efficiency = 1.0 - (engine_copy.metrics["containment_step"] / steps)
        else:
            time_efficiency = 0.0
        
        # Calculate final score (weighted average)
        final_score = (
            0.3 * population_survived +
            0.2 * gdp_preserved +
            0.2 * infection_control +
            0.15 * resource_efficiency +
            0.15 * time_efficiency
        )
        
        # Store results
        results[name] = {
            "population_survived": population_survived,
            "gdp_preserved": gdp_preserved,
            "infection_control": infection_control,
            "resource_efficiency": resource_efficiency,
            "time_to_containment": time_efficiency,
            "final_score": final_score
        }
    
    return results

def display_strategy_comparison(results: Dict[str, Dict[str, float]]) -> None:
    """
    Display a comparison of strategy results.
    
    Parameters:
    -----------
    results: Dict[str, Dict[str, float]]
        Results from compare_strategies function
    """
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    # Create DataFrame for easier visualization
    data = []
    for strategy, metrics in results.items():
        row = {"Strategy": strategy}
        row.update(metrics)
        data.append(row)
    
    df = pd.DataFrame(data)
    
    # Set Strategy as index
    df.set_index("Strategy", inplace=True)
    
    # Create bar chart
    ax = df.plot(kind="bar", figsize=(12, 6))
    plt.title("Strategy Comparison")
    plt.ylabel("Score (0-1)")
    plt.grid(axis="y", alpha=0.3)
    plt.legend(title="Metrics")
    plt.tight_layout()
    
    # Add value labels on top of bars
    for container in ax.containers:
        ax.bar_label(container, fmt="%.2f", fontsize=8)
    
    plt.show()
    
    # Print the scores in a table
    print("\nStrategy Scores:")
    print("-" * 100)
    print(f"{'Strategy':<25} | {'Population':<12} | {'GDP':<12} | {'Infection':<12} | {'Resources':<12} | {'Time':<12} | {'Final Score':<12}")
    print("-" * 100)
    
    for strategy, metrics in results.items():
        print(f"{strategy:<25} | {metrics['population_survived']:<12.4f} | {metrics['gdp_preserved']:<12.4f} | "
              f"{metrics['infection_control']:<12.4f} | {metrics['resource_efficiency']:<12.4f} | "
              f"{metrics['time_to_containment']:<12.4f} | {metrics['final_score']:<12.4f}")
    
    # Find best strategy
    best_strategy = max(results.items(), key=lambda x: x[1]["final_score"])
    print("\n" + "=" * 100)
    print(f"Best strategy: {best_strategy[0]} (Score: {best_strategy[1]['final_score']:.4f})")
    print("=" * 100) 