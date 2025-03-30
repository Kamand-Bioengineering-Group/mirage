# How to Play XPECTO Epidemic 2.0

This guide provides step-by-step instructions on how to engage with the XPECTO Epidemic 2.0 simulation, from setup to strategy execution.

## Setup and Requirements

Before starting, ensure you have:
- Python 3.8 or higher installed
- Required libraries (pandas, numpy, matplotlib, etc.)
- The XPECTO repository cloned or downloaded

## Getting Started

1. Navigate to the project directory
2. Run VS Code or Jupyter notebook or your preferred notebook environment
3. Open one of the following notebooks to begin:
   - `notebooks/competition_tutorial.ipynb` - For a guided introduction
   - `notebooks/practice_playground.ipynb` - For unrestricted practice
   - `notebooks/competition_playground.ipynb` - For official competition attempts

## Basic Game Flow

The game follows this basic sequence:

1. **Register as a player** - Provide your name to be tracked in the system
2. **Select a scenario** - Each scenario represents a different epidemic situation
3. **Develop an intervention strategy** - Code your approach to managing the epidemic
4. **Run the simulation** - Execute your strategy and observe the results
5. **Analyze performance** - Review your score and metrics to improve your approach
6. **Refine and retry** - In practice mode, or make official attempts in competition mode

## Simulation Interface

All interaction with the simulation happens through the `CompetitionManager` interface:

```python
# Initialize the system
engine = MockEngine()
competition = CompetitionManager(data_dir="your_data_dir", engine=engine)

# Register as a player
player_id = competition.setup_player(name="Your Name")

# Select a scenario
competition.set_scenario("standard")  # or "challenging" or other available scenarios

# Setup simulation
competition.setup_simulation()

# Run your strategy
results = competition.run_simulation(steps=365, interventions=[your_strategy])

# View results
competition.display_score(results)
competition.display_player_attempts()
```

## Practice vs. Competition Mode

The simulation has two modes:

### Practice Mode
- Unlimited attempts
- Results not counted for leaderboard rankings
- Use for developing and testing strategies

```python
# Enable practice mode
competition.toggle_practice_mode(is_practice=True)
```

### Competition Mode
- Limited to 3 official attempts per scenario
- Results recorded for leaderboard ranking
- Use for submitting your best strategies

```python
# Enable competition mode
competition.toggle_practice_mode(is_practice=False)
```

## Key Controls and Methods

The simulation engine provides these primary control methods:

1. **Setting Lockdown Level**:
```python
engine.set_lockdown_level(0.5)  # Value from 0 (no lockdown) to 1 (full lockdown)
```

2. **Allocating Resources**:
```python
engine.allocate_resources('healthcare', 200)  # Allocate to healthcare system
engine.allocate_resources('economic', 150)   # Economic support
engine.allocate_resources('research', 100)   # Research and development
```

3. **Monitoring and Responding to Conditions** (via callbacks):
```python
def monitor_callback(step, state):
    # Analyze current state and respond
    infection_rate = state.population.infected / state.population.total
    if infection_rate > 0.1:  # If infection rate exceeds 10%
        engine.set_lockdown_level(0.8)  # Implement strict lockdown
    
# Register the callback
engine.register_step_callback(monitor_callback)
```

## Analyzing Results

After running a simulation, analyze your performance:

1. **Score Breakdown**
```python
competition.display_score(results)
```

2. **Attempt History**
```python
competition.display_player_attempts()
```

3. **Leaderboard** (for competitive attempts)
```python
competition.display_leaderboard()
```

## Next Steps

Now that you understand the basics, proceed to:
- [03_Intervention_Strategies.md](03_Intervention_Strategies.md) to learn advanced strategy development
- [05_Scenarios.md](05_Scenarios.md) to understand the different challenge scenarios
- Try out the Practice Playground to experiment with your own strategies

Remember: The most effective strategies find the right balance between health outcomes, economic impacts, and resource efficiency! 