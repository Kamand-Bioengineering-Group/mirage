# Engine Parameters and Configuration

This document provides a comprehensive overview of the different engines available in XPECTO Epidemic 2.0, their parameters, and how they affect gameplay.

## Available Engines

XPECTO Epidemic 2.0 includes several simulation engines with varying levels of complexity:

### 1. MockEngine

A simplified engine used primarily for practice mode and testing. It provides basic epidemic dynamics while being computationally light.

### 2. EnhancedEngine

An advanced engine that incorporates more realistic epidemiological models, variant emergence, and complex economic effects. This engine produces more diverse outcomes for different strategies.

## Engine Parameters

### Common Parameters

These parameters are available in all engine types:

| Parameter | Default | Description | Optional |
|-----------|---------|-------------|----------|
| `initial_population` | 10,000 | Total population in the simulation | Yes |
| `name` | "MockEngine" or "EnhancedEngine" | Name of the engine instance | Yes |
| `speed` | 1 | Simulation speed multiplier | Yes |
| `history_persistence` | 100 | How often to save historical data | Yes |
| `seed` | None | Random seed for reproducibility | Yes |

### MockEngine Specific Parameters

The MockEngine uses these core parameters to model the epidemic:

#### Disease Parameters

| Parameter | Default | Description | Optional |
|-----------|---------|-------------|----------|
| `r0_base` | 3.0 | Basic reproduction number | Yes |
| `infection_duration` | 14 | Days an infected person remains infectious | Yes |
| `mortality_rate_base` | 0.02 | Base mortality rate without healthcare | Yes |
| `recovery_rate` | 0.1 | Base recovery rate per step | Yes |

#### Intervention Effects

| Parameter | Default | Description | Optional |
|-----------|---------|-------------|----------|
| `lockdown_r0_reduction` | 0.85 | Maximum R0 reduction from lockdown | Yes |
| `healthcare_mortality_reduction` | 0.9 | Maximum reduction in mortality from healthcare | Yes |
| `economic_support_efficiency` | 0.9 | Effectiveness of economic support | Yes |
| `research_effectiveness` | 0.008 | Per-unit research effectiveness | Yes |
| `testing_detection_improvement` | 0.7 | Maximum improvement from testing | Yes |

### EnhancedEngine Specific Parameters

The EnhancedEngine includes all MockEngine parameters plus these additional parameters:

#### Enhanced Disease Parameters

| Parameter | Default | Description | Optional |
|-----------|---------|-------------|----------|
| `r0_base` | 3.8 | Higher base R0 | Yes |
| `r0_variance` | 0.6 | R0 can vary by this amount | Yes |
| `mortality_rate_base` | 0.025 | Base mortality rate | Yes |
| `mortality_variance` | 0.01 | Variation in mortality rate | Yes |
| `incubation_period` | 5 | Days before becoming infectious | Yes |
| `recovery_period` | 14 | Days to recovery | Yes |
| `immunity_period` | 120 | Days immunity lasts | Yes |
| `reinfection_risk` | 0.3 | Chance of reinfection after immunity wanes | Yes |
| `asymptomatic_rate` | 0.4 | Percentage of cases that are asymptomatic | Yes |
| `asymptomatic_transmission` | 0.6 | Relative transmission rate for asymptomatic | Yes |
| `variant_emergence_rate` | 0.01 | Base chance of new variants emerging | Yes |
| `variant_prevalence_increase` | 0.02 | Base rate of variant prevalence increase | Yes |

#### Enhanced Intervention Effects

| Parameter | Default | Description | Optional |
|-----------|---------|-------------|----------|
| `lockdown_r0_reduction` | 0.8 | Maximum R0 reduction from lockdown | Yes |
| `lockdown_diminishing_factor` | 0.85 | Each subsequent lockdown is less effective | Yes |
| `lockdown_compliance_decay` | 0.02 | Daily reduction in compliance | Yes |
| `economic_support_efficiency` | 0.85 | Effectiveness of economic support | Yes |
| `economic_diminishing_factor` | 0.9 | Diminishing returns on economic support | Yes |
| `healthcare_mortality_reduction` | 0.85 | Maximum reduction in mortality from healthcare | Yes |
| `healthcare_capacity_threshold` | 0.7 | Healthcare system overwhelm threshold | Yes |
| `healthcare_overwhelm_penalty` | 2.5 | Multiplier for mortality when overwhelmed | Yes |
| `research_effectiveness` | 0.012 | Per-unit research effectiveness | Yes |
| `research_breakthrough_threshold` | 0.8 | Research level for breakthrough | Yes |
| `research_breakthrough_effect` | 0.6 | Effectiveness multiplier after breakthrough | Yes |
| `travel_restriction_effectiveness` | 0.7 | Effectiveness of travel restrictions | Yes |
| `travel_economic_impact` | 0.15 | Economic impact of travel restrictions | Yes |

