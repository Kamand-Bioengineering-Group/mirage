import unittest
import os
import json
import tempfile
from unittest.mock import MagicMock
from datetime import datetime

from src.competition.competition_manager import CompetitionManager
from src.competition.core.models import PlayerAttempt, SimulationResults


class TestExportBestResult(unittest.TestCase):
    """Test the export_best_result method."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a competition manager with mocked dependencies
        self.competition_manager = CompetitionManager(data_dir="/tmp/test_data")
        self.competition_manager.competition_service = MagicMock()
        
        # Set current player and scenario
        self.competition_manager.current_player_id = "test_player"
        self.competition_manager.current_player_name = "Test Player"
        self.competition_manager.current_scenario_id = "test_scenario"
        
        # Create a mock attempt with results
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
            raw_metrics={"some_key": "some_value"}
        )
        
        mock_attempt = MagicMock(spec=PlayerAttempt)
        mock_attempt.player_id = "test_player"
        mock_attempt.scenario_id = "test_scenario"
        mock_attempt.timestamp = datetime.now()
        mock_attempt.is_official = True
        mock_attempt.results = results
        
        # Set up mock to return the attempt
        self.competition_manager.competition_service.get_best_attempt.return_value = mock_attempt
    
    def test_export_best_result(self):
        """Test exporting the best result to a file."""
        # Create temporary file for export
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
            export_path = temp_file.name
        
        try:
            # Export the result
            success = self.competition_manager.export_best_result(export_path)
            
            # Verify success
            self.assertTrue(success)
            
            # Verify file exists and contains expected data
            self.assertTrue(os.path.exists(export_path))
            
            # Read the file and check contents
            with open(export_path, 'r') as f:
                data = json.load(f)
            
            # Check key fields
            self.assertEqual(data["player_id"], "test_player")
            self.assertEqual(data["player_name"], "Test Player")
            self.assertEqual(data["scenario_id"], "test_scenario")
            self.assertEqual(data["score"], 0.85)
            self.assertEqual(data["components"]["population_survived"], 0.95)
            self.assertEqual(data["raw_metrics"]["some_key"], "some_value")
        
        finally:
            # Clean up the temporary file
            if os.path.exists(export_path):
                os.unlink(export_path)
    
    def test_export_best_result_no_player(self):
        """Test exporting with no player set."""
        self.competition_manager.current_player_id = None
        
        with self.assertRaises(ValueError):
            self.competition_manager.export_best_result("output.json")
    
    def test_export_best_result_no_scenario(self):
        """Test exporting with no scenario set."""
        self.competition_manager.current_scenario_id = None
        
        with self.assertRaises(ValueError):
            self.competition_manager.export_best_result("output.json")
    
    def test_export_best_result_no_attempts(self):
        """Test exporting when no attempts are found."""
        # Set up mock to return None (no attempts found)
        self.competition_manager.competition_service.get_best_attempt.return_value = None
        
        success = self.competition_manager.export_best_result("output.json")
        self.assertFalse(success)


if __name__ == "__main__":
    unittest.main() 