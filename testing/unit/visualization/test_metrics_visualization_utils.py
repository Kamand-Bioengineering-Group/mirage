import unittest
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from unittest.mock import patch
import sys
import os

# Add project root to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.visualization.metrics_visualization import (
    create_metrics_dataframe,
    plot_metrics_dashboard,
    visualize_metrics
)

class TestMetricsVisualizationUtils(unittest.TestCase):
    """Tests for metrics visualization utility functions."""
    
    def setUp(self):
        """Set up test environment."""
        # Create complete sample metrics data
        self.complete_metrics = [
            {
                "step": 0,
                "infected": 100,
                "dead": 0,
                "survived": 9900,
                "gdp": 10000,
                "initial_gdp": 10000,
                "healthcare_resources": 200,
                "economic_resources": 100,
                "research_resources": 50,
                "lockdown_level": 0.2
            },
            {
                "step": 1,
                "infected": 150,
                "dead": 5,
                "survived": 9845,
                "gdp": 9800,
                "initial_gdp": 10000,
                "healthcare_resources": 250,
                "economic_resources": 100,
                "research_resources": 50,
                "lockdown_level": 0.3
            }
        ]
        
        # Create incomplete metrics (missing infection_rate)
        self.incomplete_metrics = [
            {"step": 0, "infected": 100, "dead": 0, "survived": 9900},
            {"step": 1, "infected": 150, "dead": 5, "survived": 9845}
        ]
        
        # Create empty metrics
        self.empty_metrics = []
    
    def test_create_metrics_dataframe_complete(self):
        """Test creating a DataFrame from complete metrics."""
        df = create_metrics_dataframe(self.complete_metrics)
        
        # Check if DataFrame is created correctly
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        
        # Check if infection_rate is calculated
        self.assertIn('infection_rate', df.columns)
        self.assertEqual(df.loc[0, 'infection_rate'], 100 / 10000)  # 100 infected out of 10000 total
        self.assertEqual(df.loc[1, 'infection_rate'], 150 / 10000)  # 150 infected out of 10000 total
    
    def test_create_metrics_dataframe_incomplete(self):
        """Test creating a DataFrame from incomplete metrics."""
        df = create_metrics_dataframe(self.incomplete_metrics)
        
        # Check if DataFrame is created with all required columns
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        
        # Check that all required columns exist with default values
        required_columns = [
            'step', 'infected', 'infection_rate', 'dead', 'survived',
            'gdp', 'gdp_ratio', 'healthcare_resources', 'economic_resources',
            'research_resources', 'lockdown_level'
        ]
        
        for column in required_columns:
            self.assertIn(column, df.columns)
        
        # Check if infection_rate is calculated correctly
        self.assertIn('infection_rate', df.columns)
        self.assertEqual(df.loc[0, 'infection_rate'], 100 / 10000)  # 100 infected out of 10000 total
        self.assertEqual(df.loc[1, 'infection_rate'], 150 / 10000)  # 150 infected out of 10000 total
    
    def test_create_metrics_dataframe_empty(self):
        """Test creating a DataFrame from empty metrics."""
        df = create_metrics_dataframe(self.empty_metrics)
        
        # Check if empty DataFrame is returned
        self.assertIsInstance(df, pd.DataFrame)
        self.assertTrue(df.empty)
    
    @patch('matplotlib.pyplot.show')
    def test_plot_metrics_dashboard_complete(self, mock_show):
        """Test plotting a dashboard with complete metrics."""
        df = create_metrics_dataframe(self.complete_metrics)
        fig = plot_metrics_dashboard(df)
        
        # Check if figure is created
        self.assertIsNotNone(fig)
    
    @patch('matplotlib.pyplot.show')
    def test_plot_metrics_dashboard_incomplete(self, mock_show):
        """Test plotting a dashboard with incomplete metrics."""
        df = create_metrics_dataframe(self.incomplete_metrics)
        fig = plot_metrics_dashboard(df)
        
        # Check if figure is created despite incomplete data
        self.assertIsNotNone(fig)
    
    @patch('matplotlib.pyplot.show')
    def test_plot_metrics_dashboard_empty(self, mock_show):
        """Test plotting a dashboard with empty metrics."""
        df = create_metrics_dataframe(self.empty_metrics)
        fig = plot_metrics_dashboard(df)
        
        # Check that no figure is created for empty data
        self.assertIsNone(fig)
    
    @patch('matplotlib.pyplot.show')
    def test_visualize_metrics_complete(self, mock_show):
        """Test visualizing complete metrics directly."""
        fig = visualize_metrics(self.complete_metrics)
        
        # Check if figure is created
        self.assertIsNotNone(fig)
    
    @patch('matplotlib.pyplot.show')
    def test_visualize_metrics_with_saving(self, mock_show):
        """Test visualizing metrics with saving to file."""
        import tempfile
        
        # Create a temporary file for saving
        with tempfile.NamedTemporaryFile(suffix='.png') as temp:
            fig = visualize_metrics(self.complete_metrics, save_path=temp.name)
            
            # Check if figure is created and file exists
            self.assertIsNotNone(fig)
            self.assertTrue(os.path.exists(temp.name))
            self.assertTrue(os.path.getsize(temp.name) > 0)

if __name__ == '__main__':
    unittest.main() 