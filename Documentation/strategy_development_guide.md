# Strategy Development Guide for XPECTO Epidemic 2.0

This guide will help you develop effective strategies for the XPECTO Epidemic 2.0 competition by explaining what parameters you can tune, how to respond to simulation state, and how to optimize your score.

## Core Strategy Components

An epidemic management strategy in XPECTO consists of two main elements:

1. **Initial setup**: Actions taken at the beginning of the simulation
2. **Dynamic response**: How your strategy adapts to changing conditions throughout the simulation

## Available Control Parameters

These are the parameters you can manipulate in your strategy:

### Lockdown Level

The lockdown level controls the severity of social distancing measures:

```python
engine.set_lockdown_level(level)  # Value from 0.0 (no restrictions) to 1.0 (full lockdown)
```

- **0.0**: No restrictions (normal social contact)
- **0.3**: Mild measures (some limits on large gatherings)
- **0.5**: Moderate measures (schools closed, work-from-home encouraged)
- **0.7**: Strict measures (non-essential businesses closed, stay-at-home orders)
- **1.0**: Complete lockdown (only essential services allowed)

Lockdowns reduce infection rates but harm the economy, especially at higher levels.

### Resource Allocation

Resources can be allocated to various areas:

```python
engine.allocate_resources(category, amount)  # Allocate a specific amount to a category
```

Available categories:
- **'healthcare'**: Improves treatment effectiveness, reduces mortality rate
- **'economic'**: Provides economic support, preserves GDP despite lockdowns
- **'research'**: Speeds up vaccine development, treatment methods, testing
- **'testing'**: Improves detection of cases, enabling more targeted responses

Resources are limited, so allocate them strategically.

### Travel Restrictions

Control travel in and out of regions:

```python
engine.restrict_travel(True)   # Implement travel restrictions
engine.restrict_travel(False)  # Remove travel restrictions
```

Travel restrictions help contain the spread of the disease, but impact economic activity.

### Querying Current State

You can query the current state of various parameters:

```python
current_lockdown = engine.get_lockdown_level()
healthcare_resources = engine.get_allocated_resources('healthcare')
is_travel_restricted = engine.is_travel_restricted()
```

## Developing Dynamic Strategies with Callbacks

The most powerful strategies use callbacks to adapt to changing conditions:

```python
def my_strategy(engine):
    # Initial setup
    engine.set_lockdown_level(0.5)
    engine.allocate_resources('healthcare', 200)
    
    # Define callback for dynamic response
    def on_step(step, state):
        # Calculate infection rate
        infection_rate = state.population.infected / state.population.total
        
        # Get economic health
        economic_health = state.economy.current_gdp / state.economy.initial_gdp
        
        # Adjust strategy based on conditions
        if infection_rate > 0.1:  # High infection rate
            engine.set_lockdown_level(0.8)
            engine.allocate_resources('healthcare', 300)
            engine.restrict_travel(True)
        elif infection_rate > 0.05:  # Moderate infection rate
            if economic_health < 0.7:  # Poor economy
                # Balance health and economy
                engine.set_lockdown_level(0.5)
                engine.allocate_resources('economic', 200)
            else:  # Strong economy
                # Focus on containment
                engine.set_lockdown_level(0.6)
                engine.allocate_resources('healthcare', 250)
        else:  # Low infection rate
            engine.set_lockdown_level(0.3)
            engine.allocate_resources('economic', 300)
            engine.restrict_travel(False)
    
    # Register the callback to be called after each step
    engine.register_step_callback(on_step)
```

## State Object Properties

The state object passed to your callback contains these properties:

- **state.population**: Population statistics
  - `state.population.total`: Total population
  - `state.population.infected`: Currently infected
  - `state.population.dead`: Total deaths
  - `state.population.recovered`: Recovered individuals

- **state.economy**: Economic indicators
  - `state.economy.initial_gdp`: Starting GDP
  - `state.economy.current_gdp`: Current GDP
  - `state.economy.unemployment_rate`: Current unemployment rate

- **state.healthcare**: Healthcare system
  - `state.healthcare.capacity`: Current capacity (beds, etc.)
  - `state.healthcare.utilization`: Current utilization rate

- **state.resources**: Resource allocation
  - `state.resources.total_spent`: Total resources spent
  - `state.resources.remaining`: Remaining resources

## Strategy Patterns

Here are effective patterns to consider:

### 1. Phased Strategy

Divide the epidemic into phases with different priorities:

```python
def phased_strategy(engine):
    def on_step(step, state):
        # Early phase - containment
        if step < 60:
            engine.set_lockdown_level(0.7)
            engine.allocate_resources('healthcare', 300)
            
        # Middle phase - balanced approach
        elif step < 180:
            engine.set_lockdown_level(0.5)
            engine.allocate_resources('healthcare', 200)
            engine.allocate_resources('economic', 150)
            
        # Late phase - recovery
        else:
            engine.set_lockdown_level(0.3)
            engine.allocate_resources('economic', 300)
    
    engine.register_step_callback(on_step)
```

### 2. Threshold-Based Strategy

Adapt based on infection rate thresholds:

