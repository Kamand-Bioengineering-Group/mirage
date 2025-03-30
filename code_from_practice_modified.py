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
from IPython.display import display, HTML

# Set up visualization
plt.style.use('seaborn-whitegrid')
sns.set(font_scale=1.2)
pd.set_option('display.max_columns', None)

# Set random seed for reproducibility
import random
random.seed(None)  # Use variable seed for more randomness

# Create an epidemic engine with increased randomness
engine = MockEngine()

# Modify engine parameters to amplify differences
# Make lockdowns and economic investments much more impactful
engine.intervention_effects["lockdown_r0_reduction"] = 0.98  # Increased impact (was 0.85)
engine.intervention_effects["economic_support_efficiency"] = 0.98  # Increased impact (was 0.9)
engine.intervention_effects["healthcare_mortality_reduction"] = 0.98  # Increased impact (was 0.9)
engine.intervention_effects["research_effectiveness"] = 0.015  # Increased impact (was 0.008)

# Introduce more variability
engine.disease_params["r0_base"] = 3.5  # Increased from 3.0
engine.disease_params["mortality_rate_base"] = 0.03  # Increased from 0.02

# Create competition manager with a practice data directory
competition = CompetitionManager(data_dir="practice_data_random", engine=engine)

# Register as a player
player_name = "Test Player"
player_id = competition.setup_player(name=player_name)
print(f"Player registered: {player_name} (ID: {player_id})")

# Ensure we're in practice mode
competition.toggle_practice_mode(is_practice=True)
print("Mode set to: Practice")

# List available scenarios
competition.list_available_scenarios()

# Select the scenario to use - the challenging one for more differentiation
scenario_id = "challenging"
competition.set_scenario(scenario_id)
competition.display_scenario_details()

# Define Strategy 1: Extreme Lockdown
def extreme_lockdown(engine):
    """
    Extreme lockdown strategy with total focus on disease containment.
    
    Features:
    - Maximum lockdown from day one
    - All resources to healthcare
    - Complete travel ban
    - No economic support
    """
    # Initial setup - extreme containment
    engine.set_lockdown_level(1.0)  # 100% lockdown severity
    engine.allocate_resources('healthcare', 650)  # Almost all resources to healthcare
    engine.restrict_travel(True)  # Full travel ban
    
    # Define a callback for dynamic response
    def monitor_and_respond(step, state):
        infection_rate = state.population.infected / state.population.total
        
        # Maintain extreme measures until near elimination
        if infection_rate > 0.0005:  # Continue until virtually eliminated
            engine.set_lockdown_level(1.0)
            if step % 15 == 0:  # Periodically add more healthcare resources
                engine.allocate_resources('healthcare', 50)
        else:
            # Only if infection is almost eliminated, slightly reduce measures
            engine.set_lockdown_level(0.9)
            if step > 300:  # Very late in the pandemic
                engine.allocate_resources('economic', 50)  # Minimal economic support
    
    # Register the callback
    engine.register_step_callback(monitor_and_respond)

# Define Strategy 2: Economy Only
def economy_only(engine):
    """
    Strategy with absolutely no restrictions and total economic focus.
    
    Features:
    - Zero lockdown
    - All resources to economy
    - No travel restrictions
    - No healthcare investment
    """
    # Initial setup - zero restrictions
    engine.set_lockdown_level(0.0)  # No lockdown
    engine.allocate_resources('economic', 650)  # Almost all resources to economy
    engine.restrict_travel(False)  # No travel restrictions
    
    # Define a callback for dynamic response
    def monitor_and_respond(step, state):
        infection_rate = state.population.infected / state.population.total
        
        # No matter what, focus on economy
        if infection_rate > 0.35:  # Only if catastrophic infection rate
            engine.set_lockdown_level(0.1)  # Minimal restrictions
            engine.allocate_resources('healthcare', 50)  # Token healthcare
        else:
            # Maintain economic focus
            engine.set_lockdown_level(0.0)
            if step % 15 == 0:  # Periodically add economic support
                engine.allocate_resources('economic', 50)
    
    # Register the callback
    engine.register_step_callback(monitor_and_respond)

