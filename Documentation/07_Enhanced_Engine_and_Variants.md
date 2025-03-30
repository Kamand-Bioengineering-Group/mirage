# Enhanced Engine and Variant System

This document explains the enhanced engine capabilities and the variant system added to XPECTO Epidemic 2.0.

## Enhanced Engine Overview

The EnhancedEngine is an improved epidemic simulation engine that ensures different intervention strategies produce significantly different outcomes. It builds upon the original MockEngine but includes several advanced features:

1. **Network-based disease spread** (SIR model with contact networks)
2. **Intervention fatigue and compliance modeling**
3. **Region-specific effects**
4. **Variable intervention effectiveness**
5. **Multi-dimensional economic impacts**
6. **Synergistic and antagonistic intervention effects**
7. **Variant strain emergence system**

## Disease Variant System

A major enhancement to the simulation is the addition of a dynamic disease variant system.

### What Are Variants?

In epidemiology, variants are mutations of a virus that may have different characteristics than the original strain. In XPECTO, variants can have:

- **Higher transmissibility** (increased R0)
- **Different mortality rates**
- **Immune escape ability** (can reinfect recovered individuals)
- **Emergence thresholds** (population infection level required for variant to emerge)

### Predefined Variants

The enhanced engine includes several predefined variants:

| Variant | Transmissibility | Mortality | Immune Escape | Emergence Threshold |
|---------|-----------------|-----------|---------------|---------------------|
| Alpha   | 1.5x base       | 1.1x base | 10%           | 20% population infected |
| Beta    | 1.3x base       | 1.3x base | 30%           | 30% population infected |
| Gamma   | 1.7x base       | 1.2x base | 50%           | 40% population infected |

### How Variants Emerge and Spread

Variants have a chance to emerge once the total infected proportion of the population reaches their emergence threshold. The probability is controlled by the `variant_emergence_rate` parameter.

Once emerged, variants:
- Start with a small prevalence (5%)
- Grow based on their transmissibility advantage
- Compete with other variants in a realistic way
- May decline if targeted by research efforts

## New API for Variant Management

The enhanced engine provides new methods to interact with the variant system:

### Targeting Research at Variants

```python
engine.target_research(variant_name, amount)
```

This allows players to allocate research specifically toward a particular variant, which:
- Is 20% more effective than general research
- But costs 10% more resources
- Reduces the prevalence and effectiveness of the targeted variant over time

### Monitoring Variant Status

```python
variant_status = engine.get_variant_status()
```

Returns information about all potential variants:
- Name
- Active status
- Prevalence
- R0 modifier
- Mortality modifier
- Immune escape percentage

### Displaying Variant Information

```python
engine.display_variant_info()
```

Prints information about active variants to the console.

## Variant Strategy Examples

### Ignore Variants Strategy

This strategy follows a standard approach regardless of variants:

```python
def ignore_variants_strategy(engine):
    # Apply standard balanced approach regardless of variants
    engine.set_lockdown_level(0.4)
    engine.allocate_resources('healthcare', 300)
    engine.allocate_resources('economic', 100)
    engine.allocate_resources('research', 200)
```

### Target Dominant Variant Strategy

This strategy focuses resources on the most prevalent variant:

```python
def target_dominant_variant_strategy(engine):
    # Initial setup with research focus
    engine.set_lockdown_level(0.3)
    engine.allocate_resources('healthcare', 200)
    engine.allocate_resources('research', 400)
    
    def monitor_and_respond(step, state):
        # Get variant information
        variants = engine.get_variant_status()
        
        if variants:
            # Find and target the most prevalent variant
            dominant_variant = max(variants, key=lambda v: v['prevalence'])
            engine.target_research(dominant_variant['name'], 200)
            
            # Adjust lockdown based on variant transmissibility
            engine.set_lockdown_level(min(0.8, dominant_variant['r0_modifier'] * 0.4))
        
    engine.register_step_callback(monitor_and_respond)
```

### Adaptive Variant Strategy

This strategy adapts to variant characteristics, targeting research at the most severe variants and adjusting lockdown based on transmissibility:

```python
def adaptive_variant_strategy(engine):
    # Initial balanced approach
    engine.set_lockdown_level(0.2)
    engine.allocate_resources('healthcare', 200)
    engine.allocate_resources('research', 500)
    
    def monitor_and_respond(step, state):
        variants = engine.get_variant_status()
        infection_rate = state.population.infected / state.population.total
        
        if variants:
            # Find the most transmissible and most severe variants
            most_transmissible = max(variants, key=lambda v: v['r0_modifier'])
            most_severe = max(variants, key=lambda v: v['mortality_modifier'])
            
            # Adapt lockdown level based on transmissibility
            engine.set_lockdown_level(min(0.8, most_transmissible['r0_modifier'] * 0.5))
            
            # Target research at the most severe variant
            engine.target_research(most_severe['name'], 100)
            
            # Healthcare allocation based on severity
            healthcare_allocation = min(500, int(most_severe['mortality_modifier'] * 300))
            engine.allocate_resources('healthcare', healthcare_allocation)
        
    engine.register_step_callback(monitor_and_respond)
```

## Impact on Scoring

The enhanced engine's variant system affects scoring through:

1. **A new "variant_control" metric** that evaluates effectiveness against variants
2. **Adjustment of other metrics** based on variant effects:
   - Increased mortality affects population survival
   - Increased transmissibility affects infection control
   - Immune escape affects reinfection rates

## Using the Enhanced Engine

The enhanced engine can be used in place of the standard engine for more challenging and realistic simulations:

```python
from src.competition.testing.enhanced_engine import EnhancedEngine

# Create enhanced engine (optional random seed)
engine = EnhancedEngine(seed=42)

# Configure engine
engine.initial_population = 1000000
engine.reset()

# Apply your strategy
my_strategy(engine)

# Run simulation
results = engine.run(steps=120)

# Check results
print(f"Population survived: {results['population_survived']:.4f}")
print(f"GDP preserved: {results['gdp_preserved']:.4f}")
print(f"Variant control: {results.get('variant_control', 'N/A')}")
```

## Advanced Engine Parameters

The enhanced engine includes many configurable parameters:

- Disease parameters (`r0_base`, `mortality_rate_base`, etc.)
- Variant parameters (`variant_emergence_rate`, etc.)
- Intervention effects (`lockdown_r0_reduction`, etc.)
- Regional parameters (urban vs. rural populations)
- Economic sector definitions

These can be modified to create custom scenarios with different characteristics.

## Next Steps

- Try running the `variant_test.py` script to see how different strategies perform
- Develop your own variant-aware strategies
- Experiment with different engine parameter settings
- Incorporate variant management into your competition strategies 