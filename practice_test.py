import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Add project root to system path
sys.path.append(os.path.abspath(os.path.join(os.getcwd())))

# Import necessary modules
from src.competition import CompetitionManager
from src.competition.testing.engine_adapter import MockEngine

# Set up the competition system
mock_engine = MockEngine()
competition = CompetitionManager(data_dir="data", engine=mock_engine)
player_id = competition.setup_player(name="test_player")
competition.toggle_practice_mode(is_practice=True)

# Function to run simulation and return results
print("Running multiple strategies to test randomization...")

# Set the scenario to use
competition.set_scenario("standard")

def run_strategy(strategy_func, strategy_name, num_runs=5):
    """
    Run a strategy multiple times and collect results
    """
    results = []
    
    for i in range(num_runs):
        print(f"Running {strategy_name} - Attempt {i+1}/{num_runs}")
        # Reset the simulation for each run
        competition.setup_simulation()
        
        sim_results = competition.run_simulation(
            steps=365,
            interventions=[strategy_func]
        )
        
        # Extract metrics from the results dictionary
        results.append({
            "strategy": strategy_name,
            "attempt": i+1,
            "score": sim_results.get("final_score", 0),
            "population_survived": sim_results.get("population_survived", 0),
            "gdp_preserved": sim_results.get("gdp_preserved", 0),
            "infection_control": sim_results.get("infection_control", 0),
            "resource_efficiency": sim_results.get("resource_efficiency", 0),
            "time_to_containment": sim_results.get("time_to_containment", 0)
        })
        
    return results

# Define different strategies to test

# Strategy 1: Aggressive Lockdown
def aggressive_lockdown(engine):
    """
    Implement an aggressive lockdown strategy with high emphasis on containment
    """
    # Initial setup - severe lockdown
    engine.set_lockdown_level(0.8)  # 80% lockdown severity
    engine.allocate_resources('healthcare', 400)  # Heavy healthcare focus
    
    # Define a callback for dynamic response
    def monitor_and_respond(step, state):
        infection_rate = state.population.infected / state.population.total
        
        if infection_rate > 0.1:  # High infection rate
            engine.set_lockdown_level(0.9)  # Extreme lockdown
            engine.allocate_resources('healthcare', 500)  # Maximum healthcare
        elif infection_rate > 0.05:  # Moderate infection rate
            engine.set_lockdown_level(0.7)  # Strong lockdown
            engine.allocate_resources('healthcare', 350)  # Major healthcare
        elif infection_rate > 0.01:  # Low infection rate
            engine.set_lockdown_level(0.5)  # Moderate restrictions
            engine.allocate_resources('healthcare', 250)  # Maintain healthcare
            engine.allocate_resources('economic', 100)  # Some economic support
        else:  # Very low infection rate
            engine.set_lockdown_level(0.3)  # Reduced restrictions
            engine.allocate_resources('healthcare', 150)  # Basic healthcare
            engine.allocate_resources('economic', 200)  # Economic focus
    
    # Register the callback
    engine.register_step_callback(monitor_and_respond)

# Strategy 2: Balanced Approach
def balanced_approach(engine):
    """
    Implement a balanced approach between health and economy
    """
    # Initial setup - moderate measures
    engine.set_lockdown_level(0.5)  # 50% lockdown severity
    engine.allocate_resources('healthcare', 200)  # Moderate healthcare 
    engine.allocate_resources('economic', 100)  # Some economic support
    
    # Define a callback for dynamic response
    def monitor_and_respond(step, state):
        infection_rate = state.population.infected / state.population.total
        economic_health = state.economy.current_gdp / state.economy.initial_gdp
        
        if infection_rate > 0.1:  # High infection rate
            engine.set_lockdown_level(0.7)  # Strong lockdown
            engine.allocate_resources('healthcare', 300)  # Major healthcare
            engine.allocate_resources('economic', 100)  # Minimal economic support
        elif infection_rate > 0.05:  # Moderate infection rate
            engine.set_lockdown_level(0.5)  # Moderate lockdown
            engine.allocate_resources('healthcare', 200)  # Good healthcare
            engine.allocate_resources('economic', 150)  # Balanced economic support
        else:  # Low infection rate
            engine.set_lockdown_level(0.3)  # Light restrictions
            engine.allocate_resources('healthcare', 150)  # Basic healthcare
            engine.allocate_resources('economic', 250)  # Strong economic focus
    
    # Register the callback
    engine.register_step_callback(monitor_and_respond)

