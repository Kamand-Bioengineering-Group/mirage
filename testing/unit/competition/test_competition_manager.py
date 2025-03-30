import unittest
from unittest.mock import MagicMock, patch
import os
import sys
import tempfile
import shutil

from src.competition.competition_manager import CompetitionManager
from src.competition.core.models import Player, Scenario, SimulationResults, PlayerAttempt


class TestCompetitionManager(unittest.TestCase):
    """Test cases for the CompetitionManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test data
        self.test_data_dir = tempfile.mkdtemp()
        
        # Create a mock competition service
        self.mock_competition_service = MagicMock()
        
        # Create a mock simulation integration
        self.mock_simulation = MagicMock()
        
        # Create a competition manager with mocked dependencies
        self.competition_manager = CompetitionManager(data_dir=self.test_data_dir)
        self.competition_manager.competition_service = self.mock_competition_service
        self.competition_manager.simulation = self.mock_simulation
        
        # Set up current player and scenario
        self.competition_manager.current_player_id = "test_player"
        self.competition_manager.current_scenario_id = "test_scenario"
        
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.test_data_dir)
    
    def test_get_remaining_attempts_parameter_handling(self):
        """Test that get_remaining_attempts correctly handles the is_official parameter."""
        # Set up mock to return a list of attempts
        mock_attempts = [
            MagicMock(spec=PlayerAttempt),
            MagicMock(spec=PlayerAttempt)
        ]
        
        # Configure the mock to return these attempts
        self.mock_competition_service.get_player_attempts.return_value = mock_attempts
        
        # Call get_remaining_attempts
        remaining = self.competition_manager.get_remaining_attempts()
        
        # Verify get_player_attempts was called with correct parameters
        self.mock_competition_service.get_player_attempts.assert_called_once_with(
            player_id="test_player",
            scenario_id="test_scenario",
            is_official=True
        )
        
        # Verify remaining attempts calculation
        self.assertEqual(remaining, 1)  # 3 max - 2 used = 1 remaining
    
    def test_get_remaining_attempts_with_custom_parameters(self):
        """Test get_remaining_attempts with custom player and scenario IDs."""
        # Set up mock to return a list of attempts
        mock_attempts = [MagicMock(spec=PlayerAttempt)]
        
        # Configure the mock to return these attempts
        self.mock_competition_service.get_player_attempts.return_value = mock_attempts
        
        # Call get_remaining_attempts with custom parameters
        remaining = self.competition_manager.get_remaining_attempts(
            player_id="custom_player",
            scenario_id="custom_scenario"
        )
        
        # Verify get_player_attempts was called with correct parameters
        self.mock_competition_service.get_player_attempts.assert_called_once_with(
            player_id="custom_player",
            scenario_id="custom_scenario",
            is_official=True
        )
        
        # Verify remaining attempts calculation
        self.assertEqual(remaining, 2)  # 3 max - 1 used = 2 remaining
    
    def test_get_remaining_attempts_error_handling(self):
        """Test that get_remaining_attempts properly handles errors."""
        # Test when no player is set
        self.competition_manager.current_player_id = None
        
        with self.assertRaises(ValueError):
            self.competition_manager.get_remaining_attempts()
        
        # Reset player ID and test when no scenario is set
        self.competition_manager.current_player_id = "test_player"
        self.competition_manager.current_scenario_id = None
        
        with self.assertRaises(ValueError):
            self.competition_manager.get_remaining_attempts()
    
    def test_setup_simulation_error_handling(self):
        """Test that setup_simulation properly handles errors."""
        # Test case where scenario doesn't exist
        self.mock_competition_service.get_scenario.return_value = None
        
        with self.assertRaises(ValueError):
            self.competition_manager.setup_simulation()
        
        # Test case where scenario exists
        mock_scenario = MagicMock(spec=Scenario)
        mock_scenario.name = "Test Scenario"
        self.mock_competition_service.get_scenario.return_value = mock_scenario
        
        # This should not raise an error
        self.competition_manager.setup_simulation()
        
        # Verify configure_from_scenario was called
        self.mock_simulation.configure_from_scenario.assert_called_once_with(mock_scenario)


if __name__ == '__main__':
    unittest.main() 