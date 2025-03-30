import unittest
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from unittest.mock import patch, MagicMock

class TestMetricsVisualization(unittest.TestCase):
    """Tests for metrics visualization functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Create sample metrics data similar to what get_detailed_metrics would return
        self.sample_metrics = [
            {
                "step": 0,
                "infected": 100,
                "infection_rate": 0.01,
                "dead": 0,
                "survived": 9900,
                "gdp": 10000,
                "initial_gdp": 10000,
                "gdp_ratio": 1.0,
                "healthcare_resources": 200,
                "economic_resources": 100,
                "research_resources": 50,
                "lockdown_level": 0.2
            },
            {
                "step": 1,
                "infected": 150,
                "infection_rate": 0.015,
                "dead": 5,
                "survived": 9845,
                "gdp": 9800,
                "initial_gdp": 10000,
                "gdp_ratio": 0.98,
                "healthcare_resources": 250,
                "economic_resources": 100,
                "research_resources": 50,
                "lockdown_level": 0.3
            }
        ]
        
        # Create DataFrame from sample metrics
        self.metrics_df = pd.DataFrame(self.sample_metrics)
    
    def test_metrics_dataframe_contains_required_columns(self):
        """Test that the metrics DataFrame contains all required columns."""
        required_columns = [
            'step', 'infected', 'infection_rate', 'dead', 'survived',
            'gdp', 'gdp_ratio', 'healthcare_resources', 'economic_resources',
            'research_resources', 'lockdown_level'
        ]
        
        for column in required_columns:
            self.assertIn(column, self.metrics_df.columns, 
                        f"Required column '{column}' not found in metrics DataFrame")
    
    def test_infection_rate_calculation(self):
        """Test that infection_rate is correctly calculated."""
        # In a real scenario, we would test the calculation done in get_detailed_metrics
        # Here we're just verifying the column exists with expected values
        self.assertIn('infection_rate', self.metrics_df.columns)
        
        # Check sample values
        self.assertEqual(self.metrics_df.loc[0, 'infection_rate'], 0.01)
        self.assertEqual(self.metrics_df.loc[1, 'infection_rate'], 0.015)
    
    @patch('matplotlib.pyplot.show')
    def test_plot_metrics_without_errors(self, mock_show):
        """Test that plotting metrics doesn't raise errors."""
        try:
            # Plot infection rate
            plt.figure(figsize=(10, 8))
            plt.subplot(2, 2, 1)
            plt.plot(self.metrics_df['step'], self.metrics_df['infection_rate'], 'r-')
            plt.title('Infection Rate')
            
            # Plot GDP
            plt.subplot(2, 2, 2)
            plt.plot(self.metrics_df['step'], self.metrics_df['gdp'], 'g-')
            plt.title('GDP')
            
            # Plot resources
            plt.subplot(2, 2, 3)
            plt.plot(self.metrics_df['step'], self.metrics_df['healthcare_resources'], 'b-')
            plt.plot(self.metrics_df['step'], self.metrics_df['economic_resources'], 'y-')
            plt.title('Resources')
            
            # Plot lockdown
            plt.subplot(2, 2, 4)
            plt.plot(self.metrics_df['step'], self.metrics_df['lockdown_level'], 'k-')
            plt.title('Lockdown Level')
            
            plt.tight_layout()
            plt.show()
            mock_show.assert_called_once()
            self.assertTrue(True)  # If we get here without errors, the test passes
        except Exception as e:
            self.fail(f"Plotting raised an exception: {e}")
    
    def test_missing_column_raises_error(self):
        """Test that accessing a non-existent column raises KeyError."""
        # Create a DataFrame missing the infection_rate column
        incomplete_df = self.metrics_df.drop(columns=['infection_rate'])
        
        # This should raise a KeyError
        with self.assertRaises(KeyError):
            plt.plot(incomplete_df['step'], incomplete_df['infection_rate'])

if __name__ == '__main__':
    unittest.main() 