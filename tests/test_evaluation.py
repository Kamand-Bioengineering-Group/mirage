#!/usr/bin/env python3

"""
Test script for the competition evaluation module.
This script tests the strategy evaluator and visualization components.
"""

import os
import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# Add parent directory to path to allow importing from src
sys.path.append(str(Path(__file__).parent.parent))

# Import competition modules
from src.competition.testing.enhanced_engine import EnhancedEngine
from src.competition.evaluation.strategy_evaluator import StrategyEvaluator
from src.competition.evaluation.visualization import EvaluationVisualizer


# Define test strategies
def extreme_lockdown_strategy(engine):
    """Strategy that emphasizes strong lockdown measures."""
    engine.set_lockdown_level(0.8)
    engine.allocate_resources('healthcare', 600)
    engine.allocate_resources('economic', 200)
    engine.allocate_resources('research', 200)
    engine.restrict_travel(True)
    
    def monitor_and_respond(step, state):
        # Ensure we never divide by zero
        total_population = max(1, state.population.total)
        infection_rate = state.population.infected / total_population
        
        if infection_rate < 0.05:
            engine.set_lockdown_level(0.5)
            engine.allocate_resources('economic', 50)
        elif infection_rate > 0.15:
            engine.set_lockdown_level(0.9)
            engine.allocate_resources('healthcare', 50)
    
    engine.register_step_callback(monitor_and_respond)


def economy_focused_strategy(engine):
    """Strategy that prioritizes economic stability."""
    engine.set_lockdown_level(0.3)
    engine.allocate_resources('economic', 700)
    engine.allocate_resources('healthcare', 200)
    engine.allocate_resources('research', 100)
    engine.restrict_travel(False)
    
    def monitor_and_respond(step, state):
        # Ensure we never divide by zero
        total_population = max(1, state.population.total)
        infection_rate = state.population.infected / total_population
        
        if infection_rate > 0.2:
            engine.set_lockdown_level(0.5)
            engine.allocate_resources('healthcare', 100)
        else:
            engine.set_lockdown_level(0.2)
            engine.allocate_resources('economic', 50)
    
    engine.register_step_callback(monitor_and_respond)


def balanced_strategy(engine):
    """Strategy that balances health and economic concerns."""
    engine.set_lockdown_level(0.5)
    engine.allocate_resources('healthcare', 400)
    engine.allocate_resources('economic', 300)
    engine.allocate_resources('research', 300)
    
    def monitor_and_respond(step, state):
        # Ensure we never divide by zero
        total_population = max(1, state.population.total)
        infection_rate = state.population.infected / total_population
        
        if infection_rate > 0.1:
            engine.set_lockdown_level(0.7)
            engine.allocate_resources('healthcare', 50)
        elif infection_rate < 0.03:
            engine.set_lockdown_level(0.3)
            engine.allocate_resources('economic', 50)
    
    engine.register_step_callback(monitor_and_respond)


def research_priority_strategy(engine):
    """Strategy that focuses on research."""
    engine.set_lockdown_level(0.6)
    engine.allocate_resources('research', 500)
    engine.allocate_resources('healthcare', 300)
    engine.allocate_resources('economic', 200)
    
    def monitor_and_respond(step, state):
        if state.research.progress > 0.5:
            engine.allocate_resources('economic', 100)
            engine.set_lockdown_level(0.4)
    
    engine.register_step_callback(monitor_and_respond)


def main():
    """Main test function."""
    print("Testing Evaluation Module...")
    
    # Create output directory for results
    os.makedirs("test_results", exist_ok=True)
    
    # Initialize evaluator with fixed seed for reproducibility
    evaluator = StrategyEvaluator(random_seed=42)
    
    # Set strategies to evaluate
    strategies = {
        "Extreme Lockdown": extreme_lockdown_strategy,
        "Economy Focused": economy_focused_strategy,
        "Balanced Approach": balanced_strategy,
        "Research Priority": research_priority_strategy
    }
    
    # Compare strategies
    print("\nComparing strategies...")
    comparison_df = evaluator.compare_strategies(strategies, steps=365, num_trials=1)
    print("\nStrategy Comparison:")
    print(comparison_df)
    
    # Create visualizations
    print("\nCreating visualizations...")
    visualizer = EvaluationVisualizer(evaluator)
    
    # Generate dashboard
    dashboard_dir = "test_results/dashboard"
    visualizer.create_evaluation_dashboard(list(strategies.keys()), dashboard_dir)
    
    # Generate report
    report = evaluator.create_strategy_report("test_results/evaluation_report.md")
    
    # Save evaluations to JSON
    evaluator.save_evaluations("test_results/evaluations.json")
    
    print("\nEvaluation testing complete!")
    print(f"Results saved to 'test_results' directory")


if __name__ == "__main__":
    main() 