# Strategy 3: Economy Focused
def economy_focused(engine):
    """
    Implement an economy-focused approach with minimal restrictions
    """
    # Initial setup - light measures
    engine.set_lockdown_level(0.3)  # 30% lockdown severity
    engine.allocate_resources('healthcare', 150)  # Basic healthcare 
    engine.allocate_resources('economic', 300)  # Heavy economic focus
    
    # Define a callback for dynamic response
    def monitor_and_respond(step, state):
        infection_rate = state.population.infected / state.population.total
        
        if infection_rate > 0.15:  # Critical infection rate
            engine.set_lockdown_level(0.6)  # Increased restrictions
            engine.allocate_resources('healthcare', 300)  # Increased healthcare
            engine.allocate_resources('economic', 150)  # Reduced economic focus
        elif infection_rate > 0.1:  # High infection rate
            engine.set_lockdown_level(0.4)  # Moderate restrictions
            engine.allocate_resources('healthcare', 200)  # Moderate healthcare
            engine.allocate_resources('economic', 250)  # Maintained economic focus
        else:  # Manageable infection rate
            engine.set_lockdown_level(0.2)  # Minimal restrictions
            engine.allocate_resources('healthcare', 100)  # Basic healthcare
            engine.allocate_resources('economic', 400)  # Maximum economic focus
    
    # Register the callback
    engine.register_step_callback(monitor_and_respond)

# Run the strategies and collect results

# Run each strategy multiple times
results1 = run_strategy(aggressive_lockdown, "Aggressive Lockdown")
results2 = run_strategy(balanced_approach, "Balanced Approach")
results3 = run_strategy(economy_focused, "Economy Focused")

# Combine results
all_results = pd.DataFrame(results1 + results2 + results3)

# Save results to CSV
all_results.to_csv("strategy_comparison_results.csv", index=False)

# Create boxplot visualization
plt.figure(figsize=(10, 8))
all_results.boxplot(column='score', by='strategy')
plt.title('Score Distribution by Strategy')
plt.suptitle('')  # Remove default pandas boxplot title
plt.tight_layout()
plt.savefig('strategy_comparison.png')

# Create plots for key metrics
plt.figure(figsize=(14, 12))

# Population Survived
plt.subplot(3, 1, 1)
for strategy in all_results['strategy'].unique():
    strategy_data = all_results[all_results['strategy'] == strategy]
    attempts = strategy_data['attempt'].to_numpy()
    survived = strategy_data['population_survived'].to_numpy()
    plt.plot(attempts, survived, 'o-', label=strategy)
plt.ylabel('Population Survived')
plt.title('Variations in Metrics Across Runs')
plt.legend()

# GDP Preserved
plt.subplot(3, 1, 2)
for strategy in all_results['strategy'].unique():
    strategy_data = all_results[all_results['strategy'] == strategy]
    attempts = strategy_data['attempt'].to_numpy()
    gdp = strategy_data['gdp_preserved'].to_numpy()
    plt.plot(attempts, gdp, 'o-', label=strategy)
plt.ylabel('GDP Preserved')
plt.legend()

# Infection Control
plt.subplot(3, 1, 3)
for strategy in all_results['strategy'].unique():
    strategy_data = all_results[all_results['strategy'] == strategy]
    attempts = strategy_data['attempt'].to_numpy()
    infection = strategy_data['infection_control'].to_numpy()
    plt.plot(attempts, infection, 'o-', label=strategy)
plt.ylabel('Infection Control')
plt.xlabel('Run Number')
plt.legend()
plt.tight_layout()
plt.savefig('metrics_comparison.png')

print("\nAnalysis complete! Results saved to 'strategy_comparison_results.csv'")
print("Visualizations saved as 'strategy_comparison.png' and 'metrics_comparison.png'")

# Check if we get different scores for the same strategy with different randomization
for strategy in all_results['strategy'].unique():
    strategy_scores = all_results[all_results['strategy'] == strategy]['score']
    if strategy_scores.std() > 0:
        print(f"\n{strategy} shows variation in scores (std dev: {strategy_scores.std():.6f}) - RANDOMIZATION WORKING")
    else:
        print(f"\n{strategy} shows NO variation in scores - RANDOMIZATION NOT WORKING")

print("\nCONCLUSION:")
if all_results['score'].std() > 0:
    print("The simulation includes randomization, as demonstrated by the variation in scores.")
else:
    print("The simulation doesn't show evidence of randomization, as all attempts yielded identical scores.") 