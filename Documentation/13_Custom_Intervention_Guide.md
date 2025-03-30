# Creating Custom Interventions for XPECTO Epidemic 2.0

This guide walks you through the process of designing, implementing, and testing your own custom intervention strategies for the XPECTO Epidemic 2.0 Competition.

## Understanding Interventions

In XPECTO, an intervention is a function that applies a set of actions to the simulation engine. An effective intervention strategy typically consists of:

1. **Initial actions**: Measures taken at the beginning of the simulation
2. **Adaptive responses**: How your strategy responds to changing conditions
3. **Resource allocation**: How you distribute limited resources over time

## Basic Intervention Structure

A basic intervention function has this structure:

```python
def my_intervention_strategy(engine):
    """
    Custom intervention strategy
    
    Parameters:
    -----------
    engine: The simulation engine to apply strategy to
    """
    # Initial actions
    engine.set_lockdown_level(0.5)
    engine.allocate_resources('healthcare', 200)
    engine.restrict_travel(True)
    
    # Define step callback for adaptive response
    def step_callback(step, state):
        # Get current conditions
        infection_rate = state.population.infected / state.population.total
        
        # Adapt strategy based on conditions
        if infection_rate > 0.1:
            # High infection rate response
            engine.set_lockdown_level(0.7)
        elif infection_rate < 0.02:
            # Low infection rate response
            engine.set_lockdown_level(0.2)
            engine.restrict_travel(False)
    
    # Register callback to execute after each step
    engine.register_step_callback(step_callback)
```

## Accessing Simulation State

Your intervention can adapt based on the simulation's current state. Here are key properties you can access:

```python
def step_callback(step, state):
    # Current step (day) of the simulation
    current_day = step  # or state.day
    
    # Population metrics
    total_population = state.population.total
    healthy_people = state.population.healthy  # or susceptible in EnhancedEngine
    infected_people = state.population.infected
    recovered_people = state.population.recovered
    dead_people = state.population.dead  # or deaths
    
    # Calculate infection rate
    infection_rate = infected_people / total_population
    
    # Economic metrics
    initial_gdp = state.economy.initial_gdp
    current_gdp = state.economy.current_gdp
    economic_health = current_gdp / initial_gdp
    
    # Research progress (0-1)
    research_progress = state.research.progress
    
    # EnhancedEngine: Try to access variant information
    try:
        variants = engine.get_variant_status()
        # Process variant info if available
    except (AttributeError, KeyError):
        # Fall back to standard logic if variants aren't available
        pass
```

## Strategy Design Patterns

Here are some common patterns for designing effective intervention strategies:

### 1. Phase-Based Strategy

Divides the response into distinct phases based on the epidemic's progression:

```python
def phase_based_strategy(engine):
    """Strategy that transitions through different phases"""
    
    # Initial containment phase
    engine.set_lockdown_level(0.7)
    engine.restrict_travel(True)
    engine.allocate_resources('healthcare', 300)
    
    def step_callback(step, state):
        infection_rate = state.population.infected / state.population.total
        
        # Phase 1: Initial containment (days 0-30)
        if step < 30:
            # Continue initial containment
            pass
            
        # Phase 2: Stabilization (days 30-100)
        elif step < 100:
            engine.set_lockdown_level(0.5)
            engine.allocate_resources('economic', 200)
            engine.allocate_resources('research', 100)
            
        # Phase 3: Recovery (day 100+)
        else:
            if infection_rate < 0.02:
                engine.set_lockdown_level(0.3)
                engine.allocate_resources('economic', 300)
                engine.restrict_travel(False)
    
    engine.register_step_callback(step_callback)
```

### 2. Threshold-Based Strategy

Adapts responses based on crossing specific threshold values:

