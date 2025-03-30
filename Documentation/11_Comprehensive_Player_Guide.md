# XPECTO Epidemic 2.0: Comprehensive Player Guide

This guide provides a complete overview of XPECTO Epidemic 2.0, designed for players who are completely new to the game. It covers all aspects of gameplay, strategy development, and underlying mechanics.

## Table of Contents
1. [Game Overview](#game-overview)
2. [Getting Started](#getting-started)
3. [Core Game Mechanics](#core-game-mechanics)
4. [Intervention Types](#intervention-types)
5. [Strategy Development](#strategy-development)
6. [Understanding Metrics and Scoring](#understanding-metrics-and-scoring)
7. [Competition Mode](#competition-mode)
8. [Advanced Features](#advanced-features)
9. [Tips for Success](#tips-for-success)
10. [Troubleshooting](#troubleshooting)

## Game Overview

XPECTO Epidemic 2.0 is a sophisticated epidemic management simulation that challenges you to develop effective strategies for controlling a disease outbreak. You'll make critical decisions about resource allocation, containment measures, and economic policies that will determine the outcome of the epidemic.

### The Core Challenge

```
┌─────────────────────────────────────────────────────────────────┐
│                    The Epidemic Management Challenge             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐          ┌────────────────┐                    │
│  │             │          │                │                    │
│  │  INFECTION  │◄────────►│  INTERVENTION  │                    │
│  │   SPREAD    │          │   STRATEGIES   │                    │
│  │             │          │                │                    │
│  └──────┬──────┘          └────────┬───────┘                    │
│         │                          │                            │
│         ▼                          ▼                            │
│  ┌─────────────┐          ┌────────────────┐                    │
│  │             │          │                │                    │
│  │  PUBLIC     │◄────────►│  ECONOMIC      │                    │
│  │  HEALTH     │          │  IMPACTS       │                    │
│  │             │          │                │                    │
│  └──────┬──────┘          └────────┬───────┘                    │
│         │                          │                            │
│         └──────────────────────────┘                            │
│                      │                                          │
│                      ▼                                          │
│             ┌─────────────────┐                                 │
│             │                 │                                 │
│             │  FINAL OUTCOME  │                                 │
│             │     SCORE       │                                 │
│             │                 │                                 │
│             └─────────────────┘                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

The simulation presents a delicate balance between controlling the disease and maintaining economic activity. Strict containment measures may effectively stop the disease but at a high economic cost, while minimal intervention preserves the economy but risks higher infection rates and mortality.

## Getting Started

### Installing XPECTO

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-repo/XPECTO.git
   cd XPECTO
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the practice playground**:
   Open the `notebooks/practice_playground.ipynb` Jupyter notebook.

### Your First Simulation

Here's a simple example to get started:

```python
# Import competition manager
from src.competition import CompetitionManager

# Create a new competition instance
competition = CompetitionManager()

# Register yourself as a player
competition.setup_player("Your Name")

# Set the scenario to standard
competition.set_scenario("standard")

# Enable practice mode
competition.toggle_practice_mode(True)

# Set up the simulation
competition.setup_simulation()

# Define a simple strategy
def my_first_strategy(engine):
    # Apply a moderate lockdown
    engine.set_lockdown_level(0.5)
    # Allocate resources to healthcare
    engine.allocate_resources('healthcare', 300)
    # Allocate resources to economic support
    engine.allocate_resources('economic', 200)

# Run the simulation with your strategy
results = competition.run_simulation(steps=200, interventions=[my_first_strategy])

# View the results
print(f"Final score: {results['final_score']}")
```

## Core Game Mechanics

### Simulation State

The simulation tracks several key variables:

1. **Population**: Total, susceptible, infected, recovered, and dead individuals
2. **Economy**: GDP level and economic health
3. **Resources**: Available and spent resources
4. **Research**: Progress toward treatments and vaccines
5. **Healthcare**: Capacity and current usage level

### Disease Model

XPECTO uses a modified SIR (Susceptible-Infected-Recovered) model with the following parameters:

1. **R0 (Basic Reproduction Number)**: How many people each infected person infects
2. **Mortality Rate**: Percentage of infected people who die without intervention
3. **Recovery Rate**: How quickly people recover from the disease
4. **Incubation Period**: Time before an infected person becomes contagious

```
┌─────────────────────────────────────────────────────────────────┐
│                       SIR Model Flow                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                         Infection                               │
│                            │                                    │
│  ┌───────────┐             ▼             ┌───────────┐          │
│  │           │         ┌─────────┐       │           │          │
│  │Susceptible├────────►│Infected │───────►│Recovered  │          │
│  │           │         └────┬────┘       │           │          │
│  └───────────┘              │            └───────────┘          │
│                             │                                   │
│                             ▼                                   │
│                        ┌─────────┐                              │
│                        │  Dead   │                              │
│                        └─────────┘                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Game Cycle

Each simulation step (representing one day) follows this sequence:

1. **Apply interventions**: Your strategy sets lockdown levels and allocates resources
2. **Calculate disease spread**: New infections are determined based on current conditions
3. **Process outcomes**: Calculate recoveries, deaths, and economic impacts
4. **Update metrics**: All game metrics are updated
5. **Check containment**: Determine if the epidemic has been contained
6. **Execute callbacks**: Run any registered step callbacks for dynamic strategies

## Intervention Types

You have several intervention methods available:

### 1. Lockdown Controls

```python
engine.set_lockdown_level(level)  # level from 0.0 to 1.0
```

| Lockdown Level | Description | Health Impact | Economic Impact |
|----------------|-------------|--------------|-----------------|
| 0.0 | No restrictions | None | None |
| 0.3 | Mild social distancing | Reduces R0 by ~25% | Low economic impact |
| 0.5 | Moderate restrictions | Reduces R0 by ~40% | Moderate economic impact |
| 0.7 | Severe restrictions | Reduces R0 by ~60% | High economic impact |
| 1.0 | Complete lockdown | Reduces R0 by ~85% | Severe economic impact |

### 2. Resource Allocation

```python
engine.allocate_resources(category, amount)
```

| Category | Effect | Optimal Timing |
|----------|--------|----------------|
| 'healthcare' | Reduces mortality, increases treatment effectiveness | During high infection periods |
| 'economic' | Reduces GDP impact from lockdowns | During strict lockdowns |
| 'research' | Speeds up vaccine/treatment development | Early in the epidemic |
| 'testing' | Improves detection, reduces new infections | Throughout the epidemic |

### 3. Travel Restrictions

```python
engine.restrict_travel(restricted)  # True or False
```

Travel restrictions reduce disease transmission by approximately 30% but have some economic impact.

### 4. Variant-Specific Research (EnhancedEngine only)

```python
engine.target_research(variant_name, amount)
```

Targets research at specific disease variants, making it more effective but slightly more expensive.

## Strategy Development

### Basic Strategy Structure

```python
def my_strategy(engine):
    # Initial setup - applied once at the beginning
    engine.set_lockdown_level(0.5)
    engine.allocate_resources('healthcare', 200)
    engine.restrict_travel(True)
    
    # Define dynamic response using step callback
    def step_callback(step, state):
        # Get current infection rate
        infection_rate = state.population.infected / state.population.total
        economic_health = state.economy.current_gdp / state.economy.initial_gdp
        
        # Adjust response based on current conditions
        if infection_rate > 0.1:  # High infection
            engine.set_lockdown_level(0.7)
            engine.allocate_resources('healthcare', 300)
        elif infection_rate < 0.02:  # Low infection
            engine.set_lockdown_level(0.3)
            engine.allocate_resources('economic', 200)
    
    # Register the callback to be called after each step
    engine.register_step_callback(step_callback)
```

### Strategy Types

#### Suppression Strategy
Aggressive early measures to quickly eliminate the infection.

```python
def suppression_strategy(engine):
    # Start with very strict measures
    engine.set_lockdown_level(0.9)
    engine.allocate_resources('healthcare', 400)
    engine.restrict_travel(True)
    
    def adjust_measures(step, state):
        infection_rate = state.population.infected / state.population.total
        
        if infection_rate < 0.01:  # Very low infection rate
            engine.set_lockdown_level(0.5)  # Relax somewhat
        if infection_rate < 0.001:  # Near elimination
            engine.set_lockdown_level(0.2)  # Relax significantly
    
    engine.register_step_callback(adjust_measures)
```

#### Balanced Strategy
Moderate measures that balance health and economic concerns.

```python
def balanced_strategy(engine):
    # Start with moderate measures
    engine.set_lockdown_level(0.5)
    engine.allocate_resources('healthcare', 200)
    engine.allocate_resources('economic', 200)
    
    def adjust_measures(step, state):
        infection_rate = state.population.infected / state.population.total
        economic_health = state.economy.current_gdp / state.economy.initial_gdp
        
        if infection_rate > 0.1:  # High infection
            engine.set_lockdown_level(0.7)
            engine.allocate_resources('healthcare', 300)
        elif infection_rate < 0.05 and economic_health < 0.7:  # Low infection, poor economy
            engine.set_lockdown_level(0.3)
            engine.allocate_resources('economic', 300)
    
    engine.register_step_callback(adjust_measures)
```

#### Research-Focused Strategy
Prioritizes research for long-term containment.

```python
def research_strategy(engine):
    # Moderate initial measures with research focus
    engine.set_lockdown_level(0.6)
    engine.allocate_resources('research', 500)
    
    def adjust_measures(step, state):
        infection_rate = state.population.infected / state.population.total
        research_progress = state.research.progress
        
        if research_progress > 0.5:  # Substantial research progress
            engine.set_lockdown_level(0.4)  # Can relax somewhat
        
        if infection_rate > 0.15:  # Crisis situation
            engine.set_lockdown_level(0.8)  # Emergency measures
            engine.allocate_resources('healthcare', 300)
    
    engine.register_step_callback(adjust_measures)
```

## Understanding Metrics and Scoring

XPECTO evaluates your performance using these key metrics:

### Primary Metrics

1. **Population Survived (30%)**: Percentage of the population that survives the epidemic
   ```
   population_survived = (total_population - deaths) / total_population
   ```

2. **GDP Preserved (20%)**: Percentage of the initial GDP maintained
   ```
   gdp_preserved = final_gdp / initial_gdp
   ```

3. **Infection Control (20%)**: How well you prevented widespread infection
   ```
   infection_control = 1.0 - (max_infection_rate)
   ```

4. **Resource Efficiency (15%)**: How efficiently resources were used
   ```
   resource_efficiency = 1.0 - (total_spent / maximum_possible)
   ```

5. **Time to Containment (15%)**: How quickly the epidemic was contained
   ```
   time_efficiency = 1.0 - (containment_step / maximum_steps)
   ```

6. **Variant Control** (EnhancedEngine only): Effectiveness against disease variants
   ```
   variant_control = 1.0 - average_variant_prevalence
   ```

### Final Score Calculation

```
final_score = (0.30 * population_survived +
               0.20 * gdp_preserved +
               0.20 * infection_control +
               0.15 * resource_efficiency +
               0.15 * time_efficiency)
```

With the EnhancedEngine, variant control is also factored into the score.

## Competition Mode

XPECTO includes a competition mode that allows you to test your strategies against standardized scenarios and compare results with others.

### Competition Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                     Competition Workflow                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐       ┌─────────────┐       ┌─────────────┐    │
│  │             │       │             │       │             │    │
│  │  Register   │──────►│   Select    │──────►│   Submit    │    │
│  │   Player    │       │  Scenario   │       │  Strategy   │    │
│  │             │       │             │       │             │    │
│  └─────────────┘       └─────────────┘       └──────┬──────┘    │
│                                                     │           │
│                                                     ▼           │
│  ┌─────────────┐       ┌─────────────┐       ┌─────────────┐    │
│  │             │       │             │       │             │    │
│  │   View      │◄──────┤  Review     │◄──────┤   Run       │    │
│  │ Leaderboard │       │  Results    │       │ Simulation  │    │
│  │             │       │             │       │             │    │
│  └─────────────┘       └─────────────┘       └─────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Available Scenarios

1. **Standard Scenario**: Baseline epidemic challenge with moderate difficulty
2. **Challenging Scenario**: More difficult situation with higher R0 and limited resources
3. **Expert Challenge**: Extremely difficult with high R0 and severe resource constraints
4. **Economic Crisis**: Focuses on maintaining economic stability
5. **Resource Scarcity**: Tests efficiency with very limited resources

### Submitting to Competition

```python
# Import competition manager
from src.competition import CompetitionManager

# Initialize competition
competition = CompetitionManager()

# Setup player
competition.setup_player("Your Name", "your.email@example.com")

# Select scenario
competition.set_scenario("standard")

# Disable practice mode for official submission
competition.toggle_practice_mode(False)

# Setup simulation
competition.setup_simulation()

# Run your strategy
results = competition.run_simulation(steps=200, interventions=[my_strategy])

# View results
print(f"Final score: {results['final_score']}")
```

## Advanced Features

### Variant System

In the EnhancedEngine, disease variants can emerge during the simulation:

```
┌─────────────────────────────────────────────────────────────────┐
│                      Variant Emergence                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐        ┌─────────────┐       ┌─────────────┐   │
│  │             │        │             │       │             │   │
│  │ Population  │───────►│ Cumulative  │──────►│  Threshold  │   │
│  │  Infected   │        │ Infections  │       │  Reached    │   │
│  │             │        │             │       │             │   │
│  └─────────────┘        └─────────────┘       └──────┬──────┘   │
│                                                      │          │
│                                                      ▼          │
│  ┌─────────────┐        ┌─────────────┐       ┌─────────────┐   │
│  │             │        │             │       │             │   │
│  │  Variant    │◄───────┤   Random    │◄──────┤  Chance of  │   │
│  │  Emerges    │        │  Process    │       │  Emergence  │   │
│  │             │        │             │       │             │   │
│  └──────┬──────┘        └─────────────┘       └─────────────┘   │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────────────────────────────────┐                    │
│  │                                         │                    │
│  │  Effects on R0, Mortality, Immunity     │                    │
│  │                                         │                    │
│  └─────────────────────────────────────────┘                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

Variants require special strategies:

```python
def variant_aware_strategy(engine):
    # Initial balanced approach
    engine.set_lockdown_level(0.4)
    engine.allocate_resources('healthcare', 200)
    engine.allocate_resources('research', 300)
    
    def monitor_and_respond(step, state):
        try:
            # Get current variant status
            variants = engine.get_variant_status()
            
            if variants:
                # Find most prevalent variant
                dominant_variant = max(variants, key=lambda v: v['prevalence'])
                
                # Target research at the dominant variant
                engine.target_research(dominant_variant['name'], 200)
                
                # Adjust lockdown based on variant transmissibility
                transmissibility = dominant_variant.get('r0_modifier', 1.0)
                engine.set_lockdown_level(min(0.8, 0.4 * transmissibility))
                
                # Adjust healthcare based on variant severity
                severity = dominant_variant.get('mortality_modifier', 1.0)
                engine.allocate_resources('healthcare', int(200 * severity))
        except:
            # Fall back to standard strategy if variant features unavailable
            pass
    
    engine.register_step_callback(monitor_and_respond)
```

### Region-Specific Effects

The EnhancedEngine models different regions (urban and rural) with distinct characteristics:

```python
def region_aware_strategy(engine):
    # Default strategy
    engine.set_lockdown_level(0.5)
    
    def regional_response(step, state):
        try:
            # Check if we can access regional data
            urban_infection = engine.enhanced_state["regional_infection"]["urban"]
            rural_infection = engine.enhanced_state["regional_infection"]["rural"]
            
            # More strict in regions with higher infection
            if urban_infection > 0.1 and rural_infection < 0.05:
                # Target urban areas more strictly
                print("Urban outbreak detected, focusing restrictions there")
                # In a real implementation, would use region-specific controls
            elif rural_infection > urban_infection:
                # Target rural areas more strictly
                print("Rural outbreak detected, focusing restrictions there")
        except:
            # Fall back to standard strategy if regional features unavailable
            pass
    
    engine.register_step_callback(regional_response)
```

## Tips for Success

1. **Balance health and economic impacts**: The highest scores come from keeping both mortality and economic damage low.

2. **Adapt to changing conditions**: Monitor infection rates and adjust your strategy dynamically.

3. **Act early**: Preventive measures are more effective than reactive ones.

4. **Consider resource efficiency**: Don't overspend in areas that aren't needed.

5. **Research is crucial**: Invest in research early for faster containment.

6. **Monitor healthcare capacity**: Prevent the healthcare system from being overwhelmed.

7. **In the EnhancedEngine, watch for variants**: Be ready to adapt when new variants emerge.

8. **Test multiple approaches**: Compare different strategies to find the most effective one.

9. **Pay attention to diminishing returns**: More isn't always better with resource allocation.

10. **Study the scenarios**: Different scenarios require different approaches.

## Troubleshooting

### Common Issues

1. **"KeyError" when accessing variant data**: Make sure you're using the EnhancedEngine and handle exceptions for engine-specific features.

2. **Similar scores for different strategies**: This is a known limitation in some engine configurations. See the [Improving Strategy Differentiation](09_Improving_Strategy_Differentiation.md) document.

3. **Strategy not having expected effect**: Check for diminishing returns in resource allocation or intervention fatigue effects.

4. **Unable to contain the epidemic**: Make sure you're investing enough in research alongside containment measures.

5. **Errors with step callbacks**: Ensure your callback function accepts the correct parameters (step, state).

### Getting Help

If you encounter issues:

1. Check the [FAQ](06_FAQ.md) document
2. Review the [API Reference](competition_api_reference.md)
3. Examine the example code in the `examples/` directory
4. Try simplifying your strategy to isolate the problem

## Further Reading

For more detailed information on specific aspects of XPECTO:

- [Engine Parameters](10_Engine_Parameters.md): Details on simulation engine configuration
- [Enhanced Engine and Variants](07_Enhanced_Engine_and_Variants.md): Advanced features of the EnhancedEngine
- [Game Architecture](08_Game_Architecture.md): Technical overview of the simulation system
- [Competition Rules](04_Competition_Rules.md): Official rules and evaluation criteria
- [Improving Strategy Differentiation](09_Improving_Strategy_Differentiation.md): Analysis of strategy outcomes 