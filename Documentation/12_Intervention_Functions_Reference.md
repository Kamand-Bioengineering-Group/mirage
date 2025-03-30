# Epidemic Intervention Functions Reference

This reference document provides detailed information about the available intervention functions in the XPECTO Epidemic 2.0 Competition System. These functions are essential for implementing containment strategies and managing epidemic impacts.

## Available Intervention Functions

The XPECTO engine provides several functions to implement containment strategies. All these functions are available in both practice and competition modes unless otherwise noted.

### 1. Set Lockdown Level

Controls the strength of lockdown measures, affecting transmission rates and economic activity.

```python
engine.set_lockdown_level(level)
```

**Parameters:**
- `level` (float): A value between 0 and 1 representing lockdown severity
  - 0 = No restrictions
  - 1 = Complete lockdown

**Example:**
```python
# Implement a moderate lockdown
engine.set_lockdown_level(0.5)

# Implement a severe lockdown
engine.set_lockdown_level(0.8)

# Remove lockdown measures
engine.set_lockdown_level(0)
```

**Effects:**
- Reduces transmission rate (R0) by up to 85% at maximum level
- Reduces economic activity (GDP) proportionally to lockdown level
- No direct resource cost, but impacts economy

**Engine Differences:**
- **MockEngine**: Linear reduction in R0 and GDP
- **EnhancedEngine**: Non-linear effects with diminishing returns and compliance decay

### 2. Allocate Resources

Allocates available resources to different response categories.

```python
engine.allocate_resources(category, amount)
```

**Parameters:**
- `category` (str): One of 'healthcare', 'economic', 'research', or 'testing'
- `amount` (int): Amount of resources to allocate

**Example:**
```python
# Invest in healthcare capacity
engine.allocate_resources('healthcare', 300)

# Provide economic support
engine.allocate_resources('economic', 200)

# Fund research for treatments/vaccines
engine.allocate_resources('research', 150)

# Expand testing capabilities
engine.allocate_resources('testing', 100)
```

**Effects by category:**
- **healthcare**: Reduces mortality rate by up to 90%
- **economic**: Counteracts economic damage from lockdowns with up to 90% efficiency
- **research**: Increases research progress, helps achieve containment faster
- **testing**: Improves detection and reduces new infections by up to 70%

**Engine Differences:**
- **MockEngine**: Linear effects with constant returns
- **EnhancedEngine**: Diminishing returns on repeated investment

### 3. Restrict Travel

Controls whether travel restrictions are in place.

```python
engine.restrict_travel(restricted)
```

**Parameters:**
- `restricted` (bool): Whether to restrict travel (True) or not (False)

**Example:**
```python
# Implement travel restrictions
engine.restrict_travel(True)

# Remove travel restrictions
engine.restrict_travel(False)
```

**Effects:**
- Reduces disease transmission rate by approximately 30%
- No direct resource cost
- Some economic impact (indirect)

**Engine Differences:**
- **EnhancedEngine**: Also impacts different regions differently

### 4. Register Step Callback

Registers a function to be called after each simulation step, allowing dynamic strategy adjustments.

```python
engine.register_step_callback(callback_function)
```

**Parameters:**
- `callback_function` (callable): Function to be called after each step

**Example:**
```python
def adaptive_strategy(step, state):
    # Adjust strategy based on current infection rate
    infection_rate = state.population.infected / state.population.total
    
    if infection_rate > 0.1:
        # Strict measures when infection rate is high
        engine.set_lockdown_level(0.7)
        engine.allocate_resources('healthcare', 200)
    elif infection_rate < 0.05:
        # Relaxed measures when infection rate is low
        engine.set_lockdown_level(0.3)
        engine.allocate_resources('economic', 150)

# Register the callback
engine.register_step_callback(adaptive_strategy)
```

### 5. Target Research at Variants (EnhancedEngine only)

Allocates research resources specifically toward a particular variant.

```python
engine.target_research(variant_name, amount)
```

**Parameters:**
- `variant_name` (str): The name of the variant to target (e.g., "Alpha", "Beta", "Gamma")
- `amount` (int): Amount of resources to allocate to this variant

**Example:**
```python
# Target research at Alpha variant
engine.target_research("Alpha", 200)

# Check variant status first, then target
variants = engine.get_variant_status()
if variants:
    most_severe = max(variants, key=lambda v: v.get('mortality_modifier', 0))
    engine.target_research(most_severe['name'], 300)
```

**Effects:**
- 20% more effective than general research for the targeted variant
- Costs 10% more resources than general research
- Reduces the prevalence of the targeted variant
- Most effective when targeting emerging variants before they become dominant

### 6. Get Variant Status (EnhancedEngine only)

Returns information about all potential variants.

```python
variant_status = engine.get_variant_status()
```

