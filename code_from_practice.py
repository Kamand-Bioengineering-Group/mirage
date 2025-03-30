#!/usr/bin/env python3

# Add the project root to the path
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path.cwd().parent))

# Import required modules
from src.competition import CompetitionManager
from src.competition.testing.engine_adapter import MockEngine

# Import visualization libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import src.competition.utils as utils

# Set up visualization
plt.style.use('seaborn-whitegrid')
sns.set(font_scale=1.2)
pd.set_option('display.max_columns', None)

# Create an epidemic engine
engine = MockEngine()

# Create competition manager with a practice data directory
competition = CompetitionManager(data_dir="practice_data", engine=engine)

# Register as a player - use your real name for consistent tracking
player_name = "Your Name"  # Change this to your name
player_id = competition.setup_player(name=player_name)
print(f"Registered as player: {player_name} (ID: {player_id})")

# Ensure we're in practice mode
competition.toggle_practice_mode(is_practice=True)
print("Practice mode enabled - attempts will not count for competition")

# List available scenarios
competition.list_available_scenarios()

# Select the scenario to use
scenario_id = "standard"  # Options: "standard", "challenging", etc.
competition.set_scenario(scenario_id)
competition.display_scenario_details()

# Define your intervention strategy here
def my_strategy(engine):
    """
    My custom epidemic intervention strategy.
    
    This is a template strategy - modify it to implement your approach!
    """
    # Initial setup - moderate measures
    engine.set_lockdown_level(0.5)  # 50% lockdown severity
    engine.allocate_resources('healthcare', 200)  # Allocate resources to healthcare
    
    # Define a callback for dynamic response
    def monitor_and_respond(step, state):
        # Calculate current infection rate
        infection_rate = state.population.infected / state.population.total
        
        # Use current_gdp instead of gdp
        economic_health = state.economy.current_gdp / state.economy.initial_gdp
        
        # Early phase - containment focus
        if step < 50:
            if infection_rate > 0.05:  # If infection rate rises early
                engine.set_lockdown_level(0.7)  # Increase restrictions
                engine.allocate_resources('healthcare', 300)  # Boost healthcare
            else:
                engine.set_lockdown_level(0.4)  # Moderate restrictions
                engine.allocate_resources('healthcare', 150)  # Moderate healthcare
                
        # Middle phase (50-200) - targeted response
        elif 50 <= step < 200:
            if infection_rate > 0.1:  # High infection rate
                engine.set_lockdown_level(0.8)  # Strong lockdown
                engine.allocate_resources('healthcare', 350)  # Major healthcare
            elif infection_rate > 0.05:  # Moderate infection rate
                engine.set_lockdown_level(0.6)  # Significant restrictions
                engine.allocate_resources('healthcare', 250)  # Enhanced healthcare
                engine.allocate_resources('economic', 100)  # Some economic support
            else:  # Low infection rate
                engine.set_lockdown_level(0.3)  # Reduced restrictions 
                engine.allocate_resources('healthcare', 150)  # Maintain healthcare
                engine.allocate_resources('economic', 200)  # Focus on economy
                
        # Late phase (200+) - recovery focus if controlled
        else:
            if infection_rate < 0.01:  # Very low infection rate
                engine.set_lockdown_level(0.2)  # Minimal restrictions
                engine.allocate_resources('economic', 300)  # Economic recovery
                engine.allocate_resources('healthcare', 100)  # Maintenance healthcare
            elif infection_rate < 0.05:  # Low infection rate
                engine.set_lockdown_level(0.4)  # Moderate restrictions
                engine.allocate_resources('economic', 200)  # Economic support
                engine.allocate_resources('healthcare', 150)  # Moderate healthcare
            else:  # Still significant infection
                engine.set_lockdown_level(0.6)  # Maintain restrictions
                engine.allocate_resources('healthcare', 250)  # Prioritize healthcare
                engine.allocate_resources('economic', 150)  # Some economic support
    
    # Register the callback
    engine.register_step_callback(monitor_and_respond)

