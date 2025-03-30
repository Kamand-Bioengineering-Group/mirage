# Intervention Strategies Guide

This guide explains how to create effective intervention strategies for XPECTO Epidemic 2.0, with examples and best practices.

## What Are Interventions?

In XPECTO Epidemic 2.0, interventions are the actions you take to control the epidemic and mitigate its impacts. These are represented as Python functions that interact with the simulation engine to modify parameters like lockdown levels, resource allocation, and more.

## How to Define an Intervention

An intervention is defined as a Python function that takes the simulation engine as its parameter:

```python
def my_strategy(engine):
    # Apply interventions to the engine
    engine.set_lockdown_level(0.5)  # 50% lockdown severity
    engine.allocate_resources('healthcare', 200)  # Allocate resources to healthcare
```

## Available Intervention Methods

The engine provides several methods to control the simulation:

### 1. Lockdown Controls

```python
engine.set_lockdown_level(level)  # Set lockdown severity (0.0-1.0)
```

- **0.0**: No restrictions 
- **0.3**: Mild social distancing
- **0.5**: Moderate restrictions (schools closed, some businesses limited)
- **0.7**: Severe restrictions (most non-essential businesses closed)
- **1.0**: Complete lockdown (only essential services operating)

Higher lockdown levels reduce infection spread but have a greater economic impact.

### 2. Resource Allocation

```python
engine.allocate_resources(category, amount)
```

Key resource categories:
- **healthcare**: Improves treatment effectiveness, reduces mortality
- **economic**: Provides economic support, reducing GDP impact
- **research**: Speeds up vaccine development and treatment methods
- **testing**: Improves detection and tracking of cases

Resources are limited, so allocate them wisely.

## Responsive Strategies with Callbacks

For advanced strategies, you can register a callback function that executes after each simulation step:

```python
def my_strategy(engine):
    # Initial setup
    engine.set_lockdown_level(0.3)  # Start with mild measures
    
    # Define callback for dynamic response
    def monitor_and_respond(step, state):
        # Get current infection rate
        infection_rate = state.population.infected / state.population.total
        
        # Adjust response based on infection rate
        if infection_rate > 0.1:  # If over 10% infected
            engine.set_lockdown_level(0.8)  # Severe lockdown
            engine.allocate_resources('healthcare', 300)  # Boost healthcare
        elif infection_rate > 0.05:  # If 5-10% infected
            engine.set_lockdown_level(0.5)  # Moderate lockdown
            engine.allocate_resources('healthcare', 200)
        else:  # Low infection rate
            engine.set_lockdown_level(0.2)  # Light restrictions
            engine.allocate_resources('economic', 150)  # Focus on economy
    
    # Register the callback
    engine.register_step_callback(monitor_and_respond)
```

The callback receives:
- **step**: Current simulation step (day/time unit)
- **state**: Current state object with attributes like:
  - `state.population.total`: Total population
  - `state.population.infected`: Currently infected
  - `state.population.dead`: Total deaths
  - `state.population.recovered`: Recovered individuals
  - `state.gdp`: Current GDP level
  - `state.resources_spent`: Total resources spent

## Example Strategy Templates

### 1. Basic Balanced Strategy

```python
def balanced_strategy(engine):
    """Balanced approach with moderate measures throughout."""
    engine.set_lockdown_level(0.5)  # Moderate lockdown
    engine.allocate_resources('healthcare', 200)  # Healthcare investment
    engine.allocate_resources('economic', 150)  # Economic support
```

### 2. Phased Strategy

```python
def phased_strategy(engine):
    """Strategy that changes over time."""
    
    def phase_controller(step, state):
        # Early phase - containment focus
        if step < 50:
            engine.set_lockdown_level(0.7)  # Strong initial response
            engine.allocate_resources('healthcare', 250)
            engine.allocate_resources('testing', 100)
            
        # Middle phase - balanced approach
        elif 50 <= step < 200:
            engine.set_lockdown_level(0.5)
            engine.allocate_resources('healthcare', 200)
            engine.allocate_resources('economic', 150)
            
        # Late phase - recovery focus
        else:
            engine.set_lockdown_level(0.3)
            engine.allocate_resources('economic', 250)
            engine.allocate_resources('healthcare', 100)
    
    engine.register_step_callback(phase_controller)
```

### 3. Adaptive Response Strategy

```python
def adaptive_strategy(engine):
    """Strategy that adapts to the current infection level."""
    
    # Track state between steps
    state_tracker = {'peak_infection': 0.0, 'lockdown_level': 0.3}
    
    def adaptive_controller(step, state):
        # Calculate current infection rate
        infection_rate = state.population.infected / state.population.total
        
        # Update peak tracking
        if infection_rate > state_tracker['peak_infection']:
            state_tracker['peak_infection'] = infection_rate
        
        # Adjust lockdown based on infection rate
        if infection_rate > 0.15:  # Severe outbreak
            target_lockdown = 0.9
        elif infection_rate > 0.1:  # Serious outbreak
            target_lockdown = 0.7
        elif infection_rate > 0.05:  # Moderate outbreak
            target_lockdown = 0.5
        elif infection_rate > 0.02:  # Mild outbreak
            target_lockdown = 0.3
        else:  # Controlled situation
            target_lockdown = 0.2
        
        # Don't change lockdown too abruptly (max 0.1 change per step)
        current = state_tracker['lockdown_level']
        change = target_lockdown - current
        change = max(min(change, 0.1), -0.1)  # Limit change magnitude
        state_tracker['lockdown_level'] = current + change
        
        # Apply lockdown
        engine.set_lockdown_level(state_tracker['lockdown_level'])
        
        # Allocate resources based on situation
        if infection_rate > 0.1:
            engine.allocate_resources('healthcare', 300)
        elif infection_rate > 0.05:
            engine.allocate_resources('healthcare', 200)
            engine.allocate_resources('economic', 100)
        else:
            engine.allocate_resources('healthcare', 150)
            engine.allocate_resources('economic', 200)
    
    # Set initial lockdown
    engine.set_lockdown_level(state_tracker['lockdown_level'])
    
    # Register callback
    engine.register_step_callback(adaptive_controller)
```

## Strategy Development Best Practices

1. **Balance Trade-offs**: Every decision involves trade-offs between health, economy, and resources.

2. **Adapt to Changing Conditions**: The most effective strategies respond dynamically to the evolving situation.

3. **Consider Timing**: The timing of interventions is crucial. Early action can prevent larger outbreaks.

4. **Monitor Key Metrics**: Pay attention to infection rates, healthcare capacity, and economic indicators.

5. **Think in Phases**: Different phases of the epidemic require different approaches.

6. **Test Extensively**: Use practice mode to refine your strategy before making official attempts.

7. **Learn from History**: Study the results of your previous attempts to identify what worked and what didn't.

## Common Strategy Types

- **Suppression**: Aggressive early measures to quickly eliminate the infection
- **Mitigation**: Moderate measures that slow but don't stop spread, protecting the most vulnerable
- **Oscillating**: Alternating between strict and relaxed measures based on thresholds
- **Phased**: Predetermined changes in approach as the epidemic progresses
- **Adaptive**: Dynamic response based on current conditions

## Next Steps

Now that you understand how to develop intervention strategies:
- Experiment in the [Practice Playground](../notebooks/practice_playground.ipynb)
- Review the [Competition Rules](04_Competition_Rules.md) to understand scoring
- Study the [Scenarios](05_Scenarios.md) to prepare for different challenges 