```python
def threshold_based_strategy(engine):
    """Strategy that responds to threshold crossings"""
    
    # Moderate initial measures
    engine.set_lockdown_level(0.4)
    engine.allocate_resources('healthcare', 150)
    
    def step_callback(step, state):
        infection_rate = state.population.infected / state.population.total
        economic_health = state.economy.current_gdp / state.economy.initial_gdp
        
        # Critical infection threshold
        if infection_rate > 0.15:
            engine.set_lockdown_level(0.8)
            engine.restrict_travel(True)
            engine.allocate_resources('healthcare', 300)
            
        # High infection threshold
        elif infection_rate > 0.08:
            engine.set_lockdown_level(0.6)
            engine.restrict_travel(True)
            engine.allocate_resources('healthcare', 200)
            
        # Moderate infection threshold
        elif infection_rate > 0.03:
            engine.set_lockdown_level(0.4)
            engine.allocate_resources('healthcare', 100)
            
        # Low infection - focus on economic recovery
        else:
            engine.set_lockdown_level(0.2)
            engine.restrict_travel(False)
            engine.allocate_resources('economic', 200)
    
    engine.register_step_callback(step_callback)
```

### 3. Balanced Multi-Objective Strategy

Balances multiple competing objectives simultaneously:

```python
def balanced_strategy(engine):
    """Strategy that balances multiple objectives"""
    
    # Balanced initial approach
    engine.set_lockdown_level(0.5)
    engine.allocate_resources('healthcare', 150)
    engine.allocate_resources('economic', 150)
    
    def step_callback(step, state):
        infection_rate = state.population.infected / state.population.total
        economic_health = state.economy.current_gdp / state.economy.initial_gdp
        
        # Healthcare system at risk
        if infection_rate > 0.1:
            engine.set_lockdown_level(0.7)
            engine.allocate_resources('healthcare', 250)
            
        # Economy at risk
        elif economic_health < 0.6:
            engine.set_lockdown_level(0.3)
            engine.allocate_resources('economic', 250)
            
        # Balanced situation - invest in research
        else:
            engine.set_lockdown_level(0.5)
            engine.allocate_resources('research', 150)
    
    engine.register_step_callback(step_callback)
```

### 4. Variant-Aware Strategy (EnhancedEngine)

Adapts to disease variants as they emerge:

```python
def variant_aware_strategy(engine):
    """Strategy that adapts to variant emergence"""
    
    # Initial measures
    engine.set_lockdown_level(0.4)
    engine.allocate_resources('research', 300)
    
    def step_callback(step, state):
        try:
            # Get variant information
            variants = engine.get_variant_status()
            
            # If variants are present
            if variants:
                # Find most transmissible variant
                most_transmissible = max(variants, key=lambda v: v.get('r0_modifier', 0))
                
                # Find most severe variant
                most_severe = max(variants, key=lambda v: v.get('mortality_modifier', 0))
                
                # Target most severe variant with research
                engine.target_research(most_severe['name'], 200)
                
                # Adjust lockdown based on transmissibility
                transmissibility = most_transmissible.get('r0_modifier', 1.0)
                engine.set_lockdown_level(min(0.9, 0.4 * transmissibility))
        except:
            # Fallback for non-variant aware engines
            infection_rate = state.population.infected / state.population.total
            
            # Standard threshold-based approach
            if infection_rate > 0.1:
                engine.set_lockdown_level(0.7)
                engine.allocate_resources('healthcare', 200)
            elif infection_rate < 0.03:
                engine.set_lockdown_level(0.3)
                engine.allocate_resources('economic', 150)
    
    engine.register_step_callback(step_callback)
```

## Testing Your Strategy

You can test your custom strategy using the utility functions provided:

```python
from src.competition.utils import create_randomized_engine, compare_strategies

# Create a test engine
engine = create_randomized_engine(seed=42)

# Define strategies
strategies = {
    "My Custom Strategy": my_intervention_strategy,
    "Baseline Aggressive": aggressive_containment,
    "Baseline Economic": economic_focus,
}

# Compare strategies
results = compare_strategies(engine, strategies, steps=200)

# Print summary
for name, metrics in results.items():
    print(f"{name}: Score = {metrics['final_score']:.4f}")
```

