# Competition Evaluation Guide

This document explains how to use the Competition Evaluation Notebook to test, evaluate, and submit strategies for the XPECTO epidemic competition.

## Overview

The Competition Evaluation Notebook (`competition_evaluation.ipynb`) provides a standardized environment for:

1. Testing your strategies in practice mode
2. Evaluating performance with detailed metrics
3. Visualizing performance over time
4. Creating official submissions for the competition

## Getting Started

### Accessing the Notebook

The competition evaluation notebook can be generated using the `create_competition_notebook.py` script located in the `notebooks` directory:

```bash
cd notebooks
python create_competition_notebook.py
```

This will create a new `competition_evaluation.ipynb` file in the current directory.

### Player Registration

When using the notebook, you'll first need to register as a player:

```python
# Player information - please use your real name and email
PLAYER_NAME = "Your Name"
PLAYER_EMAIL = "your.email@example.com"  # Optional but recommended

# Initialize the competition system
engine = EnhancedEngine()
competition = CompetitionManager(data_dir="practice_data", engine=engine)

# Register player
player_id = competition.setup_player(name=PLAYER_NAME, email=PLAYER_EMAIL)
```

### Competition Scenarios

The competition includes several scenarios of varying difficulty:

1. **Standard**: A balanced scenario with moderate difficulty
2. **Easy**: Lower initial infection rate and higher resources
3. **Hard**: Higher transmission rate and lower initial resources
4. **Variants**: Multiple disease variants that emerge during the simulation
5. **Limited Resources**: Severely restricted initial resources

## Defining Your Strategy

Your strategy should be defined as a function that accepts an `engine` parameter:

```python
def my_strategy(engine):
    """
    My competition strategy for epidemic control.
    
    Parameters:
    -----------
    engine : EnhancedEngine
        The simulation engine instance
    """
    # Initial settings
    engine.set_lockdown_level(0.5)  # 50% lockdown
    engine.allocate_resources('healthcare', 400)
    engine.allocate_resources('economy', 300)
    engine.allocate_resources('research', 300)
    
    # Define a callback function for adaptive response
    def adaptive_response(step, state):
        total_population = max(1, state.population.total)
        infection_rate = state.population.infected / total_population
        
        # Adjust lockdown based on infection rate
        if infection_rate > 0.15:
            engine.set_lockdown_level(0.8)
            # Reallocate resources...
        elif infection_rate > 0.05:
            engine.set_lockdown_level(0.5)
            # Reallocate resources...
        else:
            engine.set_lockdown_level(0.3)
            # Reallocate resources...
    
    # Register the callback function
    engine.register_step_callback(adaptive_response)
```

## Practice Mode

Before making official submissions, you can test your strategy in practice mode:

```python
# Make sure we're in practice mode
competition.toggle_practice_mode(is_practice=True)

# Setup and run the simulation
competition.setup_simulation()
practice_results = competition.run_simulation(
    steps=365,  # Full year simulation
    interventions=[my_strategy]
)
```

## Performance Visualization

The notebook includes tools for visualizing your strategy's performance:

```python
# Create visualizer
evaluator = StrategyEvaluator()
visualizer = EvaluationVisualizer(evaluator)

# Evaluate your strategy
evaluation = evaluator.evaluate_strategy(
    name="My Strategy",
    strategy=my_strategy,
    steps=365
)

# Generate visualizations
visualizer.plot_score_breakdown("My Strategy")
visualizer.plot_metric_over_time(
    strategies=["My Strategy"],
    metric="infected",
    title="Infection Curve Over Time"
)
```

### Troubleshooting Visualizations

If plots don't appear in your notebook, add this to a cell at the beginning:

```python
%matplotlib inline
import matplotlib.pyplot as plt
```

This ensures that matplotlib is configured to display plots inline in Jupyter notebooks.

## Official Submissions

When you're ready to make an official submission:

```python
# Check remaining attempts
remaining_attempts = competition.get_remaining_attempts()

# Create official submission
submission_file, official_results = create_official_submission(
    my_strategy, 
    SELECTED_SCENARIO
)

# Verify submission
is_valid = verify_submission_file(submission_file)
```

## Submission Rules

1. **Attempt Limits**: Maximum of 3 official attempts per scenario
2. **Required Duration**: All official submissions must run for the full 365 days
3. **Verification**: All submissions include timestamped code and execution data
4. **No Tampering**: Anti-tampering measures are in place to ensure fair competition

## Performance Metrics

Your strategy will be evaluated on multiple metrics:

1. **Final Score**: Overall performance score (0-1)
2. **Population Survived**: Percentage of initial population that survived
3. **GDP Preserved**: Percentage of GDP maintained throughout the simulation
4. **Infection Control**: How effectively infections were contained
5. **Resource Efficiency**: How efficiently resources were allocated
6. **Time to Containment**: Days until the epidemic was brought under control
7. **Variant Control**: (When applicable) Effectiveness against disease variants

## Working with the EnhancedEngine

The `EnhancedEngine` used in the competition adds several features over the basic simulation engine:

1. **Disease Variants**: Multiple variants can emerge with different characteristics
2. **Improved Realism**: More realistic transmission and economic modeling
3. **Resource Allocation**: More granular control over resource allocation
4. **Research Effects**: Research can improve treatment effectiveness and help counter variants

For more information on the EnhancedEngine, see the [Enhanced Engine Documentation](07_Enhanced_Engine_and_Variants.md).

## Tips for Success

1. **Adaptive Strategies**: Use the callback function to adapt to changing conditions
2. **Variant Handling**: Be prepared for new disease variants that may emerge
3. **Balance Resources**: Finding the right balance between healthcare, economy, and research is critical
4. **Test Thoroughly**: Use practice mode to refine your strategy before making official submissions
5. **Data-Driven Decisions**: Use the visualizations to understand where your strategy can be improved 