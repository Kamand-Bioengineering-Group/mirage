#!/usr/bin/env python3
"""
Test script to verify that different intervention strategies produce 
different outcomes with randomized scenario parameters.
"""
import sys
import os
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent))

from src.competition.utils.utils_functions import (
    create_randomized_engine,
    aggressive_containment,
    economic_focus,
    research_focus,
    testing_focus,
    balanced_approach,
    compare_strategies,
    display_strategy_comparison
)

def test_strategy_differentiation():
    """
    Test that different strategies produce different outcomes.
    """
    print("=== Testing Strategy Differentiation ===")
    
    # Create a randomized engine with a fixed seed for reproducibility in this test
    engine = create_randomized_engine(seed=42, difficulty="standard")
    print(f"Created engine with R0: {engine.disease_params['r0_base']:.2f}")
    
    # Create a dictionary of strategies to test
    strategies = {
        "Aggressive Containment": aggressive_containment,
        "Economic Focus": economic_focus,
        "Research Focus": research_focus,
        "Testing Focus": testing_focus,
        "Balanced Approach": balanced_approach
    }
    
    # Run comparison (this will run the same initial conditions with different strategies)
    print("\nRunning all strategies with the same initial conditions...")
    results = compare_strategies(engine, strategies, steps=200)
    
    # Display results
    display_strategy_comparison(results)
    
    # Verify that strategies produce different outcomes
    scores = [result["final_score"] for result in results.values()]
    score_difference = max(scores) - min(scores)
    
    print(f"\nScore range: {min(scores):.4f} to {max(scores):.4f}")
    print(f"Score difference: {score_difference:.4f}")
    
    # Check if the difference is meaningful (arbitrary threshold)
    if score_difference > 0.05:
        print("✅ SUCCESS: Strategies produce meaningfully different outcomes")
    else:
        print("❌ WARNING: Strategies don't produce very different outcomes")
        
    return score_difference > 0.05

def test_randomized_scenarios():
    """
    Test that the same strategy produces different outcomes with randomized scenarios.
    """
    print("\n=== Testing Randomized Scenarios ===")
    
    # Create engines with different random seeds
    engines = [
        create_randomized_engine(seed=i, difficulty="standard") 
        for i in range(42, 47)  # 5 different seeds
    ]
    
    # Use the same strategy for all engines
    strategy = balanced_approach
    
    print(f"\nRunning balanced_approach strategy on {len(engines)} different randomized scenarios...")
    
    # Keep track of results
    all_results = {}
    
    for i, engine in enumerate(engines):
        # Create a deep copy to prevent modifications
        import copy
        engine_copy = copy.deepcopy(engine)
        
        # Apply the strategy
        strategy(engine_copy)
        
        # Run the simulation
        engine_copy.run(200)
        
        # Calculate results
        population_survived = (engine_copy.metrics["population"]["total"] - engine_copy.metrics["population"]["dead"]) / engine_copy.metrics["population"]["total"]
        gdp_preserved = engine_copy.metrics["economy"]["current_gdp"] / engine_copy.metrics["economy"]["initial_gdp"]
        infection_control = 1.0 - (engine_copy.metrics["max_infection_rate"])
        
        # Calculate resource efficiency
        total_resources = engine_copy.metrics["resources"]["total_spent"]
        resource_efficiency = 1.0 - (total_resources / 5000) if total_resources > 0 else 1.0
        
        # Calculate time to containment
        if engine_copy.metrics["containment_achieved"]:
            time_efficiency = 1.0 - (engine_copy.metrics["containment_step"] / 200)
        else:
            time_efficiency = 0.0
            
        # Calculate final score
        final_score = (
            0.3 * population_survived +
            0.2 * gdp_preserved +
            0.2 * infection_control +
            0.15 * resource_efficiency +
            0.15 * time_efficiency
        )
        
        # Store results
        scenario_name = f"Scenario {i+1} (seed={engines[i].name.split('-')[1]})"
        all_results[scenario_name] = {
            "population_survived": population_survived,
            "gdp_preserved": gdp_preserved,
            "infection_control": infection_control,
            "resource_efficiency": resource_efficiency,
            "time_to_containment": time_efficiency,
            "final_score": final_score
        }
        
        print(f"{scenario_name}: Score = {final_score:.4f}")
    
    # Calculate score range
    scores = [result["final_score"] for result in all_results.values()]
    score_difference = max(scores) - min(scores)
    
    print(f"\nScore range: {min(scores):.4f} to {max(scores):.4f}")
    print(f"Score difference: {score_difference:.4f}")
    
    # Check if the difference is meaningful
    if score_difference > 0.03:  # Lower threshold since these are just seed variations
        print("✅ SUCCESS: Randomized scenarios produce different outcomes")
    else:
        print("❌ WARNING: Randomized scenarios don't produce very different outcomes")
    
    # Display all results in a table
    print("\nDetailed Results:")
    print("-" * 100)
    print(f"{'Scenario':<20} | {'Population':<12} | {'GDP':<12} | {'Infection':<12} | {'Resources':<12} | {'Time':<12} | {'Score':<12}")
    print("-" * 100)
    
    for scenario, metrics in all_results.items():
        print(f"{scenario:<20} | {metrics['population_survived']:<12.4f} | {metrics['gdp_preserved']:<12.4f} | "
              f"{metrics['infection_control']:<12.4f} | {metrics['resource_efficiency']:<12.4f} | "
              f"{metrics['time_to_containment']:<12.4f} | {metrics['final_score']:<12.4f}")
              
    return score_difference > 0.03

if __name__ == "__main__":
    # Run both tests
    strategy_diff = test_strategy_differentiation()
    scenario_diff = test_randomized_scenarios()
    
    # Final verdict
    print("\n=== Final Verdict ===")
    if strategy_diff and scenario_diff:
        print("✅ SUCCESS: Both tests passed! Different strategies produce different outcomes and randomized scenarios work as expected.")
    elif strategy_diff:
        print("⚠️ PARTIAL SUCCESS: Different strategies produce different outcomes, but randomized scenarios need improvement.")
    elif scenario_diff:
        print("⚠️ PARTIAL SUCCESS: Randomized scenarios work as expected, but strategies don't produce different enough outcomes.")
    else:
        print("❌ FAILURE: Both tests failed. Further adjustments needed.") 