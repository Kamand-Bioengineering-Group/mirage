import sys
from pathlib import Path
import pandas as pd
sys.path.append(str(Path('../').resolve()))

from src.competition.testing.enhanced_engine import EnhancedEngine
from src.competition.competition_manager import CompetitionManager

# Create instances
engine = EnhancedEngine()
manager = CompetitionManager(data_dir='practice_data', engine=engine)

# Set up player and simulation
manager.setup_player('Test Player')
manager.toggle_practice_mode(True)
manager.set_scenario('standard')
manager.setup_simulation()

# Define strategies to test

# Strategy 1: Balanced approach
def balanced_strategy(engine):
    engine.set_lockdown_level(0.5)
    engine.allocate_resources('healthcare', 400)
    engine.allocate_resources('economic', 300)
    engine.allocate_resources('research', 200)
    
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

# Strategy 2: Health-focused
def health_focused_strategy(engine):
    engine.set_lockdown_level(0.7)
    engine.allocate_resources('healthcare', 650)
    engine.restrict_travel(True)
    
    def monitor_and_respond(step, state):
        # Ensure we never divide by zero
        total_population = max(1, state.population.total)
        infection_rate = state.population.infected / total_population
        if infection_rate < 0.05:
            engine.set_lockdown_level(0.5)
            engine.allocate_resources('economic', 50)
    
    engine.register_step_callback(monitor_and_respond)

# Strategy 3: Economy-focused
def economy_focused_strategy(engine):
    engine.set_lockdown_level(0.3)
    engine.allocate_resources('economic', 600)
    engine.restrict_travel(False)
    
    def monitor_and_respond(step, state):
        # Ensure we never divide by zero
        total_population = max(1, state.population.total)
        infection_rate = state.population.infected / total_population
        if infection_rate > 0.15:
            engine.set_lockdown_level(0.5)
            engine.allocate_resources('healthcare', 100)
    
    engine.register_step_callback(monitor_and_respond)

# Strategy 4: Research-focused
def research_focused_strategy(engine):
    engine.set_lockdown_level(0.4)
    engine.allocate_resources('research', 500)
    engine.allocate_resources('healthcare', 300)
    
    def monitor_and_respond(step, state):
        if state.research.progress > 0.5:
            engine.allocate_resources('economic', 100)
    
    engine.register_step_callback(monitor_and_respond)

# Test all strategies and compare results
print("===== Enhanced Scoring System Demonstration =====")
results = []

# Run each strategy
for strategy_name, strategy_func in [
    ("Balanced", balanced_strategy),
    ("Health-Focused", health_focused_strategy),
    ("Economy-Focused", economy_focused_strategy),
    ("Research-Focused", research_focused_strategy)
]:
    print(f"\nTesting {strategy_name} strategy...")
    manager.setup_simulation()  # Reset simulation
    strategy_results = manager.run_simulation(365, [strategy_func])
    
    # Store results for comparison
    results.append({
        'Strategy': strategy_name,
        'Final Score': strategy_results.get('final_score', 0),
        'Raw Score': strategy_results.get('raw_score', 0),
        'Population Survived': strategy_results.get('population_survived', 0),
        'GDP Preserved': strategy_results.get('gdp_preserved', 0),
        'Infection Control': strategy_results.get('infection_control', 0)
    })

# Display comparison table
print("\n===== Strategy Comparison =====")
results_df = pd.DataFrame(results)
results_df = results_df.sort_values('Final Score', ascending=False)
print(results_df)