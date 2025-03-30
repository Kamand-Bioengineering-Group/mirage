#!/usr/bin/env python3

"""
Test script for the adaptive strategies module.

This script tests different types of adaptive strategies and evaluates their performance.
"""

import os
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time

# Add parent directory to path to allow importing from src
sys.path.append(str(Path(__file__).parent.parent))

# Import competition modules
from src.competition.testing.enhanced_engine import EnhancedEngine
from src.competition.evaluation.strategy_evaluator import StrategyEvaluator
from src.competition.evaluation.visualization import EvaluationVisualizer
from src.competition.evaluation.adaptive_strategies import (
    AdaptiveStrategy,
    PhaseBasedStrategy,
    ResponseCurveStrategy,
    RLInspiredStrategy,
    AdaptiveStrategyEvaluator,
    StrategyAction
)


def main():
    """Main test function."""
    print("Testing Adaptive Strategies Module...")
    
    # Create output directory for results
    os.makedirs("test_results/adaptive", exist_ok=True)
    
    # Initialize evaluator with fixed seed for reproducibility
    evaluator = StrategyEvaluator(random_seed=42)
    adaptive_evaluator = AdaptiveStrategyEvaluator(evaluator)
    
    # Create adaptive strategies
    print("\nCreating adaptive strategies...")
    phase_strategy = PhaseBasedStrategy("Phase-Based Strategy")
    response_curve_strategy = ResponseCurveStrategy("Response Curve Strategy")
    rl_strategy = RLInspiredStrategy("RL-Inspired Strategy")
    
    # Create a basic static strategy for comparison
    class StaticStrategy(AdaptiveStrategy):
        def __init__(self):
            super().__init__("Static Strategy")
            
        def decide_action(self, state):
            # Always return the same action regardless of state
            return StrategyAction(
                lockdown_level=0.5,
                healthcare_allocation=400,
                economic_allocation=300,
                research_allocation=300,
                restrict_travel=True
            )
    
    static_strategy = StaticStrategy()
    
    # List of strategies to evaluate
    strategies = [
        static_strategy,
        phase_strategy,
        response_curve_strategy,
        rl_strategy
    ]
    
    # Evaluate each strategy individually
    print("\nEvaluating strategies individually...")
    for strategy in strategies:
        print(f"\nEvaluating {strategy.name}...")
        evaluation = adaptive_evaluator.evaluate_adaptive_strategy(
            strategy, 
            steps=180,  # Shorter simulation for testing
            num_trials=1
        )
        print(f"Score: {evaluation.score:.4f} (Grade: {evaluation.grade})")
        print(f"Population: {evaluation.population_survived:.1%}, GDP: {evaluation.gdp_preserved:.1%}")
    
    # Compare all strategies
    print("\nComparing all strategies...")
    comparison_df = adaptive_evaluator.compare_adaptive_strategies(strategies, steps=180, num_trials=1)
    print("\nStrategy Comparison:")
    print(comparison_df)
    
    # Analyze adaptability
    print("\nAnalyzing strategy adaptability...")
    adaptability_results = {}
    for strategy in strategies:
        adaptability = adaptive_evaluator.analyze_strategy_adaptability(strategy, steps=180)
        adaptability_results[strategy.name] = adaptability
        
        print(f"\n{strategy.name} Adaptability Analysis:")
        print(f"- Adaptability Score: {adaptability['adaptability_score']:.3f}")
        print(f"- State-Action Correlation: {adaptability['state_action_correlation']:.3f}")
        print(f"- Average Action Change: {adaptability['avg_action_change']:.3f}")
    
    # Create visualizations
    print("\nCreating visualizations...")
    visualizer = EvaluationVisualizer(evaluator)
    
    # Generate dashboard
    dashboard_dir = "test_results/adaptive/dashboard"
    visualizer.create_evaluation_dashboard([s.name for s in strategies], dashboard_dir)
    
    # Generate strategy analysis report
    report = evaluator.create_strategy_report("test_results/adaptive/strategy_report.md")
    
    # Plot adaptability comparison
    plt.figure(figsize=(10, 6))
    strategy_names = list(adaptability_results.keys())
    adaptability_scores = [adaptability_results[name]["adaptability_score"] for name in strategy_names]
    
    plt.bar(strategy_names, adaptability_scores)
    plt.title("Strategy Adaptability Comparison")
    plt.ylabel("Adaptability Score")
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig("test_results/adaptive/adaptability_comparison.png", dpi=300)
    
    print("\nAdaptive Strategies testing complete!")
    print(f"Results saved to 'test_results/adaptive' directory")


if __name__ == "__main__":
    main() 