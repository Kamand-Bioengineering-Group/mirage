"""
Competition Demo Script

This script demonstrates how to use the competition API to
create and submit competition attempts.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.competition.api import CompetitionAPI
from src.competition.utils.utils_functions import create_randomized_engine

def main():
    """Run a competition demo."""
    print("=" * 80)
    print(" XPECTO Epidemic 2.0 Competition Demo ".center(80, "="))
    print("=" * 80)
    
    # Initialize the competition API
    competition = CompetitionAPI(storage_dir="./competition_data")
    
    # Register a player
    player = competition.register_player(
        name="Demo Player",
        email="demo@example.com"
    )
    print(f"\nPlayer registered: {player.name} (ID: {player.id})")
    
    # Create a scenario
    scenario = competition.create_scenario(
        name="Standard Scenario",
        description="A balanced scenario for testing",
        seed=12345,
        r0=2.5,
        initial_infections=100,
        initial_resources=5000,
        difficulty="standard"
    )
    print(f"\nScenario created: {scenario.name} (ID: {scenario.id})")
    
    # Create a randomized engine
    engine = create_randomized_engine(seed=scenario.seed, difficulty=scenario.difficulty)
    print("\nRandomized engine created with the following parameters:")
    print(f"- R0: {engine.disease_params['r0_base']:.2f}")
    print(f"- Initial infections: {engine.metrics['population']['infected']}")
    print(f"- Initial resources: {engine.metrics['resources']['available']}")
    
    # Define a basic strategy
    def demo_strategy(engine):
        """A simple demo strategy."""
        # Initial measures
        engine.set_lockdown_level(0.5)
        engine.allocate_resources('healthcare', 200)
        engine.restrict_travel(True)
        
        def step_callback(step, state):
            """Adapt strategy based on infection rate."""
            infection_rate = state.population.infected / state.population.total
            
            if infection_rate > 0.1:
                engine.set_lockdown_level(0.7)
                engine.allocate_resources('healthcare', 300)
            elif infection_rate < 0.05:
                engine.set_lockdown_level(0.3)
                engine.allocate_resources('economic', 200)
                if infection_rate < 0.01:
                    engine.restrict_travel(False)
        
        engine.register_step_callback(step_callback)
    
    # Apply the strategy
    print("\nApplying demo strategy...")
    demo_strategy(engine)
    
    # Run the simulation
    print("\nRunning simulation for 200 steps...")
    engine.run(200)
    
    # Get final metrics
    metrics = engine.metrics
    print("\nSimulation completed with the following results:")
    print(f"- Population survived: {(metrics['population']['total'] - metrics['population']['dead']) / metrics['population']['total']:.2%}")
    print(f"- GDP preserved: {metrics['economy']['current_gdp'] / metrics['economy']['initial_gdp']:.2%}")
    print(f"- Max infection rate: {metrics['max_infection_rate']:.2%}")
    
    # Submit the attempt
    attempt = competition.submit_attempt(
        player_id=player.id,
        scenario_id=scenario.id,
        engine_state={"metrics": metrics},
        is_practice=False
    )
    print(f"\nAttempt submitted (ID: {attempt.id})")
    
    # Show the result
    if attempt.result:
        print("\nScores:")
        print(f"- Population survived: {attempt.result.population_survived:.4f}")
        print(f"- GDP preserved: {attempt.result.gdp_preserved:.4f}")
        print(f"- Infection control: {attempt.result.infection_control:.4f}")
        print(f"- Resource efficiency: {attempt.result.resource_efficiency:.4f}")
        print(f"- Time to containment: {attempt.result.time_to_containment:.4f}")
        print(f"- Final score: {attempt.result.final_score:.4f}")
    
    # Display leaderboard
    leaderboard = competition.get_leaderboard()
    print("\nCurrent Leaderboard:")
    print("-" * 80)
    for i, entry in enumerate(leaderboard):
        print(f"{i+1}. {entry['player_name']}: {entry['score']:.4f}")
    print("-" * 80)
    
    print("\nDemo completed successfully!")

if __name__ == "__main__":
    main() 