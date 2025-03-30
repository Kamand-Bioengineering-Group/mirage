#!/usr/bin/env python3

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Callable, Any, Tuple
import random

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Import required modules
from src.competition import CompetitionManager
from src.competition.testing.engine_adapter import MockEngine

def run_strategy_test(engine_name: str, engine_instance, strategies: List[Tuple[str, Callable]], 
                     runs_per_strategy: int = 3) -> pd.DataFrame:
    """
    Run multiple strategies on the given engine and return results.
    
    Args:
        engine_name: Name of the engine being tested
        engine_instance: Instance of the engine to test
        strategies: List of tuples (strategy_name, strategy_function)
        runs_per_strategy: Number of runs per strategy
        
    Returns:
        DataFrame with test results
    """
    print(f"\n=== Testing {engine_name} ===")
    
    # Create competition manager
    competition = CompetitionManager(data_dir=f"test_data_{engine_name.lower()}", engine=engine_instance)
    
    # Setup player
    player_id = competition.setup_player(name="Test Player")
    competition.toggle_practice_mode(is_practice=True)
    
    # Use challenging scenario for more differentiation
    try:
        competition.set_scenario("challenging")
    except:
        # Fallback to standard scenario if challenging isn't available
        competition.set_scenario("standard")
    
    # Store results by strategy
    all_results = []
    
    # Run each strategy multiple times
    for strategy_name, strategy_func in strategies:
        strategy_scores = []
        
        for run in range(runs_per_strategy):
            # Reset simulation
            competition.setup_simulation()
            
            # Run simulation with strategy
            print(f"Running {strategy_name} with {engine_name} - Run {run+1}/{runs_per_strategy}")
            result = competition.run_simulation(steps=365, interventions=[strategy_func])
            
            # Store result with additional metadata
            result_data = {
                'Engine': engine_name,
                'Strategy': strategy_name,
                'Run': run+1,
                'Population Survived': result.get('population_survived', 0),
                'GDP Preserved': result.get('gdp_preserved', 0),
                'Infection Control': result.get('infection_control', 0),
                'Resource Efficiency': result.get('resource_efficiency', 0),
                'Time to Containment': result.get('time_to_containment', 0),
                'Final Score': result.get('final_score', 0)
            }
            all_results.append(result_data)
            strategy_scores.append(result.get('final_score', 0))
        
        # Print summary for this strategy
        print(f"{strategy_name} with {engine_name} - Avg Score: {np.mean(strategy_scores):.4f}, "
              f"StdDev: {np.std(strategy_scores):.4f}")
    
    # Convert to DataFrame
    return pd.DataFrame(all_results)

def extreme_lockdown(engine):
    """
    Extreme lockdown strategy with total focus on disease containment.
    """
    # Initial setup - extreme containment
    engine.set_lockdown_level(1.0)  # 100% lockdown severity
    engine.allocate_resources('healthcare', 650)  # Almost all resources to healthcare
    engine.restrict_travel(True)  # Full travel ban
    
    # Define a callback for dynamic response
    def monitor_and_respond(step, state):
        infection_rate = state.population.infected / state.population.total
        
        # Maintain extreme measures until near elimination
        if infection_rate > 0.0005:  # Continue until virtually eliminated
            engine.set_lockdown_level(1.0)
            if step % 15 == 0:  # Periodically add more healthcare resources
                engine.allocate_resources('healthcare', 50)
        else:
            # Only if infection is almost eliminated, slightly reduce measures
            engine.set_lockdown_level(0.9)
            if step > 300:  # Very late in the pandemic
                engine.allocate_resources('economic', 50)  # Minimal economic support
    
    # Register the callback
    engine.register_step_callback(monitor_and_respond)

def economy_only(engine):
    """
    Strategy with absolutely no restrictions and total economic focus.
    """
    # Initial setup - zero restrictions
    engine.set_lockdown_level(0.0)  # No lockdown
    engine.allocate_resources('economic', 650)  # Almost all resources to economy
    engine.restrict_travel(False)  # No travel restrictions
    
    # Define a callback for dynamic response
    def monitor_and_respond(step, state):
        infection_rate = state.population.infected / state.population.total
        
        # No matter what, focus on economy
        if infection_rate > 0.35:  # Only if catastrophic infection rate
            engine.set_lockdown_level(0.1)  # Minimal restrictions
            engine.allocate_resources('healthcare', 50)  # Token healthcare
        else:
            # Maintain economic focus
            engine.set_lockdown_level(0.0)
            if step % 15 == 0:  # Periodically add economic support
                engine.allocate_resources('economic', 50)
    
    # Register the callback
    engine.register_step_callback(monitor_and_respond)