```python
def threshold_strategy(engine):
    def on_step(step, state):
        infection_rate = state.population.infected / state.population.total
        
        if infection_rate > 0.15:  # Crisis
            engine.set_lockdown_level(0.9)
            engine.allocate_resources('healthcare', 400)
        elif infection_rate > 0.1:  # Serious outbreak
            engine.set_lockdown_level(0.7)
            engine.allocate_resources('healthcare', 300)
        elif infection_rate > 0.05:  # Concerning
            engine.set_lockdown_level(0.5)
            engine.allocate_resources('healthcare', 200)
        elif infection_rate > 0.01:  # Mild
            engine.set_lockdown_level(0.3)
            engine.allocate_resources('healthcare', 100)
        else:  # Under control
            engine.set_lockdown_level(0.2)
            engine.allocate_resources('economic', 200)
    
    engine.register_step_callback(on_step)
```

### 3. Balanced Multi-Factor Strategy

Consider multiple factors simultaneously:

```python
def balanced_strategy(engine):
    def on_step(step, state):
        infection_rate = state.population.infected / state.population.total
        economic_health = state.economy.current_gdp / state.economy.initial_gdp
        healthcare_load = state.healthcare.utilization / state.healthcare.capacity
        
        # Calculate balanced lockdown level
        base_lockdown = infection_rate * 5  # Scale to reasonable range
        economic_adjustment = (1 - economic_health) * -0.2  # Reduce lockdown if economy suffering
        healthcare_adjustment = (healthcare_load - 0.5) * 0.3  # Increase if healthcare strained
        
        lockdown_level = base_lockdown + economic_adjustment + healthcare_adjustment
        lockdown_level = max(0.1, min(0.9, lockdown_level))  # Clamp to reasonable range
        
        engine.set_lockdown_level(lockdown_level)
        
        # Allocate resources based on needs
        if healthcare_load > 0.8:  # Critical healthcare shortage
            engine.allocate_resources('healthcare', 300)
        elif economic_health < 0.6:  # Economic crisis
            engine.allocate_resources('economic', 300)
        else:  # Balanced allocation
            engine.allocate_resources('healthcare', 150)
            engine.allocate_resources('economic', 150)
    
    engine.register_step_callback(on_step)
```

## Optimizing for Score Components

Your final score is based on five weighted components:

### 1. Population Survived (30%)

To maximize this component:
- Invest heavily in healthcare
- Implement early lockdowns to prevent spread
- Adjust lockdown based on infection rate

### 2. GDP Preserved (20%)

To maximize this component:
- Avoid excessive lockdowns
- Allocate resources to economic support
- Ease restrictions when infection is under control

### 3. Infection Control (20%)

To maximize this component:
- Implement strict measures early to prevent high peak infection
- Use travel restrictions for serious outbreaks
- Maintain adequate healthcare resources

### 4. Resource Efficiency (15%) 

To maximize this component:
- Avoid over-allocating resources when unnecessary
- Scale resource allocation to the severity of the situation
- Reduce healthcare spending when infection rates are low

### 5. Time to Containment (15%)

To maximize this component:
- Focus on rapid containment early in the epidemic
- Use aggressive measures to bring infection rates down quickly
- Invest in research to speed up containment

## Practice vs. Competition Mode

### Practice Mode

Use practice mode to:
- Experiment with different strategies
- Test the impact of parameter changes
- Refine your approach before official attempts

```python
# Enable practice mode
competition.toggle_practice_mode(is_practice=True)

# Run multiple strategies to compare
results_strategy_a = competition.run_simulation(interventions=[strategy_a])
results_strategy_b = competition.run_simulation(interventions=[strategy_b])

# Compare results
print(f"Strategy A score: {results_strategy_a['final_score']}")
print(f"Strategy B score: {results_strategy_b['final_score']}")
```

### Competition Mode

In competition mode:
- You have limited attempts (3 per scenario)
- Results count toward your official ranking
- Use your best refined strategy

```python
# Enable competition mode
competition.toggle_practice_mode(is_practice=False)

# Check remaining attempts
remaining = competition.get_remaining_attempts()
print(f"You have {remaining} attempts remaining")

# Make an official attempt
if remaining > 0:
    results = competition.run_simulation(interventions=[my_best_strategy])
    attempt_id = competition.save_attempt(results)
    print(f"Official attempt submitted with ID: {attempt_id}")
    print(f"Final score: {results['final_score']}")
```

## Advanced Strategy Techniques

### Gradient Descent Approach

For the most advanced strategies, implement a form of gradient descent during practice:

1. Start with a baseline strategy
2. Make small adjustments to parameters
3. Evaluate the impact on score
4. Move in the direction that improves score
5. Repeat until optimized

### Hybrid Strategies

Combine different approach patterns for different phases:
- Aggressive containment early
- Balanced approach mid-epidemic
- Economic recovery focus late

### Meta-Learning

Use previous attempt results to inform future strategies:
- Record what worked in different scenarios
- Identify patterns in successful approaches
- Adapt strategies based on this learning

## Final Tips

1. **Test thoroughly** in practice mode before competition
2. **Document your strategies** to track what works
3. **Consider all score components** rather than focusing on just one or two
4. **Adapt to each scenario's** unique characteristics
5. **Balance short-term** (infection control) with **long-term** (economic) goals

Remember that the most successful strategies will find the optimal balance between competing objectives, adapting dynamically to changing conditions throughout the simulation. 