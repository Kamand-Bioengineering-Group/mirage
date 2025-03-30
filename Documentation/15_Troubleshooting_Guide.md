# XPECTO Epidemic 2.0 Troubleshooting Guide

This document provides solutions for common issues that might occur when working with the XPECTO Epidemic 2.0 simulation platform.

## Table of Contents
- [Visualization Issues](#visualization-issues)
- [Runtime Errors](#runtime-errors)
- [Performance Issues](#performance-issues)
- [Competition Submission Problems](#competition-submission-problems)

## Visualization Issues

### Plots Not Appearing in Jupyter Notebooks

**Issue:** Visualizations and plots created with Matplotlib do not appear in Jupyter notebooks.

**Solution:** Add the `%matplotlib inline` magic command at the beginning of your notebook.

```python
%matplotlib inline
import matplotlib.pyplot as plt
```

This ensures that plots render directly in the notebook cells rather than in separate windows. Add this command in a cell before any plotting code or at the beginning of your import section.

If you're still having issues with plots not showing up after adding the magic command:

1. Make sure you're running all the necessary cells in the notebook in order
2. Try restarting the kernel (Kernel > Restart & Run All)
3. Check if your matplotlib backend is compatible with your environment:
   ```python
   import matplotlib
   print(matplotlib.get_backend())
   # If needed, set a specific backend:
   matplotlib.use('Agg')  # or 'TkAgg', 'Qt5Agg', etc.
   ```
4. Verify that the visualization functions are returning figures rather than calling `plt.show()`

For competition notebooks specifically, make sure to run the first code cell that contains all the imports and the `%matplotlib inline` command before trying to generate visualizations.

### Missing Legends or Labels in Plots

**Issue:** Plots appear but are missing legends, axis labels, or titles.

**Solution:** Explicitly set these elements in your plotting code:

```python
plt.figure(figsize=(10, 6))
plt.plot(data, label='Your Data')
plt.title('Your Plot Title')
plt.xlabel('X-Axis Label')
plt.ylabel('Y-Axis Label')
plt.legend()
plt.grid(True)
plt.tight_layout()
```

## Runtime Errors

### Division by Zero Error

**Issue:** `ZeroDivisionError` when running simulations, particularly in scenarios where the population is heavily affected.

**Solution:** Use safe division patterns in your code. When calculating rates or proportions:

```python
# Instead of this:
infection_rate = infected_count / total_population  # May cause division by zero

# Do this:
infection_rate = infected_count / total_population if total_population > 0 else 0

# Or use a utility function:
def safe_divide(numerator, denominator, default=0):
    return numerator / denominator if denominator != 0 else default

infection_rate = safe_divide(infected_count, total_population)
```

This pattern has been implemented in the `EnhancedEngine` to prevent crashes during extreme scenarios.

### ImportError or ModuleNotFoundError

**Issue:** Python cannot find modules that should be available.

**Solution:** Ensure your Python path includes the project root directory:

```python
import sys
from pathlib import Path
sys.path.append(str(Path.cwd().parent))  # Add parent directory to path
```

This is especially important in Jupyter notebooks, which might have different working directories.

## Performance Issues

### Slow Simulation Execution

**Issue:** Simulations take too long to run, especially with multiple trials.

**Solutions:**

1. **Reduce simulation steps for testing:**
   ```python
   # Use fewer steps during development
   results = competition.run_simulation(steps=30)  # Instead of 365
   ```

2. **Profile your strategy code** to identify bottlenecks:
   ```python
   import cProfile
   cProfile.run('competition.run_simulation(steps=365, interventions=[my_strategy])')
   ```

3. **Optimize expensive calculations** in your strategy by caching results or reducing computational complexity.

## Competition Submission Problems

### Submission Verification Failures

**Issue:** The competition system rejects your submission file.

**Solution:** Check the following:

1. Ensure your strategy is a properly defined function that accepts an `engine` parameter.
2. Verify that your strategy doesn't attempt to modify competition rules or scenarios.
3. Make sure your simulation ran for the full 365 days.
4. Check that all required result metrics are present.

You can use the verification function in the competition notebook:

```python
# Verify a submission file
verify_submission_file('path/to/your/submission_file.json')
```

### Attempts Not Being Counted

**Issue:** Your submission attempts don't seem to be tracked correctly.

**Solution:** Verify that you've toggled practice mode correctly:

```python
# For practice runs (doesn't count toward limit)
competition.toggle_practice_mode(is_practice=True)

# For official submission (counts toward limit)
competition.toggle_practice_mode(is_practice=False)
```

Also, check that you're using your consistent player name and that you've properly registered:

```python
player_id = competition.setup_player(name="Your Full Name", email="your.email@example.com")
```

## Additional Resources

If you encounter an issue not covered here, please:

1. Check the documentation in the `Documentation/` folder
2. Review example code in the `examples/` directory
3. Examine the relevant test files in the `tests/` directory

For complex issues with code, consider adding debug print statements to track values throughout the simulation:

```python
def my_strategy(engine):
    def debug_callback(step, state):
        print(f"Step {step}: Population={state.population.total}, Infected={state.population.infected}")
    
    engine.register_step_callback(debug_callback)
    # Rest of your strategy...
```

Remember to remove debug code before making your final submission. 