# Define Strategy 3: Adaptive Strategy
def adaptive_strategy(engine):
    """
    Highly adaptive strategy that changes dramatically based on conditions.
    
    Features:
    - Different phases with distinct approaches
    - Reacts to both infection rates and economic conditions
    - Strategic travel restrictions
    - Balanced resource allocation that shifts over time
    """
    # Initial setup - moderate-high measures
    engine.set_lockdown_level(0.7)  # Significant initial lockdown
    engine.allocate_resources('healthcare', 300)  # Initial healthcare focus
    engine.allocate_resources('economic', 200)  # Some economic support
    engine.restrict_travel(True)  # Initial travel ban
    
    # Define a callback for dynamic response
    def monitor_and_respond(step, state):
        infection_rate = state.population.infected / state.population.total
        economic_health = state.economy.current_gdp / state.economy.initial_gdp
        
        # Early phase - strong containment (0-60 days)
        if step < 60:
            if infection_rate > 0.08:
                engine.set_lockdown_level(0.8)
                engine.allocate_resources('healthcare', 70)
            elif infection_rate > 0.03:
                engine.set_lockdown_level(0.6)
                engine.allocate_resources('healthcare', 50)
                engine.allocate_resources('economic', 20)
            else:
                engine.set_lockdown_level(0.5)
                engine.allocate_resources('economic', 50)
                
        # Middle phase - balance with economic focus (60-180 days)
        elif 60 <= step < 180:
            if infection_rate > 0.1:
                engine.set_lockdown_level(0.7)
                engine.allocate_resources('healthcare', 60)
            elif economic_health < 0.6:  # Economy struggling badly
                engine.set_lockdown_level(0.3)
                engine.allocate_resources('economic', 100)
                engine.restrict_travel(False)
            else:
                engine.set_lockdown_level(0.5)
                engine.allocate_resources('healthcare', 40)
                engine.allocate_resources('economic', 60)
                engine.restrict_travel(infection_rate > 0.03)
                
        # Late phase - recovery and targeted controls (180+ days)
        else:
            if infection_rate < 0.01:
                engine.set_lockdown_level(0.2)
                engine.allocate_resources('economic', 80)
                engine.restrict_travel(False)
            elif economic_health < 0.5:  # Severe economic problems
                engine.set_lockdown_level(0.3)
                engine.allocate_resources('economic', 120)
                engine.restrict_travel(False)
            else:
                engine.set_lockdown_level(0.4)
                engine.allocate_resources('healthcare', 30)
                engine.allocate_resources('economic', 40)
                engine.restrict_travel(infection_rate > 0.05)
    
    # Register the callback
    engine.register_step_callback(monitor_and_respond)

# Define Strategy 4: Research Priority
def research_priority(engine):
    """
    Strategy that prioritizes research above all else.
    
    Features:
    - Massive investment in research
    - Moderate containment to buy time
    - Transition to economic focus after research breakthrough
    - Very dynamic response based on research progress
    """
    # Initial setup - focus on research and moderate containment
    engine.set_lockdown_level(0.6)  # Significant lockdown to slow spread
    engine.allocate_resources('research', 500)  # Massive research focus
    engine.allocate_resources('healthcare', 150)  # Some healthcare
    engine.restrict_travel(True)  # Travel restrictions
    
    # Define a callback for dynamic response
    def monitor_and_respond(step, state):
        infection_rate = state.population.infected / state.population.total
        research_progress = state.research.progress
        
        # Research phase - continue heavy investment
        if research_progress < 0.7:  # Until research milestone
            if step % 10 == 0:  # Regularly invest in research
                engine.allocate_resources('research', 80)
            
            # Maintain containment to buy time
            if infection_rate > 0.15:
                engine.set_lockdown_level(0.8)
                engine.allocate_resources('healthcare', 50)
            else:
                engine.set_lockdown_level(0.6)
        
        # Post-research phase - leverage breakthrough
        else:
            # After research milestones, cut lockdown and focus on economy
            if infection_rate > 0.08:
                engine.set_lockdown_level(0.5)
                engine.allocate_resources('healthcare', 80)
            else:
                engine.set_lockdown_level(0.3)
                engine.allocate_resources('economic', 100)
                engine.restrict_travel(False)
    
    # Register the callback
    engine.register_step_callback(monitor_and_respond)

# List of strategies to compare
strategies = [
    ("Extreme Lockdown", extreme_lockdown),
    ("Economy Only", economy_only),
    ("Adaptive Strategy", adaptive_strategy),
    ("Research Priority", research_priority)
]

# Dictionary to store results
all_results = {}

# Run each strategy multiple times for better comparison
num_runs = 3  # Run each strategy 3 times
all_runs = {}