def adaptive_strategy(engine):
    """
    Highly adaptive strategy that changes dramatically based on conditions.
    """
    # Initial setup - moderate-high measures
    engine.set_lockdown_level(0.7)  # Significant initial lockdown
    engine.allocate_resources('healthcare', 300)  # Initial healthcare focus
    engine.allocate_resources('economic', 200)  # Some economic support
    engine.restrict_travel(True)  # Initial travel ban
    
    # Define a callback for dynamic response
    def monitor_and_respond(step, state):
        infection_rate = state.population.infected / state.population.total
        economic_health = state.economy.current_gdp / state.economy.initial_gdp
        
        # Early phase - strong containment (0-60 days)
        if step < 60:
            if infection_rate > 0.08:
                engine.set_lockdown_level(0.8)
                engine.allocate_resources('healthcare', 70)
            elif infection_rate > 0.03:
                engine.set_lockdown_level(0.6)
                engine.allocate_resources('healthcare', 50)
                engine.allocate_resources('economic', 20)
            else:
                engine.set_lockdown_level(0.5)
                engine.allocate_resources('economic', 50)
                
        # Middle phase - balance with economic focus (60-180 days)
        elif 60 <= step < 180:
            if infection_rate > 0.1:
                engine.set_lockdown_level(0.7)
                engine.allocate_resources('healthcare', 60)
            elif economic_health < 0.6:  # Economy struggling badly
                engine.set_lockdown_level(0.3)
                engine.allocate_resources('economic', 100)
                engine.restrict_travel(False)
            else:
                engine.set_lockdown_level(0.5)
                engine.allocate_resources('healthcare', 40)
                engine.allocate_resources('economic', 60)
                engine.restrict_travel(infection_rate > 0.03)
                
        # Late phase - recovery and targeted controls (180+ days)
        else:
            if infection_rate < 0.01:
                engine.set_lockdown_level(0.2)
                engine.allocate_resources('economic', 80)
                engine.restrict_travel(False)
            elif economic_health < 0.5:  # Severe economic problems
                engine.set_lockdown_level(0.3)
                engine.allocate_resources('economic', 120)
                engine.restrict_travel(False)
            else:
                engine.set_lockdown_level(0.4)
                engine.allocate_resources('healthcare', 30)
                engine.allocate_resources('economic', 40)
                engine.restrict_travel(infection_rate > 0.05)
    
    # Register the callback
    engine.register_step_callback(monitor_and_respond)

def research_priority(engine):
    """
    Strategy that prioritizes research above all else.
    """
    # Initial setup - focus on research and moderate containment
    engine.set_lockdown_level(0.6)  # Significant lockdown to slow spread
    engine.allocate_resources('research', 500)  # Massive research focus
    engine.allocate_resources('healthcare', 150)  # Some healthcare
    engine.restrict_travel(True)  # Travel restrictions
    
    # Define a callback for dynamic response
    def monitor_and_respond(step, state):
        infection_rate = state.population.infected / state.population.total
        research_progress = state.research.progress
        
        # Research phase - continue heavy investment
        if research_progress < 0.7:  # Until research milestone
            if step % 10 == 0:  # Regularly invest in research
                engine.allocate_resources('research', 80)
            
            # Maintain containment to buy time
            if infection_rate > 0.15:
                engine.set_lockdown_level(0.8)
                engine.allocate_resources('healthcare', 50)
            else:
                engine.set_lockdown_level(0.6)
        
        # Post-research phase - leverage breakthrough
        else:
            # After research milestones, cut lockdown and focus on economy
            if infection_rate > 0.08:
                engine.set_lockdown_level(0.5)
                engine.allocate_resources('healthcare', 80)
            else:
                engine.set_lockdown_level(0.3)
                engine.allocate_resources('economic', 100)
                engine.restrict_travel(False)
    
    # Register the callback
    engine.register_step_callback(monitor_and_respond)

def run_tests():
    """Run tests with different engines and strategies."""
    # Set random seed for reproducibility
    random.seed(42)
    
    # Define strategies to test
    strategies = [
        ("Extreme Lockdown", extreme_lockdown),
        ("Economy Only", economy_only),
        ("Adaptive Strategy", adaptive_strategy),
        ("Research Priority", research_priority)
    ]
    
    # Test with MockEngine
    mock_engine = MockEngine()
    # Modify the MockEngine parameters to potentially increase differences
    mock_engine.intervention_effects["lockdown_r0_reduction"] = 0.98
    mock_engine.intervention_effects["economic_support_efficiency"] = 0.98
    mock_engine.intervention_effects["healthcare_mortality_reduction"] = 0.98
    mock_engine.intervention_effects["research_effectiveness"] = 0.015
    mock_engine.disease_params["r0_base"] = 3.5
    mock_engine.disease_params["mortality_rate_base"] = 0.03
    
    mock_results = run_strategy_test("MockEngine", mock_engine, strategies)
    
    # Note: We can't test with the original engine as it's not available in this setup
    # This would be where we would test with the original engine if available
    
    # Calculate statistics and display them
    print("\n=== Summary Statistics ===")
    summary = mock_results.groupby(['Engine', 'Strategy'])['Final Score'].agg(['mean', 'std', 'min', 'max'])
    print(summary)
    
    # Visualize the results
    plt.figure(figsize=(12, 8))
    sns.boxplot(x='Strategy', y='Final Score', hue='Engine', data=mock_results)
    plt.title('Strategy Comparison by Engine')
    plt.tight_layout()
    plt.savefig('engine_strategy_comparison.png')
    
    # Calculate score range for each engine
    for engine_name in mock_results['Engine'].unique():
        engine_data = mock_results[mock_results['Engine'] == engine_name]
        max_score = engine_data['Final Score'].max()
        min_score = engine_data['Final Score'].min()
        score_range = max_score - min_score
        print(f"\n{engine_name} Score Range: {score_range:.4f} (Min: {min_score:.4f}, Max: {max_score:.4f})")
    
    return mock_results

if __name__ == "__main__":
    run_tests() 