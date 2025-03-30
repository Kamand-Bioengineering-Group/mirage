#!/usr/bin/env python3
"""
Quick test script to verify the save_attempt method fixes.
"""
import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.competition.competition_manager import CompetitionManager


class TestSaveAttempt(unittest.TestCase):
    """Test the save_attempt method."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a competition manager with mocked dependencies
        self.competition_manager = CompetitionManager(data_dir="/tmp/test_data")
        self.competition_manager.competition_service = MagicMock()
        self.competition_manager.current_player_id = "test_player"
        self.competition_manager.current_scenario_id = "test_scenario"
        self.competition_manager.current_player_name = "Test Player"
        
        # Set up mock to return success
        self.competition_manager.competition_service.record_attempt.return_value = (True, None)
    
    def test_save_attempt_with_positional_results(self):
        """Test that save_attempt works with results as first positional argument."""
        # Create a results dictionary
        results = {
            "player_id": "test_player",
            "scenario_id": "test_scenario",
            "total_steps": 365,
            "final_score": 0.85,
            "population_survived": 0.95,
            "gdp_preserved": 0.80,
            "infection_control": 0.90,
            "resource_efficiency": 0.75,
            "time_to_containment": 0.70,
            "metadata": {},
            "raw_metrics": {}
        }
        
        # Call save_attempt with results as first argument
        success = self.competition_manager.save_attempt(results)
        
        # Verify record_attempt was called with correct parameters
        self.competition_manager.competition_service.record_attempt.assert_called_once()
        call_args = self.competition_manager.competition_service.record_attempt.call_args[1]
        
        self.assertEqual(call_args["player_id"], "test_player")
        self.assertEqual(call_args["scenario_id"], "test_scenario")
        self.assertTrue(call_args["is_official"] is not None)  # Don't care about exact value, just that it was passed
        
        # Verify success
        self.assertTrue(success)


if __name__ == "__main__":
    unittest.main() 