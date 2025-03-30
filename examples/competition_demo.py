#!/usr/bin/env python3
"""
XPECTO Epidemic 2.0 Competition Demo

This script demonstrates how to use the competition system to:
1. Register a player
2. Run simulations with different strategies
3. Compare results
4. View and save the leaderboard

Use this as a reference for how to interact with the competition system.
"""

import sys
import os
from pathlib import Path
import random
import time

# Add the project root to the path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Import the competition API and MockEngine
from src.competition.api import CompetitionAPI
from src.competition.testing.engine_adapter import MockEngine

# Create the competition manager instance with a demo data directory
competition = CompetitionAPI(data_dir="demo_data", engine=MockEngine())

def print_header(title):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def simulate_thinking(message, duration=1.0):
    """Simulate thinking with dots."""
    print(message, end="", flush=True)
    for _ in range(3):
        time.sleep(duration / 3)
        print(".", end="", flush=True)
    print(" Done!")

def basic_strategy(engine):
    """A very basic strategy that sets moderate controls."""
    engine.set_lockdown_level(0.5)
    engine.allocate_resources('healthcare', 100)
    engine.restrict_travel(True)

def reactive_strategy(engine):
    """A strategy that reacts to the simulation state."""
    
    # Set initial conditions
    engine.set_lockdown_level(0.3)
    engine.allocate_resources('healthcare', 50)
    
    def on_step(step, state):
        # Calculate infection rate
        infection_rate = state.population.infected / state.population.total
        
        # Adjust strategy based on infection rate
        if infection_rate > 0.1:
            engine.set_lockdown_level(0.7)
            engine.allocate_resources('healthcare', 200)
            engine.restrict_travel(True)
        elif infection_rate > 0.05:
            engine.set_lockdown_level(0.5)
            engine.allocate_resources('healthcare', 100)
            engine.restrict_travel(True)
        else:
            engine.set_lockdown_level(0.3)
            engine.allocate_resources('healthcare', 50)
            engine.restrict_travel(False)
    
    # Register the callback
    engine.register_step_callback(on_step)

def random_strategy(engine):
    """A strategy that makes random decisions (not recommended!)."""
    
    def on_step(step, state):
        if random.random() < 0.1:  # 10% chance to change strategy each step
            engine.set_lockdown_level(random.random())
            engine.allocate_resources('healthcare', random.randint(0, 300))
            engine.restrict_travel(random.random() > 0.5)
    
    # Register the callback
    engine.register_step_callback(on_step)

def main():
    """Main demonstration function."""
    print_header("XPECTO Epidemic 2.0 Competition Demo")
    
    # Step 1: Register a player
    player_name = "Demo Player"
    player_id = competition.register_player(name=player_name)
    print(f"Registered player: {player_name} (ID: {player_id})")
    
    # Enable practice mode
    competition.set_practice_mode(True)
    print("Practice mode enabled - attempts won't count for the official competition")
    
    # Step 2: List available scenarios
    print_header("Available Scenarios")
    scenarios = competition.list_scenarios()
    for scenario in scenarios:
        print(f"- {scenario['id']}: {scenario['name']} (Difficulty: {scenario['difficulty']})")
        print(f"  {scenario['description']}")
        print()
    
    # Step 3: Select a scenario
    scenario_id = "standard"  # Use the standard scenario for the demo
    if competition.set_scenario(scenario_id):
        print(f"Selected scenario: {scenario_id}")
        
        # Display scenario details
        details = competition.get_scenario_details(scenario_id)
        print(f"\nScenario details:")
        print(f"- Name: {details['name']}")
        print(f"- Description: {details['description']}")
        print(f"- Difficulty: {details['difficulty']}")
    else:
        print(f"Error: Could not select scenario {scenario_id}")
        return
    
    # Step 4: Run simulations with different strategies
    print_header("Running Simulations")
    
    # Dictionary to store results
    results = {}
    
    # Run with basic strategy
    print("Running simulation with basic strategy...")
    simulate_thinking("Processing", 2)
    results["Basic Strategy"] = competition.run_simulation(
        interventions=[basic_strategy],
        steps=200  # Shorter simulation for demo purposes
    )
    print(f"Basic Strategy score: {results['Basic Strategy']['final_score']:.4f}")
    
    # Run with reactive strategy
    print("\nRunning simulation with reactive strategy...")
    simulate_thinking("Processing", 2)
    results["Reactive Strategy"] = competition.run_simulation(
        interventions=[reactive_strategy],
        steps=200
    )
    print(f"Reactive Strategy score: {results['Reactive Strategy']['final_score']:.4f}")
    
    # Run with random strategy
    print("\nRunning simulation with random strategy...")
    simulate_thinking("Processing", 2)
    results["Random Strategy"] = competition.run_simulation(
        interventions=[random_strategy],
        steps=200
    )
    print(f"Random Strategy score: {results['Random Strategy']['final_score']:.4f}")
    
    # Step 5: Compare results
    print_header("Results Comparison")
    print(f"{'Strategy':<20} | {'Population':<12} | {'GDP':<12} | {'Infection':<12} | {'Resources':<12} | {'Time':<12} | {'Final Score':<12}")
    print("-" * 100)
    
    for strategy, result in results.items():
        print(f"{strategy:<20} | {result['population_survived']:<12.4f} | {result['gdp_preserved']:<12.4f} | "
              f"{result['infection_control']:<12.4f} | {result['resource_efficiency']:<12.4f} | "
              f"{result['time_to_containment']:<12.4f} | {result['final_score']:<12.4f}")
    
    # Step 6: Save results and view leaderboard
    print_header("Leaderboard")
    
    # Save all results
    for strategy, result in results.items():
        attempt_id = competition.save_result(result)
        print(f"Saved {strategy} result with attempt ID: {attempt_id}")
    
    # Display the leaderboard
    leaderboard = competition.get_leaderboard()
    print("\nCurrent Leaderboard:")
    print(f"{'Rank':<5} | {'Player':<15} | {'Score':<10} | {'Scenario':<10} | {'Date':<20}")
    print("-" * 70)
    
    for entry in leaderboard:
        print(f"{entry['rank']:<5} | {entry['player_name']:<15} | {entry['score']:<10.4f} | "
              f"{entry['scenario_id']:<10} | {entry['attempt_date']}")
    
    # Save the leaderboard
    leaderboard_file = competition.save_leaderboard("demo_leaderboard.json")
    print(f"\nLeaderboard saved to: {leaderboard_file}")
    
    # Step 7: Export the best result
    best_result_file = competition.export_result(output_path="demo_best_result.json")
    print(f"Best result exported to: {best_result_file}")
    
    print_header("Demo Complete")
    print("This demonstration showed how to:")
    print("1. Register a player")
    print("2. Browse and select competition scenarios")
    print("3. Run simulations with different strategies")
    print("4. Compare results across strategies")
    print("5. Save results and view the leaderboard")
    print("6. Export data for further analysis")
    print("\nFor more information, refer to the competition documentation.")

if __name__ == "__main__":
    main()