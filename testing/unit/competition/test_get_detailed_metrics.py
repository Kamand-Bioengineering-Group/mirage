import unittest
import os
import json
from unittest.mock import MagicMock
from datetime import datetime

from src.competition.competition_manager import CompetitionManager
from src.competition.core.models import PlayerAttempt, SimulationResults


class TestGetDetailedMetrics(unittest.TestCase):
    """Test the get_detailed_metrics method."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a competition manager with mocked dependencies
        self.competition_manager = CompetitionManager(data_dir="/tmp/test_data")
        self.competition_manager.competition_service = MagicMock()
        
        # Set current player and scenario
        self.competition_manager.current_player_id = "test_player"
        self.competition_manager.current_player_name = "Test Player"
        self.competition_manager.current_scenario_id = "test_scenario"
        
        # Create sample metrics history
        metrics_history = [
            {
                "population": {"total": 10000, "infected": 100, "dead": 10},
                "economy": {"current_gdp": 950, "initial_gdp": 1000},
                "resources": {"available": 900, "total_spent": 100},
                "resource_allocation": {"healthcare": 60, "economic": 30, "research": 10},
                "interventions": {"lockdown_level": 0.5, "travel_restricted": True}
            },
            {
                "population": {"total": 10000, "infected": 150, "dead": 15},
                "economy": {"current_gdp": 920, "initial_gdp": 1000},
                "resources": {"available": 850, "total_spent": 150},
                "resource_allocation": {"healthcare": 80, "economic": 40, "research": 30},
                "interventions": {"lockdown_level": 0.6, "travel_restricted": True}
            }
        ]
        
        # Create a mock attempt with results
        raw_metrics = {"metrics_history": metrics_history}
        
        results = SimulationResults(
            player_id="test_player",
            scenario_id="test_scenario",
            total_steps=365,
            final_score=0.85,
            population_survived=0.95,
            gdp_preserved=0.80,
            infection_control=0.90,
            resource_efficiency=0.75,
            time_to_containment=0.70,
            metadata={},
            raw_metrics=raw_metrics
        )
        
        # Create two mock attempts with different timestamps
        mock_attempt1 = MagicMock(spec=PlayerAttempt)
        mock_attempt1.id = "attempt1"
        mock_attempt1.player_id = "test_player"
        mock_attempt1.scenario_id = "test_scenario"
        mock_attempt1.timestamp = datetime(2023, 1, 1)
        mock_attempt1.is_official = True
        mock_attempt1.results = results
        
        mock_attempt2 = MagicMock(spec=PlayerAttempt)
        mock_attempt2.id = "attempt2"
        mock_attempt2.player_id = "test_player"
        mock_attempt2.scenario_id = "test_scenario"
        mock_attempt2.timestamp = datetime(2023, 1, 2)  # More recent
        mock_attempt2.is_official = True
        mock_attempt2.results = results
        
        # Set up mock to return the attempts
        self.competition_manager.competition_service.get_player_attempts.return_value = [
            mock_attempt1, mock_attempt2
        ]
    
    def test_get_detailed_metrics_latest(self):
        """Test getting detailed metrics from the latest attempt."""
        # Get metrics without specifying an attempt_id
        metrics = self.competition_manager.get_detailed_metrics()
        
        # Verify we got the correct number of metrics entries
        self.assertEqual(len(metrics), 2)
        
        # Check the metrics values
        first_metric = metrics[0]
        self.assertEqual(first_metric["step"], 0)
        self.assertEqual(first_metric["infected"], 100)
        self.assertAlmostEqual(first_metric["infection_rate"], 0.01)
        self.assertEqual(first_metric["gdp"], 950)
        self.assertEqual(first_metric["healthcare_resources"], 60)
        self.assertEqual(first_metric["lockdown_level"], 0.5)
        self.assertTrue(first_metric["travel_restricted"])
        
        # Check second step metrics
        second_metric = metrics[1]
        self.assertEqual(second_metric["step"], 1)
        self.assertEqual(second_metric["infected"], 150)
        self.assertEqual(second_metric["healthcare_resources"], 80)
    
    def test_get_detailed_metrics_specific_attempt(self):
        """Test getting detailed metrics from a specific attempt."""
        # Get metrics for a specific attempt
        metrics = self.competition_manager.get_detailed_metrics(attempt_id="attempt1")
        
        # Verify we got metrics
        self.assertEqual(len(metrics), 2)
        
        # Service should have been called
        self.competition_manager.competition_service.get_player_attempts.assert_called_once()
    
    def test_get_detailed_metrics_no_player(self):
        """Test getting metrics with no player set."""
        self.competition_manager.current_player_id = None
        
        with self.assertRaises(ValueError):
            self.competition_manager.get_detailed_metrics()
    
    def test_get_detailed_metrics_no_attempts(self):
        """Test getting metrics when no attempts are found."""
        # Set up mock to return empty list
        self.competition_manager.competition_service.get_player_attempts.return_value = []
        
        metrics = self.competition_manager.get_detailed_metrics()
        
        # Should return empty list
        self.assertEqual(metrics, [])
    
    def test_get_detailed_metrics_no_raw_metrics(self):
        """Test getting metrics when no raw metrics are available."""
        # Create a mock attempt with no raw_metrics
        mock_attempt = MagicMock(spec=PlayerAttempt)
        mock_attempt.id = "attempt1"
        mock_attempt.timestamp = datetime.now()  # Add timestamp to avoid error
        mock_attempt.results = MagicMock(spec=SimulationResults)
        
        # raw_metrics attribute is not set
        
        # Set up mock to return this attempt
        self.competition_manager.competition_service.get_player_attempts.return_value = [mock_attempt]
        
        metrics = self.competition_manager.get_detailed_metrics()
        
        # Should return empty list
        self.assertEqual(metrics, [])
    
    def test_get_detailed_metrics_no_metrics_history(self):
        """Test getting metrics when metrics_history is not in raw_metrics."""
        # Create a mock attempt with raw_metrics but no metrics_history
        mock_attempt = MagicMock(spec=PlayerAttempt)
        mock_attempt.id = "attempt1"
        mock_attempt.timestamp = datetime.now()  # Add timestamp to avoid error
        mock_attempt.results = MagicMock(spec=SimulationResults)
        mock_attempt.results.raw_metrics = {}  # Empty raw_metrics
        
        # Set up mock to return this attempt
        self.competition_manager.competition_service.get_player_attempts.return_value = [mock_attempt]
        
        metrics = self.competition_manager.get_detailed_metrics()
        
        # Should return empty list
        self.assertEqual(metrics, [])


if __name__ == "__main__":
    unittest.main() 