#!/usr/bin/env python3
"""
XPECTO Epidemic 2.0 Strategy Testing Example

This script demonstrates how to use the enhanced utility functions
to compare different epidemic control strategies and identify the
most effective approach.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.competition.utils import (
    create_randomized_engine,
    create_varied_strategies,
    compare_strategies,
    display_strategy_comparison
)

def main():
    # Create a randomized engine to ensure varied results
    print("Creating randomized epidemic engine...")
    engine = create_randomized_engine(seed=12345, difficulty="standard")
    
    # Load a set of varied strategies
    print("Loading varied strategies...")
    strategies = create_varied_strategies()
    print(f"Available strategies: {', '.join(strategies.keys())}")
    
    # Compare all strategies
    print("\nComparing strategies over 200 simulation steps...")
    results = compare_strategies(engine, strategies, steps=200)
    
    # Display the comparison
    print("Displaying strategy comparison results...")
    display_strategy_comparison(results)
    
    # Define a custom strategy
    print("\nDefining a custom adaptive strategy...")
    
    def custom_strategy(engine):
        # Initial balanced measures
        engine.set_lockdown_level(0.4)
        engine.allocate_resources('healthcare', 200)
        engine.allocate_resources('economic', 100)
        engine.restrict_travel(False)
        
        def step_callback(step, state):
            # Get the current infection rate
            infection_rate = state.population.infected / state.population.total
            
            # Dynamic lockdown based on infection rate with thresholds
            if infection_rate > 0.15:  # Severe outbreak
                engine.set_lockdown_level(0.8)
                engine.restrict_travel(True)
                engine.allocate_resources('healthcare', 300)
            elif infection_rate > 0.08:  # Moderate outbreak
                engine.set_lockdown_level(0.6)
                engine.restrict_travel(True)
                engine.allocate_resources('healthcare', 200)
                engine.allocate_resources('economic', 100)
            elif infection_rate > 0.03:  # Mild outbreak
                engine.set_lockdown_level(0.4)
                engine.restrict_travel(False)
                engine.allocate_resources('healthcare', 150)
                engine.allocate_resources('economic', 150)
            else:  # Controlled situation
                engine.set_lockdown_level(0.2)
                engine.restrict_travel(False)
                engine.allocate_resources('economic', 250)
                
            # Always invest some in research
            engine.allocate_resources('research', 50)
        
        engine.register_step_callback(step_callback)
    
    # Add the custom strategy to our comparison
    custom_strategies = {"Custom Adaptive": custom_strategy}
    
    # Get the best strategy from the previous comparison
    best_strategy_name = max(results.items(), key=lambda x: x[1]['final_score'])[0]
    best_strategy = {best_strategy_name: strategies[best_strategy_name]}
    
    # Combine the best strategy with our custom strategy
    combined_strategies = {**best_strategy, **custom_strategies}
    
    # Compare them
    print(f"\nComparing custom strategy against {best_strategy_name}...")
    custom_results = compare_strategies(create_randomized_engine(seed=12345, difficulty="standard"), 
                                      combined_strategies, steps=200)
    display_strategy_comparison(custom_results)

if __name__ == "__main__":
    main() 