**Returns:**
- List of dictionaries containing variant information:
  - `name`: Variant name
  - `active`: Whether the variant has emerged
  - `prevalence`: Proportion of infections of this variant (0-1)
  - `r0_modifier`: Effect on transmission rate
  - `mortality_modifier`: Effect on mortality rate
  - `immune_escape`: Ability to reinfect recovered people (0-1)

**Example:**
```python
# Get and process variant information
variants = engine.get_variant_status()
for variant in variants:
    if variant['active']:
        print(f"Variant {variant['name']} is active with {variant['prevalence']*100:.1f}% prevalence")
        print(f"  R0 modifier: {variant['r0_modifier']}")
        print(f"  Mortality modifier: {variant['mortality_modifier']}")
```

### 7. Display Variant Information (EnhancedEngine only)

Prints information about active variants to the console.

```python
engine.display_variant_info()
```

**Example:**
```python
# Display current variant status in a readable format
engine.display_variant_info()
```

**Output example:**
```
Active variants:
Alpha: 74.3% prevalence (Transmissibility: +50%, Severity: +10%, Immune Escape: 10%)
Beta: 12.1% prevalence (Transmissibility: +30%, Severity: +30%, Immune Escape: 30%)
```

## Creating Your Own Intervention Strategy

To create your own intervention strategy, follow these steps:

1. **Define your strategy function:**

```python
def my_custom_strategy(engine):
    """
    My custom epidemic response strategy.
    
    Parameters:
    -----------
    engine: The simulation engine to apply strategy to
    """
    # Initial measures
    engine.set_lockdown_level(0.6)
    engine.allocate_resources('healthcare', 200)
    engine.restrict_travel(True)
    
    # Define adaptive response using a step callback
    def step_callback(step, state):
        infection_rate = state.population.infected / state.population.total
        economic_health = state.economy.current_gdp / state.economy.initial_gdp
        
        # Adjust strategy based on infection rate and economic health
        if infection_rate > 0.15:
            # Crisis response
            engine.set_lockdown_level(0.8)
            engine.allocate_resources('healthcare', 300)
        elif infection_rate > 0.05:
            # Balanced response based on economic health
            if economic_health < 0.6:
                # Prioritize economy if it's suffering
                engine.set_lockdown_level(0.4)
                engine.allocate_resources('economic', 250)
            else:
                # Otherwise maintain moderate controls
                engine.set_lockdown_level(0.6)
                engine.allocate_resources('healthcare', 150)
        else:
            # Recovery phase when infections are low
            engine.set_lockdown_level(0.2)
            engine.allocate_resources('economic', 200)
            engine.restrict_travel(False)
    
    # Register the callback to be executed at each step
    engine.register_step_callback(step_callback)
```

2. **Use your strategy in the competition:**

```python
# Setup competition
competition = CompetitionManager()
competition.setup_player("Your Name")
competition.set_scenario("standard")
competition.setup_simulation()

# Apply your strategy and run the simulation
results = competition.run_simulation(steps=200, interventions=[my_custom_strategy])

# View your results
print(f"Final score: {results['final_score']}")
```

## Strategy Evaluation

Your intervention strategy will be evaluated based on several metrics:

1. **Population Survived (30%)**: Percentage of the population that survived
2. **GDP Preserved (20%)**: Percentage of the initial GDP maintained
3. **Infection Control (20%)**: Effectiveness in preventing widespread infection
4. **Resource Efficiency (15%)**: How efficiently resources were used
5. **Time to Containment (15%)**: How quickly the epidemic was contained

## Comparing Multiple Strategies

The competition utility functions provide tools to compare different strategies:

```python
from src.competition.utils import (
    create_randomized_engine,
    compare_strategies,
    display_strategy_comparison
)

# Create a test engine
engine = create_randomized_engine(seed=42)

# Define strategies to compare
strategies = {
    "My Strategy": my_custom_strategy,
    "Aggressive Containment": aggressive_containment,
    "Economic Focus": economic_focus
}

# Run and compare all strategies
results = compare_strategies(engine, strategies, steps=200)

# Display comparison
display_strategy_comparison(results)
```

## Tips for Effective Interventions

1. **Balance health and economic impacts**: Severe lockdowns contain the epidemic but damage the economy.

2. **Adaptive strategies work best**: Adjust your interventions based on the current state of the epidemic.

3. **Early action matters**: Implementing measures early can prevent exponential growth.

4. **Resource allocation timing**: Healthcare investments have the most impact during high infection periods, while economic support is crucial during lockdowns.

5. **Research for long-term containment**: Investing in research can help achieve containment faster.

6. **Monitor variant emergence**: In the EnhancedEngine, watch for new variants and adjust your strategy accordingly.

7. **Consider diminishing returns**: Additional investment in the same category may yield progressively smaller benefits. 