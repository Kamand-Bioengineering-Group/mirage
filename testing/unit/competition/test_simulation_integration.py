import unittest
import random
from unittest.mock import MagicMock, patch
import numpy as np
import pandas as pd

from src.competition.services.simulation_integration import SimulationIntegration
from src.competition.core.models import Scenario


class MockEngine:
    """Mock engine for testing that mimics the basic structure of the actual engine."""
    def __init__(self):
        self.metrics = {
            'population': {
                'total': 10000,
                'infected': 100,
                'dead': 0
            },
            'economy': {
                'current_gdp': 1000,
                'initial_gdp': 1000
            },
            'resources': {
                'available': 5000,
                'total_spent': 0,
                'total_initial': 5000
            }
        }
        self.callbacks = []
        self.parameters = {}
        self.initial_resources = 5000
        self.current_resources = 5000
    
    def set_initial_resources(self, value):
        """Set initial resources."""
        self.initial_resources = value
        self.current_resources = value
        self.metrics['resources']['available'] = value
        self.metrics['resources']['total_initial'] = value
    
    def register_step_callback(self, callback):
        """Register a callback function."""
        self.callbacks.append(callback)
    
    def run(self, steps):
        """Run the simulation for the specified number of steps."""
        for step in range(steps):
            # Update metrics to simulate changes
            self.metrics['population']['infected'] = 100 + step * 10
            self.metrics['resources']['total_spent'] += 50
            self.metrics['resources']['available'] -= 50
            
            # Call callbacks
            for callback in self.callbacks:
                callback(step, self)


class TestSimulationIntegration(unittest.TestCase):
    """Test cases for the SimulationIntegration class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_engine = MockEngine()
        self.simulation = SimulationIntegration(engine=self.mock_engine)
    
    def test_string_seed_conversion(self):
        """Test that string seeds are properly converted to integers."""
        # Create a scenario with a string seed
        scenario = MagicMock(spec=Scenario)
        scenario.seed = "standard_2023"
        scenario.r0 = 2.5
        scenario.initial_infections = 100
        scenario.initial_resources = 1000
        scenario.difficulty = "standard"
        scenario.name = "Test Scenario"
        scenario.parameters = {}
        
        # Configure from scenario - this should not raise a ValueError
        try:
            self.simulation.configure_from_scenario(scenario)
            # If we get here, the test passes
            passed = True
        except ValueError:
            passed = False
        
        self.assertTrue(passed, "Failed to handle non-numeric string seed")
    
    def test_dictionary_infections_handling(self):
        """Test handling of dictionary-type initial infections."""
        # Create a scenario with dictionary infections
        scenario = MagicMock(spec=Scenario)
        scenario.seed = 42
        scenario.r0 = 2.5
        scenario.initial_infections = {"region1": 50, "region2": 30, "region3": 20}
        scenario.initial_resources = 1000
        scenario.difficulty = "standard"
        scenario.name = "Test Scenario"
        scenario.parameters = {}
        
        # Configure from scenario - this should not raise any errors
        try:
            self.simulation.configure_from_scenario(scenario)
            # If we get here, the test passes
            passed = True
        except (TypeError, ValueError):
            passed = False
        
        self.assertTrue(passed, "Failed to handle dictionary-type initial infections")
    
    def test_metrics_processing_for_plotting(self):
        """Test that metrics are properly processed for plotting."""
        # Create sample metrics with nested structures
        sample_metrics = [
            {
                "step": 0,
                "infected": 100,
                "nested": {"value1": 10, "value2": 20},
                "complex_obj": object()
            },
            {
                "step": 1,
                "infected": 110,
                "nested": {"value1": 15, "value2": 25},
                "complex_obj": object()
            }
        ]
        
        # Process the metrics
        processed = self.simulation._prepare_metrics_for_plotting(sample_metrics)
        
        # Verify processing
        self.assertEqual(len(processed), 2)
        self.assertIn("step", processed[0])
        self.assertIn("infected", processed[0])
        self.assertIn("nested_value1", processed[0])
        self.assertNotIn("complex_obj", processed[0])
        
        # Verify all values are numeric
        for metric in processed:
            for key, value in metric.items():
                self.assertIsInstance(value, float)
    
    def test_simulation_run_with_plotting(self):
        """Test that simulation results can be properly plotted."""
        # Run a simulation
        self.simulation.run_simulation(steps=10)
        
        # Get results
        results = self.simulation._process_results()
        
        # Verify metrics_history exists and can be converted to DataFrame
        self.assertIn("metrics_history", results)
        
        # Convert to DataFrame (should not raise errors)
        try:
            df = pd.DataFrame(results["metrics_history"])
            # Try to plot (we don't need to actually create the plot)
            # This is to verify the data structure is compatible
            if 'step' in df.columns and 'infected' in df.columns:
                x = df['step'].to_numpy()
                y = df['infected'].to_numpy()
                # If we can convert to numpy arrays, plotting should work
                passed = True
            else:
                passed = False
        except Exception:
            passed = False
        
        self.assertTrue(passed, "Failed to prepare metrics for plotting")


if __name__ == '__main__':
    unittest.main() 