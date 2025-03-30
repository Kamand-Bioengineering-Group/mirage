# XPECTO Testing Suite

This directory contains tests for the XPECTO project to ensure code quality and catch common errors.

## Test Structure

- `unit/`: Unit tests for individual components
  - `competition/`: Tests for the competition module
    - `test_competition_manager.py`: Tests for CompetitionManager class
    - `test_simulation_integration.py`: Tests for SimulationIntegration class

## Running Tests

You can run all tests with:

```bash
python -m unittest discover -s testing
```

Or run a specific test file:

```bash
python -m unittest testing.unit.competition.test_simulation_integration
```

## Common Tests

These tests check for some of the most common errors:

1. **String to Int Conversion**: Tests that string seeds are properly converted to integers
2. **Dictionary Handling**: Tests handling of dictionary-type data structures
3. **Plotting Compatibility**: Tests that metrics are properly formatted for plotting
4. **Parameter Handling**: Tests that API methods use correct parameter names

## Adding New Tests

When adding new tests:

1. Create a new test file in the appropriate directory
2. Inherit from `unittest.TestCase`
3. Add test methods that start with `test_`
4. Use assertions to verify expected behavior
5. Run the tests to ensure they pass

## Mock Objects

Many tests use mock objects to isolate the component being tested. This allows testing specific behavior without requiring the entire system to be operational. 