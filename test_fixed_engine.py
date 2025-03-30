#!/usr/bin/env python3
"""
Test script to verify fixes to the MockEngine and simulation integration.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from src.competition.testing.engine_adapter import MockEngine
from src.competition.services.simulation_integration import SimulationIntegration

def simple_strategy(engine):
    """A simple test strategy."""
    engine.set_lockdown_level(0.5)
    engine.allocate_resources('healthcare', 200)
    engine.allocate_resources('research', 100)
    
    def step_callback(step, state):
        if step % 20 == 0:
            print(f"Step {step}: Infected: {state.population.infected}, Economy: {state.economy.current_gdp}")
    
    engine.register_step_callback(step_callback)

def main():
    print("Creating test engine...")
    engine = MockEngine(name="TestEngine")
    
    # Add some randomized values
    engine.metrics["population"]["infected"] = 150
    engine.metrics["economy"]["initial_gdp"] = 1200
    engine.metrics["economy"]["current_gdp"] = 1200
    
    # Create simulation integration
    print("Setting up simulation...")
    simulation = SimulationIntegration(engine=engine)
    
    # Apply strategy
    print("Applying strategy...")
    simple_strategy(engine)
    
    # Run simulation
    print("\nRunning simulation for 100 steps...")
    results = simulation.run_simulation(steps=100)
    
    # Display results
    print("\nSimulation complete!")
    print(f"Initial population: {results['initial_population']}")
    print(f"Final population: {results['final_population']}")
    print(f"Deaths: {results['dead_population']}")
    print(f"Initial GDP: {results['initial_gdp']}")
    print(f"Final GDP: {results['final_gdp']}")
    print(f"Max infection rate: {results['max_infection_rate']:.2%}")
    print(f"Resources spent: {results['total_resources_spent']}")
    print(f"Containment step: {results['containment_step']}")
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    main() 