for strategy_name, strategy_func in strategies:
    strategy_results = []
    
    for run in range(num_runs):
        # Reset simulation
        competition.setup_simulation()
        
        # Run with this strategy
        print(f"\nRunning {strategy_name} - Run {run+1}/{num_runs}")
        result = competition.run_simulation(steps=365, interventions=[strategy_func])
        
        # Store the result
        strategy_results.append({
            'Run': run+1,
            'Population Survived': result.get('population_survived', 0),
            'GDP Preserved': result.get('gdp_preserved', 0),
            'Infection Control': result.get('infection_control', 0),
            'Resource Efficiency': result.get('resource_efficiency', 0),
            'Time to Containment': result.get('time_to_containment', 0),
            'Final Score': result.get('final_score', 0)
        })
        
        # Display individual score
        competition.display_score(result)
    
    # Store all runs for this strategy
    all_runs[strategy_name] = strategy_results
    
    # Calculate average results for this strategy
    avg_result = {
        'Population Survived': np.mean([r['Population Survived'] for r in strategy_results]),
        'GDP Preserved': np.mean([r['GDP Preserved'] for r in strategy_results]),
        'Infection Control': np.mean([r['Infection Control'] for r in strategy_results]),
        'Resource Efficiency': np.mean([r['Resource Efficiency'] for r in strategy_results]),
        'Time to Containment': np.mean([r['Time to Containment'] for r in strategy_results]),
        'Final Score': np.mean([r['Final Score'] for r in strategy_results])
    }
    
    # Add to results dictionary
    all_results[strategy_name] = avg_result

# Create comparison dataframe of averages
comparison_df = pd.DataFrame(all_results)

# Display comparison table of averages
print("\n=== Strategy Comparison (Averages Over Multiple Runs) ===\n")
print(comparison_df)

# Calculate standard deviations to show variability
std_devs = {}
for strategy_name, runs in all_runs.items():
    std_devs[strategy_name] = {
        'Population Survived': np.std([r['Population Survived'] for r in runs]),
        'GDP Preserved': np.std([r['GDP Preserved'] for r in runs]),
        'Infection Control': np.std([r['Infection Control'] for r in runs]),
        'Resource Efficiency': np.std([r['Resource Efficiency'] for r in runs]),
        'Time to Containment': np.std([r['Time to Containment'] for r in runs]),
        'Final Score': np.std([r['Final Score'] for r in runs])
    }

std_df = pd.DataFrame(std_devs)
print("\n=== Variability (Standard Deviation) ===\n")
print(std_df)

# Visualize the comparison (excluding final score)
metrics_df = comparison_df.drop('Final Score')

# Create bar chart
plt.figure(figsize=(14, 8))
metrics_df.plot(kind='bar', figsize=(14, 8))
plt.title('Strategy Comparison by Metric (Averaged)', fontsize=16)
plt.ylabel('Score (0-1 scale)', fontsize=14)
plt.xlabel('Metric', fontsize=14)
plt.xticks(rotation=45)
plt.grid(axis='y', alpha=0.3)
plt.legend(title='Strategy', fontsize=12)
plt.tight_layout()
plt.savefig('strategy_comparison_avg.png')
plt.show()

# Create a radar chart for multi-dimensional comparison
plt.figure(figsize=(10, 10))
ax = plt.subplot(111, polar=True)

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
plt.savefig('strategy_radar_chart.png')
plt.show()

# Display all your practice attempts
competition.display_player_attempts()

# Print out strategy analysis with key findings
print("\n=== Strategy Analysis ===\n")
best_strategy = comparison_df.loc['Final Score'].idxmax()
best_score = comparison_df.loc['Final Score'].max()
print(f"Best Overall Strategy: {best_strategy} (Score: {best_score:.4f})")

# Analyze each metric
for metric in metrics_df.index:
    best_for_metric = metrics_df.loc[metric].idxmax()
    print(f"Best for {metric}: {best_for_metric} (Score: {metrics_df.loc[metric, best_for_metric]:.4f})")

# Calculate score differences
max_score = comparison_df.loc['Final Score'].max()
min_score = comparison_df.loc['Final Score'].min()
score_difference = max_score - min_score

# Final conclusion
print("\nKey Findings:")
print(f"1. Different strategies produce significantly different results (score range: {score_difference:.4f})")
print("2. There are clear trade-offs between health outcomes and economic preservation")
print("3. The optimal strategy depends on which metrics are most valued")
print("4. An adaptive approach with dynamic adjustment based on conditions typically performs well")
print(f"5. There is variability in results even with the same strategy (randomness in simulation)")

# Now let's compare with the original engine
print("\n=== Now comparing with original engine (this won't work, explanation below) ===")
print("The XPECTO platform uses a MockEngine for practice mode testing.")
print("The original engine would be the actual epidemic simulation model used in the full system.")
print("In a real-world scenario, differences between the mock and original engine might include:")
print("1. More complex disease dynamics (network-based spread, geographic factors)")
print("2. More detailed population models (age demographics, vulnerability factors)")
print("3. More realistic economic models (sector-by-sector impacts)")
print("4. More nuanced intervention effects (diminishing returns, compliance factors)")
print("5. Higher computational requirements for the original engine")
print("\nTo compare these engines, we would need access to both, which isn't available in this setup.") 