# Set up the simulation
competition.setup_simulation()

# Run the simulation with your strategy
results = competition.run_simulation(
    steps=365,  # Simulate for 1 year (you can change this)
    interventions=[my_strategy]  # Specify which strategy to use
)

# Display the results
print(f"\nResults for {scenario_id} scenario using 'my_strategy':")
competition.display_score(results)

# List of strategies to compare
strategies = [
    ("Custom Strategy", my_strategy),
    ("Aggressive Lockdown", utils.aggressive_containment),
    ("Economy Focused", utils.economic_focus)
]

# Dictionary to store results
all_results = {}

# Run each strategy
for name, strategy in strategies:
    # Reset simulation
    competition.setup_simulation()
    
    # Run with this strategy
    print(f"\nRunning simulation with strategy: {name}")
    result = competition.run_simulation(steps=365, interventions=[strategy])
    
    # Store results
    all_results[name] = {
        'Population Survived': result.get('population_survived', 0),
        'GDP Preserved': result.get('gdp_preserved', 0),
        'Infection Control': result.get('infection_control', 0),
        'Resource Efficiency': result.get('resource_efficiency', 0),
        'Time to Containment': result.get('time_to_containment', 0),
        'Final Score': result.get('final_score', 0)
    }
    
    # Display individual score
    competition.display_score(result)

# Create comparison dataframe
comparison_df = pd.DataFrame(all_results)

# Display comparison table
print("\n=== Strategy Comparison ===\n")
print(comparison_df)

# Visualize the comparison (excluding final score)
metrics_df = comparison_df.drop('Final Score')

# Create bar chart
ax = metrics_df.plot(kind='bar', figsize=(14, 8))
plt.title('Strategy Comparison by Metric', fontsize=16)
plt.ylabel('Score (0-1 scale)', fontsize=14)
plt.xlabel('Metric', fontsize=14)
plt.xticks(rotation=45)
plt.grid(axis='y', alpha=0.3)
plt.legend(title='Strategy', fontsize=12)

# Add value labels on bars
for container in ax.containers:
    ax.bar_label(container, fmt='%.2f', fontsize=10)

plt.tight_layout()
plt.show()

# Create a radar chart for multi-dimensional comparison
fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, polar=True)

# Prepare data for radar chart
categories = metrics_df.index.tolist()
N = len(categories)
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]  # Close the loop

# Draw one line per strategy
for strategy in metrics_df.columns:
    values = metrics_df[strategy].values.tolist()
    values += values[:1]  # Close the loop
    ax.plot(angles, values, linewidth=2, label=strategy)
    ax.fill(angles, values, alpha=0.1)

# Set category labels
plt.xticks(angles[:-1], categories, size=12)

# Draw y-axis lines and labels
ax.set_rlabel_position(0)
plt.yticks([0.2, 0.4, 0.6, 0.8], ["0.2", "0.4", "0.6", "0.8"], size=10)
plt.ylim(0, 1)

# Add title and legend
plt.title('Strategy Comparison - Multi-dimensional View', size=15)
plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))

plt.tight_layout()
plt.show()

# Display all your practice attempts
competition.display_player_attempts()

strategy_notes = """
Strategy Name: My Custom Strategy

Key Approach:
- Dynamic response based on infection rate and simulation phase
- Strong early response to prevent initial spread
- Economic recovery focus once infections are under control

Observations:
- Strategy performs well in containing the infection
- GDP preservation could be improved
- Resource efficiency needs optimization

Ideas for Improvement:
- Fine-tune thresholds for different phases
- Better balance between healthcare and economic resources
- More gradual transitions between lockdown levels
"""

print(strategy_notes)

# Commented code for cleaning up practice data
# import shutil
# shutil.rmtree("practice_data", ignore_errors=True)
# print("Practice data removed. Restart the notebook to create new data.")
