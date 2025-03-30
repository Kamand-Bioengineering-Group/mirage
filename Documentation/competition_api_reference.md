# XPECTO Epidemic 2.0 Competition API Reference

This document provides a comprehensive reference for the Competition API, which allows you to interact with the XPECTO Epidemic 2.0 competition system.

## Table of Contents

- [Getting Started](#getting-started)
- [API Classes](#api-classes)
  - [CompetitionAPI](#competitionapi)
  - [CompetitionManager](#competitionmanager)
- [Core Functions](#core-functions)
  - [Player Management](#player-management)
  - [Scenario Management](#scenario-management)
  - [Simulation Control](#simulation-control)
  - [Results and Leaderboard](#results-and-leaderboard)
- [Callback System](#callback-system)
- [Examples](#examples)

## Getting Started

To use the competition API, you need to import it first:

```python
# Option 1: Use the singleton instance
from src.competition.api import competition_api

# Option 2: Create your own instance
from src.competition.api import CompetitionAPI
api = CompetitionAPI(data_dir="my_competition_data")
```

## API Classes

### CompetitionAPI

The `CompetitionAPI` class provides a simplified interface for interacting with the competition system. It wraps the more complex `CompetitionManager` class and exposes only the functions needed for typical usage.

```python
class CompetitionAPI:
    """Public API for the XPECTO Epidemic 2.0 Competition."""
    
    def __init__(self, data_dir: str = "competition_data", engine: Any = None):
        """
        Initialize the Competition API.
        
        Args:
            data_dir: Directory to store competition data
            engine: The simulation engine instance to use
        """
```

### CompetitionManager

The `CompetitionManager` class is the core of the competition system. It handles player registration, scenario management, simulation execution, and results tracking.

```python
class CompetitionManager:
    """
    Competition manager for the XPECTO Epidemic 2.0 simulation.
    
    This class manages players, scenarios, and simulation attempts,
    providing a complete competition system.
    """
```

## Core Functions

### Player Management

#### Register a Player

```python
# Register a player
player_id = api.register_player("Player Name")
```

#### Get Player Information

```python
# Get information about the current player
player_info = api.get_player_info()
```

#### Reset Player Data

```python
# Reset all data for the current player (use with caution!)
api.reset_player_data()
```

### Scenario Management

#### List Available Scenarios

```python
# Get a list of all available scenarios
scenarios = api.list_scenarios()
```

#### Get Scenario Details

```python
# Get detailed information about a specific scenario
scenario_details = api.get_scenario_details("standard")
```

#### Set Current Scenario

```python
# Set the active scenario
api.set_scenario("standard")
```

#### Get Remaining Attempts

```python
# Check how many official attempts you have remaining for the current scenario
remaining = api.get_remaining_attempts()

# Check attempts for a specific scenario
remaining = api.get_remaining_attempts("challenging")

# Check attempts for a specific player and scenario
remaining = api.get_remaining_attempts(player_id="player123", scenario_id="standard")
```

This function returns the number of official (non-practice) attempts remaining for a player on a specific scenario. By default, a maximum of 3 official attempts are allowed per scenario. The function will return a number between 0 and 3.

If no parameters are provided, it uses the current player and scenario.

**Parameters:**
- `player_id` (optional): The ID of the player to check. If not provided, uses the current player.
- `scenario_id` (optional): The ID of the scenario to check. If not provided, uses the current scenario.

**Returns:**
- An integer between 0 and 3 representing remaining attempts.

**Raises:**
- `ValueError`: If no player or scenario is specified and none is currently set.

### Simulation Control

#### Set Practice Mode

```python
# Enable practice mode (attempts don't count against your limit)
api.set_practice_mode(True)

# Disable practice mode (attempts count against your limit)
api.set_practice_mode(False)

# Check if currently in practice mode
is_practice = api.is_practice_mode()
```

Practice mode allows you to experiment and test your strategies without using up your limited number of official attempts. Each player has a maximum of 3 official attempts per scenario, but unlimited practice attempts.

When practice mode is enabled:
- Attempts don't count toward your official limit
- Results won't appear on the public leaderboard
- You can freely experiment with different strategies

When practice mode is disabled:
- Each attempt counts toward your official limit (maximum 3 per scenario)
- Results are recorded on the public leaderboard
- You should only submit your best strategies

**Note:** Practice mode is enabled by default when you initialize the competition API. You must explicitly disable it to make official submissions.

#### Run a Simulation

```python
# Define your strategy
def my_strategy(engine):
    engine.set_lockdown_level(0.5)
    engine.allocate_resources('healthcare', 100)
    
    def on_step(step, state):
        # Adapt strategy based on state
        pass
    
    engine.register_step_callback(on_step)

# Run the simulation with your strategy
results = api.run_simulation(
    interventions=[my_strategy],
    steps=365
)
```

#### Save a Result

```python
# Save the result of your simulation
attempt_id = api.save_result(results)
```

### Results and Leaderboard

#### Get Player Attempts

```python
# Get all attempts by the current player
attempts = api.get_player_attempts()

# Get attempts for a specific scenario
attempts = api.get_player_attempts(scenario_id="standard")

# Get only official (non-practice) attempts
attempts = api.get_player_attempts(official_only=True)
```

#### Understanding Simulation Results

When you run a simulation, the results contain several components:

```python
# Run the simulation with your strategy
results = api.run_simulation(interventions=[my_strategy])

# Results structure:
{
    'final_score': 0.82,                # Overall score (0-1 scale)
    'population_survived': 0.98,        # Percentage of population survived
    'gdp_preserved': 0.76,              # Percentage of GDP preserved
    'infection_control': 0.85,          # How well infection was contained
    'resource_efficiency': 0.71,        # How efficiently resources were used
    'time_to_containment': 0.73,        # How quickly epidemic was contained
    'metrics': {                        # Raw simulation metrics
        'population': {
            'total': 10000,             # Total population
            'susceptible': 9000,        # Susceptible individuals
            'infected': 100,            # Currently infected
            'recovered': 800,           # Recovered individuals
            'dead': 100                 # Deceased individuals
        },
        'economy': {
            'current_gdp': 950,         # Current GDP level
            'initial_gdp': 1000,        # Starting GDP
            'lockdown_impact': -50      # GDP loss from lockdown
        },
        'healthcare': {
            'capacity': 500,            # Healthcare capacity
            'usage': 100                # Current usage
        },
        'resources': {
            'available': 2000,          # Remaining resources
            'total_spent': 3000,        # Resources spent
            'total_initial': 5000       # Initial resources
        }
    }
}
```

The final score is calculated based on several weighted components:
- **Population Survived (30%)**: Percentage of population that survived
- **GDP Preserved (20%)**: Economic health preserved throughout the epidemic
- **Infection Control (20%)**: How well the infection was contained
- **Resource Efficiency (15%)**: How efficiently resources were used
- **Time to Containment (15%)**: How quickly the epidemic was contained

Each component is normalized to a 0-1 scale, with higher values being better.

#### Get Detailed Metrics

```python
# Get detailed metrics for a specific attempt
metrics = api.get_detailed_metrics(attempt_id)

# Get detailed metrics for the most recent attempt
metrics = api.get_detailed_metrics()
```

#### Get Leaderboard

```python
# Get the current leaderboard
leaderboard = api.get_leaderboard()

# Get the leaderboard for a specific scenario
leaderboard = api.get_leaderboard("standard")
```

#### Export Results

```python
# Export the best result to a file
file_path = api.export_result(output_path="my_best_result.json")

# Export a specific attempt
file_path = api.export_result(attempt_id="abc123", output_path="specific_result.json")
```

#### Save Leaderboard

```python
# Save the leaderboard to a file
api.save_leaderboard("leaderboard.json")
```

## Callback System

The competition system uses a callback system to allow your strategy to dynamically respond to the simulation state. The callback function is called after each simulation step.

```python
def my_strategy(engine):
    # Initial setup
    engine.set_lockdown_level(0.5)
    
    # Define callback
    def on_step(step, state):
        """
        step: Current simulation step (day)
        state: Current simulation state object with these properties:
          - population: Population statistics
          - economy: Economic statistics
          - healthcare: Healthcare system statistics
          - resources: Resource allocation
        """
        # Example: Calculate infection rate
        infection_rate = state.population.infected / state.population.total
        
        # Adjust strategy based on infection rate
        if infection_rate > 0.1:
            engine.set_lockdown_level(0.8)
        else:
            engine.set_lockdown_level(0.4)
    
    # Register the callback
    engine.register_step_callback(on_step)
```

## Engine Control Functions

Your strategy can interact with the simulation engine using these methods:

### Lockdown Controls

```python
# Set lockdown level (0.0 to 1.0)
engine.set_lockdown_level(0.5)  # 0.5 = 50% lockdown severity
```

### Resource Allocation

```python
# Allocate resources to different areas
engine.allocate_resources('healthcare', 200)  # 200 units to healthcare
engine.allocate_resources('economic', 100)    # 100 units to economic support
engine.allocate_resources('research', 50)     # 50 units to research
```

### Travel Restrictions

```python
# Set travel restrictions
engine.restrict_travel(True)   # Restrict travel
engine.restrict_travel(False)  # Allow travel
```

### Getting Information

```python
# Get currently allocated resources
healthcare_resources = engine.get_allocated_resources('healthcare')

# Get current lockdown level
current_lockdown = engine.get_lockdown_level()

# Check if travel is restricted
is_travel_restricted = engine.is_travel_restricted()
```

## Examples

### Basic Competition Usage

```python
from src.competition.api import CompetitionAPI
from src.mirage.engines.base import EngineV1

# Create API instance
api = CompetitionAPI()

# Register player
api.register_player("John Doe")

# Set scenario
api.set_scenario("standard")

# Define strategy
def my_strategy(engine):
    engine.set_lockdown_level(0.5)
    engine.allocate_resources('healthcare', 100)
    
    def on_step(step, state):
        infection_rate = state.population.infected / state.population.total
        if infection_rate > 0.1:
            engine.set_lockdown_level(0.8)
            engine.allocate_resources('healthcare', 200)
        elif infection_rate < 0.02:
            engine.set_lockdown_level(0.3)
            engine.allocate_resources('economic', 150)
    
    engine.register_step_callback(on_step)

# Run in practice mode
api.set_practice_mode(True)
practice_results = api.run_simulation([my_strategy])
print(f"Practice Score: {practice_results['final_score']}")

# Run in competition mode
api.set_practice_mode(False)
if api.get_remaining_attempts() > 0:
    competition_results = api.run_simulation([my_strategy])
    attempt_id = api.save_result(competition_results)
    print(f"Competition Score: {competition_results['final_score']}")
    print(f"Attempt ID: {attempt_id}")
```

For more detailed examples, see the `examples/competition_demo.py` script.

## Score Components

The final score is calculated based on several components:

1. **Population Survived (30%)**: Percentage of population that survived
2. **GDP Preserved (20%)**: Economic health throughout the epidemic
3. **Infection Control (20%)**: How well the infection was contained
4. **Resource Efficiency (15%)**: How efficiently resources were used
5. **Time to Containment (15%)**: How quickly the epidemic was contained

Each component is normalized to a 0-1 scale, and the final score is a weighted average.

## Development Notes

If you're extending the competition system, please follow these guidelines:

1. Keep the API stable and backward compatible
2. Document all public methods
3. Add unit tests for new functionality
4. Maintain separation between API and implementation details

For internal development, see the source code and internal documentation. 