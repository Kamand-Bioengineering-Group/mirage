# XPECTO Epidemic 2.0 Competition System

This module implements a comprehensive competition system for the XPECTO Epidemic 2.0 simulation, allowing players to test their strategies against standardized scenarios and compare their performance.

## Features

- **Player Management**: Registration, profile management, and strategy documentation
- **Standardized Scenarios**: Predefined epidemic scenarios with consistent parameters
- **Score Tracking**: Multi-component scoring system with detailed breakdowns
- **Leaderboard**: Ranking of players based on performance
- **Practice Mode**: Unlimited attempts in practice mode
- **Competition Mode**: Limited attempts for official submissions
- **Strategy Documentation**: Text-based strategy submission and documentation

## Architecture

The competition system follows a modular, layered architecture designed for easy migration to a web-based service:

```
                   ┌─────────────────────┐
                   │  CompetitionManager │
                   └──────────┬──────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
┌────────▼───────┐ ┌──────────▼─────────┐ ┌────────▼───────┐
│    Storage     │ │  CompetitionService │ │   Simulation   │
│   Providers    │ │                     │ │  Integration   │
└────────┬───────┘ └──────────┬─────────┘ └────────┬───────┘
         │                    │                    │
┌────────▼───────┐            │            ┌───────▼────────┐
│ LocalStorage or│            │            │  Epidemic      │
│   Firebase     │            │            │  Engine        │
└────────────────┘            │            └────────────────┘
                   ┌──────────▼─────────┐
                   │   Domain Models    │
                   └────────────────────┘
```

### Core Components

1. **Domain Models**: Platform-agnostic business entities
   - Player, Scenario, Attempt, SimulationResults, LeaderboardEntry

2. **Storage Providers**: Data storage abstraction
   - Local JSON files (for notebook/local usage)
   - Firebase (for web deployment, placeholder implementation)

3. **Competition Service**: Business logic coordination
   - Scoring calculation
   - Attempt validation and tracking
   - Leaderboard management

4. **Simulation Integration**: Connection to epidemic engine
   - Engine configuration
   - Metrics tracking
   - Results processing

5. **Competition Manager**: Unified interface
   - High-level API for competition management
   - User-friendly data visualization

## Usage

### Basic Setup

```python
from src.competition import CompetitionManager
from src.mirage.engines.base import EngineV1

# Create the epidemic engine
engine = EngineV1()

# Create competition manager
competition = CompetitionManager(data_dir="data", engine=engine)

# Register as a player
player_id = competition.setup_player(name="Player Name", email="player@example.com")
```

### Running Simulations

```python
# Set up a scenario
competition.set_scenario("standard")  # or "challenging"
competition.setup_simulation()

# Define interventions (strategies)
def apply_lockdown(engine):
    # Implement lockdown strategy
    pass

# Run in practice mode
competition.toggle_practice_mode(is_practice=True)
results = competition.run_simulation(steps=730, interventions=[apply_lockdown])

# View score
competition.display_score(results)
```

### Competition Mode

```python
# Submit strategy document
strategy_doc = """Detailed explanation of strategy..."""
competition.submit_strategy_document(strategy_doc=strategy_doc)

# Switch to competition mode
competition.toggle_practice_mode(is_practice=False)

# Run official attempts (limited to 3 per scenario)
competition.set_scenario("standard")
competition.setup_simulation()
results = competition.run_simulation(steps=730, interventions=[apply_lockdown])

# View leaderboard
competition.display_leaderboard()
```

## Web Deployment

The system is designed for easy transition to a Flask/Firebase web application:

1. **Same Core Logic**: The business logic remains unchanged
2. **Storage Provider Swap**: Switch from LocalStorageProvider to FirebaseStorageProvider
3. **REST API Layer**: Add Flask endpoints that call the same services
4. **Web UI**: Create web interfaces for player interaction

## Demo

A demonstration script is included at `src/competition/demo.py`. To run:

```bash
python -m src.competition.demo
```

## Development

### Adding New Scenarios

To add new competition scenarios, modify the `_initialize_scenarios` method in `CompetitionService` class or create a scripts to add scenarios to the storage provider:

```python
new_scenario = Scenario(
    id="extreme",
    name="Extreme Pandemic",
    description="An extremely challenging scenario with rapid spread and limited resources.",
    seed="extreme_2023",
    r0=4.5,
    initial_infections={"capital": 200, "major_city_1": 100, "major_city_2": 100},
    initial_resources=500,
    difficulty="extreme",
    parameters={
        "disease_mortality": 0.04,
        "treatment_effectiveness": 0.5,
        "vaccine_development_time": 200,
        "economic_impact_factor": 1.5
    }
)

storage_provider.save_scenario(new_scenario)
```

### Customizing Scoring

To modify the scoring system, update the calculation methods in the `CompetitionService` class:

```python
def calculate_score(self, 
                   population_survived: float,
                   gdp_preserved: float,
                   infection_control: float,
                   resource_efficiency: float,
                   time_to_containment: float) -> float:
    # Adjust weights as needed
    weighted_score = (
        population_survived * 0.30 +
        gdp_preserved * 0.20 +
        infection_control * 0.20 +
        resource_efficiency * 0.15 +
        time_to_containment * 0.15
    )
    
    return round(weighted_score, 4)
``` 