For more robust testing, run your strategy on multiple random scenarios:

```python
import copy
import random

# Test strategy on multiple scenarios
total_score = 0
num_tests = 10

for i in range(num_tests):
    # New random engine for each test
    engine = create_randomized_engine(seed=i+100)
    
    # Run your strategy
    engine_copy = copy.deepcopy(engine)
    my_intervention_strategy(engine_copy)
    results = engine_copy.run(200)
    
    # Save score
    total_score += results.get('final_score', 0)
    print(f"Scenario {i+1}: Score = {results.get('final_score', 0):.4f}")

# Average score across all scenarios
avg_score = total_score / num_tests
print(f"Average score: {avg_score:.4f}")
```

## Advanced Techniques

### 1. Using Multiple Callbacks

You can register multiple step callbacks for different aspects of your strategy:

```python
def advanced_strategy(engine):
    # Register separate callbacks for different aspects
    
    def healthcare_callback(step, state):
        """Manages healthcare resource allocation"""
        infection_rate = state.population.infected / state.population.total
        if infection_rate > 0.1:
            engine.allocate_resources('healthcare', 200)
        elif infection_rate > 0.05:
            engine.allocate_resources('healthcare', 100)
    
    def economic_callback(step, state):
        """Manages economic support"""
        economic_health = state.economy.current_gdp / state.economy.initial_gdp
        if economic_health < 0.7:
            engine.allocate_resources('economic', 150)
    
    # Register all callbacks
    engine.register_step_callback(healthcare_callback)
    engine.register_step_callback(economic_callback)
```

### 2. Dynamic Resource Allocation

Allocate resources dynamically based on their impact:

```python
def dynamic_allocation_strategy(engine):
    def optimize_resources(step, state):
        infection_rate = state.population.infected / state.population.total
        economic_health = state.economy.current_gdp / state.economy.initial_gdp
        
        # Calculate allocation ratios based on needs
        available = state.resources.available
        if available < 100:
            return  # Not enough resources to allocate
            
        # Dynamically determine allocation percentages
        if infection_rate > 0.1:
            # High infection - prioritize healthcare (70%) and research (30%)
            healthcare_alloc = int(available * 0.7)
            research_alloc = available - healthcare_alloc
            
            engine.allocate_resources('healthcare', healthcare_alloc)
            engine.allocate_resources('research', research_alloc)
        elif economic_health < 0.6:
            # Poor economy - prioritize economic support (80%) and healthcare (20%)
            economic_alloc = int(available * 0.8)
            healthcare_alloc = available - economic_alloc
            
            engine.allocate_resources('economic', economic_alloc)
            engine.allocate_resources('healthcare', healthcare_alloc)
        else:
            # Balanced situation - equal distribution
            per_category = available // 3
            engine.allocate_resources('healthcare', per_category)
            engine.allocate_resources('economic', per_category)
            engine.allocate_resources('research', available - 2*per_category)
    
    engine.register_step_callback(optimize_resources)
```

## Common Mistakes to Avoid

1. **Overallocating resources**: Always check available resources before allocating.

2. **Static strategies**: Strategies that don't adapt to changing conditions often perform poorly.

3. **Ignoring economic impact**: Severe lockdowns without economic support will harm your score.

4. **Neglecting research**: Research is crucial for achieving containment.

5. **Late intervention**: Failing to act early when infection rates are rising.

6. **Allocation inefficiency**: Allocating resources to areas that don't need them.

7. **Callback errors**: Ensure your callback functions handle all edge cases and don't raise exceptions.

8. **Engine-specific features**: Always handle exceptions when using EnhancedEngine features that might not be available in all engines.

## Understanding Simulation Variability

The XPECTO simulation includes controlled randomness to ensure that:

1. Different strategies produce meaningfully different outcomes
2. The same strategy may perform differently across multiple runs
3. Players must develop robust strategies that work across a range of conditions

The best strategies account for this variability and adapt dynamically based on the actual conditions they encounter, rather than relying on perfect knowledge of simulation parameters. 