#### Region-Specific Parameters

The EnhancedEngine models different regions with distinct characteristics:

| Region Type | Population | Density | Economic Weight |
|-------------|------------|---------|----------------|
| Urban | 70% | 3.0 | 80% |
| Rural | 30% | 0.7 | 20% |

#### Economic Sector Parameters

The EnhancedEngine models different economic sectors with varying impacts:

| Sector | GDP Weight | Lockdown Impact |
|--------|------------|----------------|
| Essential | 30% | 20% reduction |
| In-person Services | 40% | 80% reduction |
| Remote Capable | 30% | 30% reduction |

## Disease Variants

The EnhancedEngine includes a variant system that models the emergence and spread of virus mutations:

### Predefined Variants

| Variant | Transmissibility | Mortality | Immune Escape | Emergence Threshold |
|---------|-----------------|-----------|---------------|---------------------|
| Alpha   | 1.5x base       | 1.1x base | 10%           | 20% population infected |
| Beta    | 1.3x base       | 1.3x base | 30%           | 30% population infected |
| Gamma   | 1.7x base       | 1.2x base | 50%           | 40% population infected |

### How Variants Affect Gameplay

Variants emerge based on the cumulative proportion of the population that has been infected. Once emerged, they affect:

1. **Transmissibility**: Higher R0 values increase infection rates
2. **Mortality**: Higher mortality rates increase deaths
3. **Immune Escape**: Ability to reinfect recovered individuals
4. **Research Effectiveness**: Variants can reduce vaccine/treatment effectiveness

### Targeting Variants with Research

Players can allocate research specifically toward a particular variant using:

```python
engine.target_research(variant_name, amount)
```

This provides several benefits:
- 20% more effective than general research
- Reduces the prevalence of the targeted variant
- Counters the variant's immune escape capabilities

## How Parameters Affect Scoring

The scoring system in XPECTO evaluates player performance across multiple metrics:

1. **Population Survived (30%)**: Affected by:
   - Base mortality rate
   - Healthcare effectiveness
   - Variant mortality modifiers
   - Healthcare capacity thresholds

2. **GDP Preserved (20%)**: Affected by:
   - Lockdown levels
   - Economic support efficiency
   - Sector-specific lockdown impacts
   - Travel restrictions

3. **Infection Control (20%)**: Affected by:
   - R0 and its modifiers
   - Lockdown effectiveness
   - Travel restrictions
   - Testing effectiveness
   - Variant transmissibility

4. **Resource Efficiency (15%)**: Affected by:
   - Resource allocation balance
   - Diminishing returns on investments
   - Resource targeting effectiveness

5. **Time to Containment (15%)**: Affected by:
   - Research effectiveness
   - Containment thresholds
   - Variant prevalence
   - Research breakthrough thresholds

6. **Variant Control** (EnhancedEngine only): Affected by:
   - Research targeting
   - Variant prevalence reduction
   - Adaptive strategy effectiveness

## Engine Parameter Customization

If you wish to customize engine parameters for testing or advanced simulations:

```python
# Create engine with custom parameters
engine = EnhancedEngine(seed=42)

# Modify disease parameters
engine.disease_params["r0_base"] = 4.0
engine.disease_params["mortality_rate_base"] = 0.03

# Modify intervention effects
engine.intervention_effects["lockdown_r0_reduction"] = 0.75
engine.intervention_effects["healthcare_mortality_reduction"] = 0.85

# Create custom disease variant
custom_variant = DiseaseVariant(
    name="Omega",
    r0_modifier=2.0,
    mortality_modifier=1.5,
    immune_escape=0.6,
    emergence_threshold=0.5
)
engine.potential_variants.append(custom_variant)

# Initialize and run
engine.initial_population = 100000
engine.reset()
```

## Conclusion

The engine parameters significantly impact simulation dynamics and outcomes. While the MockEngine provides a simplified model suitable for basic testing, the EnhancedEngine offers a more realistic and challenging simulation environment with:

- More complex disease dynamics
- Intervention fatigue and diminishing returns
- Region and sector-specific impacts
- Dynamic variant emergence and evolution

Understanding these parameters will help you develop more effective strategies tailored to different scenarios and conditions. 