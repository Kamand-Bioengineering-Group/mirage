# Frequently Asked Questions (FAQ)

## General Questions

### What is XPECTO Epidemic 2.0?
XPECTO Epidemic 2.0 is a simulation-based competition where players develop strategies to manage a simulated epidemic. Players must balance public health outcomes, economic impacts, and resource efficiency to achieve the highest scores.

### How do I get started?
Begin by reading the [01_Introduction](01_Introduction.md) and [02_How_To_Play](02_How_To_Play.md) guides, then open the notebooks/practice_playground.ipynb notebook to start experimenting with strategies.

### What programming knowledge do I need?
Basic Python programming skills are required. You'll need to understand how to define functions, use conditional statements (if/else), and work with variables. The [03_Intervention_Strategies](03_Intervention_Strategies.md) guide provides examples you can modify.

### Can I play without coding?
No, the competition requires writing Python code to define your intervention strategies. However, you can start by modifying the example strategies provided in the documentation.

## Gameplay Questions

### How do I control the simulation?
You create intervention functions that call methods on the simulation engine like `engine.set_lockdown_level()` and `engine.allocate_resources()`. See the [03_Intervention_Strategies](03_Intervention_Strategies.md) guide for details.

### What's the difference between practice and competition mode?
- **Practice Mode**: Unlimited attempts, results not counted for ranking
- **Competition Mode**: Limited to 3 attempts per scenario, results recorded for leaderboard ranking

### How long does each simulation run?
A standard simulation runs for 730 steps (simulated days/time units), representing approximately 2 years of epidemic progression.

### Can I pause or interrupt a running simulation?
No, once started, a simulation runs to completion for the specified number of steps.

### How do I know if my strategy is working?
After each simulation run, you can view your score breakdown using `competition.display_score(results)` to see how well you performed across different metrics.

### Can I see the history of my previous attempts?
Yes, use `competition.display_player_attempts()` to view your attempt history, including scores and timestamps.

## Engine and Simulation Questions

### What are the different engines available in XPECTO?
XPECTO includes two main simulation engines:
- **MockEngine**: A simplified engine used for practice mode and testing
- **EnhancedEngine**: An advanced engine with more realistic disease dynamics, variant emergence, and economic modeling

### How do I switch between engines?
By default, practice mode uses the MockEngine. To use the EnhancedEngine:

```python
from src.competition.testing.enhanced_engine import EnhancedEngine

# Create enhanced engine
engine = EnhancedEngine(seed=42)  # Optional random seed
engine.reset()

# Apply your strategy
my_strategy(engine)

# Run simulation
results = engine.run(steps=200)
```

### What are disease variants and how do they affect gameplay?
In the EnhancedEngine, disease variants are mutations that can emerge during the simulation with different properties:
- Higher transmissibility (increased R0)
- Different mortality rates
- Immune escape ability (can reinfect recovered individuals)

Variants emerge based on the cumulative proportion of the population that has been infected. Different strategies may be needed to effectively control variants.

### How do I handle disease variants in my strategy?
Use these special methods in the EnhancedEngine:

```python
# Get current variant status
variants = engine.get_variant_status()

# Target research at a specific variant
engine.target_research("Alpha", 200)  # Variant name and resource amount

# Display variant information
engine.display_variant_info()
```

### Why do different strategies sometimes produce similar scores?
This can happen for several reasons:
1. The scoring system averages multiple metrics, smoothing out differences
2. Some engine parameters may create similar outcomes for different approaches
3. Linear relationships between interventions and outcomes can limit differentiation

See [09_Improving_Strategy_Differentiation](09_Improving_Strategy_Differentiation.md) for more details on this issue.

## Technical Questions

### Why am I getting an error about EngineV1 parameters?
The full EngineV1 requires several parameters that might not be available in a test environment. We've implemented a MockEngine that automatically replaces EngineV1 in notebook environments to avoid this issue.

### How do I fix the "TypeError: __init__() missing required arguments" error?
There are two solutions:
1. Use our automatic testing mode which patches EngineV1 with MockEngine (enabled by default in notebooks)
2. Provide all required parameters to EngineV1 if using the actual engine

### What does "KeyError: 'variant_control'" mean?
This error typically occurs when trying to access variant-related features in the MockEngine. Variant features are only available in the EnhancedEngine. Always check which engine you're using and handle exceptions appropriately:

```python
try:
    variants = engine.get_variant_status()
    # Handle variant-specific logic
except (AttributeError, KeyError):
    # Fall back to standard strategy when variants aren't available
    pass
```

### Can I save my strategies for later use?
Yes, you can save your strategy functions in separate Python files and import them into your notebooks.

### How do I reset the simulation?
Call `competition.setup_simulation()` to reset the simulation to its initial state before running with a new strategy.

### Can I run multiple simulations in parallel?
No, the current implementation runs simulations sequentially.

## Strategy Questions

### What makes a good strategy?
Effective strategies balance multiple factors and adapt to changing conditions. They typically combine:
- Appropriate lockdown levels based on infection rates
- Strategic resource allocation
- Different approaches for different phases of the epidemic
- Adaptation to disease variants (in EnhancedEngine)

### Should I focus more on health or economy?
This depends on your overall strategy. Some successful approaches prioritize early containment to minimize long-term economic impact, while others accept higher infection rates to preserve economic activity. The scoring system rewards balanced approaches.

### How important is timing?
Timing is critical. Early intervention can prevent exponential growth of infections, but premature severe measures may waste resources or cause unnecessary economic damage.

### Can I win by focusing on just one aspect?
While you might score well in individual metrics, the overall scoring system is designed to reward balanced approaches. However, in some specialized scenarios, focusing on specific aspects might be advantageous.

### What's the most important metric to optimize?
Population survival carries the highest weight (30%), but a balanced approach addressing all metrics typically performs best overall.

### How should I adapt my strategy for different engines?
- **For MockEngine**: Focus on balanced interventions and timing
- **For EnhancedEngine**: Consider variant emergence, regional effects, diminishing returns, and intervention fatigue

## Competition Questions

### How is the leaderboard calculated?
The leaderboard ranks players based on their best official attempts for each required scenario. See the [04_Competition_Rules](04_Competition_Rules.md) for detailed scoring information.

### Can I modify my strategy during a simulation run?
Yes, you can use callback functions to adapt your strategy during the simulation based on changing conditions. This is a key feature of advanced strategies.

### How many official attempts do I get?
You are limited to 3 official attempts per scenario.

### Can I delete or replace an official attempt?
No, once submitted, official attempts cannot be deleted or replaced.

### Are my practice attempts visible to other players?
No, practice attempts are private and only visible to you.

### Can I see other players' strategies?
No, strategies are private during the competition. After the competition concludes, some players might choose to share their approaches.

### What happens if there's a tie in scores?
Tiebreakers are applied in this order:
1. Higher score in the Challenging scenario
2. Higher score in specialized scenarios (if applicable)
3. Earlier submission timestamp

## Technical Support

### Where can I report bugs or issues?
Contact the competition organizers through the designated support channels listed in the Competition Rules document.

### Can I modify the simulation engine?
No, modifying the simulation engine is not allowed and may result in disqualification.

### What if I accidentally corrupt my data files?
The system includes backup and recovery mechanisms. Use the data management utilities to restore from backups if needed.

### Can I run the simulation on my own computer?
Yes, all the necessary code is provided in the repository. Just ensure you have the required dependencies installed. 