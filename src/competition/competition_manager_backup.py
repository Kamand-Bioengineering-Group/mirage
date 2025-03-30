"""
Competition Manager - Main entry point for the competition system.
This class integrates all components and provides a unified interface.
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Tuple
from IPython.display import display, HTML
import pandas as pd

from .core.models import Player, PlayerAttempt, Scenario, SimulationResults
from .data.storage import StorageProvider, LocalStorageProvider
from .services.competition_service import CompetitionService
from .services.simulation_integration import SimulationIntegration


class CompetitionManager:
    """Main competition manager class."""
    
    def __init__(self, data_dir: str = "data", engine=None):
        """
        Initialize the competition manager.
        
        Args:
            data_dir: Directory for competition data
            engine: Optional epidemic engine instance
        """
        # Setup data directories
        self.data_dir = Path(data_dir)
        self._ensure_data_directory()
        
        # Initialize components
        self.storage = LocalStorageProvider(data_dir)
        self.competition_service = CompetitionService(self.storage)
        self.simulation = SimulationIntegration(engine)
        
        # Current player and scenario
        self.current_player_id = None
        self.current_player_name = None
        self.current_scenario_id = None
        self.is_practice_mode = True  # Default to practice mode
    
    def _ensure_data_directory(self):
        """Ensure data directories exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "players").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "attempts").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "scenarios").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "leaderboard").mkdir(parents=True, exist_ok=True)
    
    def setup_player(self, name: str, email: str = "") -> str:
        """
        Setup a player for the competition.
        
        Args:
            name: Player name
            email: Player email (optional)
            
        Returns:
            Player ID
        """
        player = self.competition_service.register_player(name, email)
        self.current_player_id = player.id
        self.current_player_name = player.name
        print(f"Player registered: {player.name} (ID: {player.id})")
        return player.id
    
    def set_player(self, player_id: str):
        """Set the current player."""
        player = self.competition_service.get_player(player_id)
        if player:
            self.current_player_id = player.id
            self.current_player_name = player.name
            print(f"Current player set to: {player.name}")
        else:
            print(f"Player with ID {player_id} not found")
    
    def list_available_scenarios(self) -> List[Dict[str, Any]]:
        """List available competition scenarios."""
        scenarios = self.competition_service.list_scenarios()
        
        # Display in a nice format
        if scenarios:
            scenario_data = []
            for s in scenarios:
                scenario_data.append({
                    "ID": s.id,
                    "Name": s.name,
                    "Difficulty": s.difficulty,
                    "R0": s.r0,
                    "Resources": s.initial_resources
                })
            
            df = pd.DataFrame(scenario_data)
            display(df)
            
        return [s.to_dict() for s in scenarios]
    
    def set_scenario(self, scenario_id: str):
        """Set the current scenario."""
        scenario = self.competition_service.get_scenario(scenario_id)
        if scenario:
            self.current_scenario_id = scenario.id
            print(f"Current scenario set to: {scenario.name} ({scenario.id})")
        else:
            print(f"Scenario with ID {scenario_id} not found")
    
    def toggle_practice_mode(self, is_practice: bool = None):
        """Toggle between practice and competition modes."""
        if is_practice is not None:
            self.is_practice_mode = is_practice
        else:
            self.is_practice_mode = not self.is_practice_mode
            
        mode = "Practice" if self.is_practice_mode else "Competition"
        print(f"Mode set to: {mode}")
    
    def setup_simulation(self, scenario_id: str = None):
        """
        Setup the simulation based on scenario.
        
        Args:
            scenario_id: Scenario ID (uses current if None)
        """
        # Use provided or current scenario
        scenario_id = scenario_id or self.current_scenario_id
        if not scenario_id:
            raise ValueError("No scenario specified or currently set")
            
        # Get scenario configuration
        scenario = self.competition_service.get_scenario(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")
            
        # Configure simulation
        self.simulation.configure_from_scenario(scenario)
        print(f"Simulation configured for scenario: {scenario.name}")
    
    def run_simulation(self, steps: int = 730, interventions: List[Callable] = None) -> Dict[str, Any]:
        """
        Run the simulation with current configuration.
        
        Args:
            steps: Number of steps to run
            interventions: List of intervention functions
            
        Returns:
            Dict with simulation results
        """
        if not self.current_scenario_id:
            raise ValueError("No scenario currently set. Call set_scenario() first.")
            
        if not self.current_player_id:
            raise ValueError("No player currently set. Call setup_player() or set_player() first.")
            
        # Run simulation
        results = self.simulation.run_simulation(steps, interventions)
        
        # Process results
        processed_results = self.competition_service.process_simulation_results(
            player_id=self.current_player_id,
            scenario_id=self.current_scenario_id,
            simulation_data=results
        )
        
        # Record attempt
        success, error = self.competition_service.record_attempt(
            player_id=self.current_player_id,
            player_name=self.current_player_name,
            scenario_id=self.current_scenario_id,
            results=processed_results,
            is_official=not self.is_practice_mode
        )
        
        if not success:
            print(f"Warning: Failed to record attempt - {error}")
        
        return processed_results.to_dict()
    
    def save_attempt(self, player_id: str = None, scenario_id: str = None, 
                    results: Dict[str, Any] = None, is_official: bool = None) -> bool:
        """
        Save a simulation attempt explicitly.
        
        Args:
            player_id: Player ID (uses current if None)
            scenario_id: Scenario ID (uses current if None)
            results: Simulation results (required)
            is_official: Whether this is an official attempt (uses current mode if None)
            
        Returns:
            Success status
        """
        player_id = player_id or self.current_player_id
        if not player_id:
            raise ValueError("No player specified or currently set")
            
        scenario_id = scenario_id or self.current_scenario_id
        if not scenario_id:
            raise ValueError("No scenario specified or currently set")
            
        if results is None:
            raise ValueError("No results provided")
            
        is_official = self.is_practice_mode if is_official is None else is_official
        
        # Convert results to SimulationResults if it's a dict
        from .core.models import SimulationResults
        if isinstance(results, dict):
            processed_results = SimulationResults(**results)
        else:
            processed_results = results
            
        # Record attempt
        success, error = self.competition_service.record_attempt(
            player_id=player_id,
            player_name=self.current_player_name,
            scenario_id=scenario_id,
            results=processed_results,
            is_official=not is_official  # invert is_practice_mode to get is_official
        )
        
        if not success:
            print(f"Warning: Failed to save attempt - {error}")
            
        return success
    
    def get_remaining_attempts(self, player_id: str = None, scenario_id: str = None) -> int:
        """
        Get the number of remaining official attempts for a player on a scenario.
        
        Args:
            player_id: Player ID (uses current if None)
            scenario_id: Scenario ID (uses current if None)
            
        Returns:
            Number of remaining attempts
        """
        player_id = player_id or self.current_player_id
        if not player_id:
            raise ValueError("No player specified or currently set")
            
        scenario_id = scenario_id or self.current_scenario_id
        if not scenario_id:
            raise ValueError("No scenario specified or currently set")
        
        # Get all attempts for this player and scenario
        attempts = self.competition_service.get_player_attempts(
            player_id=player_id, 
            scenario_id=scenario_id,
            is_official=True
        )
        
        # Maximum allowed attempts is 3 per scenario
        max_attempts = 3
        remaining = max_attempts - len(attempts)
        
        return max(0, remaining)
    
    def display_player_attempts(self, player_id: str = None, scenario_id: str = None):
        """
        Display a player's attempts.
        
        Args:
            player_id: Player ID (uses current if None)
            scenario_id: Scenario ID filter (optional)
        """
        player_id = player_id or self.current_player_id
        if not player_id:
            raise ValueError("No player specified or currently set")
            
        # Get attempts
        attempts = self.competition_service.get_player_attempts(
            player_id=player_id,
            scenario_id=scenario_id
        )
        
        if not attempts:
            print(f"No attempts found for player {player_id}")
            return
            
        # Display in a nice format
        attempt_data = []
        for a in attempts:
            if a.results:
                attempt_data.append({
                    "Timestamp": a.timestamp.strftime("%Y-%m-%d %H:%M"),
                    "Scenario": a.scenario_id,
                    "Official": "Yes" if a.is_official else "No",
                    "Score": a.results.final_score,
                    "Pop. Survived": f"{a.results.population_survived:.2f}",
                    "GDP": f"{a.results.gdp_preserved:.2f}",
                    "Infection Control": f"{a.results.infection_control:.2f}",
                    "Resources": f"{a.results.resource_efficiency:.2f}",
                    "Containment": f"{a.results.time_to_containment:.2f}"
                })
        
        if attempt_data:
            df = pd.DataFrame(attempt_data)
            display(df)
    
    def display_leaderboard(self):
        """Display the current competition leaderboard."""
        entries = self.competition_service.get_leaderboard()
        
        if not entries:
            print("No entries in the leaderboard yet")
            return
            
        # Display in a nice format
        leaderboard_data = []
        for e in entries:
            leaderboard_data.append({
                "Rank": e.rank,
                "Player": e.player_name,
                "Standard Score": f"{e.standard_score:.4f}",
                "Challenging Score": f"{e.challenging_score:.4f}",
                "Average Score": f"{e.average_score:.4f}"
            })
        
        if leaderboard_data:
            df = pd.DataFrame(leaderboard_data)
            display(df)
    
    def save_leaderboard(self, output_file: str = "leaderboard.html"):
        """
        Save the current leaderboard as HTML.
        
        Args:
            output_file: File to save HTML to
        """
        entries = self.competition_service.get_leaderboard()
        
        if not entries:
            print("No entries in the leaderboard to save")
            return
            
        # Create DataFrame
        leaderboard_data = []
        for e in entries:
            leaderboard_data.append({
                "Rank": e.rank,
                "Player": e.player_name,
                "Standard Score": f"{e.standard_score:.4f}",
                "Challenging Score": f"{e.challenging_score:.4f}",
                "Average Score": f"{e.average_score:.4f}"
            })
        
        if leaderboard_data:
            df = pd.DataFrame(leaderboard_data)
            
            # Generate HTML
            html = """
            <html>
            <head>
                <title>XPECTO Epidemic 2.0 Competition Leaderboard</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    h1 { color: #333366; }
                    table { border-collapse: collapse; width: 100%; }
                    th, td { border: 1px solid #dddddd; text-align: left; padding: 8px; }
                    tr:nth-child(even) { background-color: #f2f2f2; }
                    th { background-color: #333366; color: white; }
                    .medal-1 { background-color: gold; }
                    .medal-2 { background-color: silver; }
                    .medal-3 { background-color: #cd7f32; }
                </style>
            </head>
            <body>
                <h1>XPECTO Epidemic 2.0 Competition Leaderboard</h1>
            """
            
            # Add timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            html += f"<p>Generated on: {timestamp}</p>"
            
            # Convert DataFrame to HTML table with special formatting for top 3
            table_html = df.to_html(index=False)
            for i in range(1, min(4, len(df) + 1)):
                table_html = table_html.replace(f'<td>{i}</td>', f'<td class="medal-{i}">{i}</td>')
                
            html += table_html
            html += """
            </body>
            </html>
            """
            
            # Save to file
            with open(output_file, "w") as f:
                f.write(html)
                
            print(f"Leaderboard saved to {output_file}")
    
    def submit_strategy_document(self, player_id: str = None, strategy_doc: str = None, 
                               file_path: str = None) -> bool:
        """
        Submit a player's strategy document.
        
        Args:
            player_id: Player ID (uses current if None)
            strategy_doc: Strategy document text
            file_path: Path to text file containing strategy document
            
        Returns:
            Success status
        """
        player_id = player_id or self.current_player_id
        if not player_id:
            raise ValueError("No player specified or currently set")
            
        # Get strategy text
        if strategy_doc is None and file_path:
            try:
                with open(file_path, 'r') as f:
                    strategy_doc = f.read()
            except Exception as e:
                print(f"Error reading strategy file: {e}")
                return False
                
        if not strategy_doc:
            raise ValueError("No strategy document provided")
            
        # Update player's strategy
        return self.competition_service.update_player_strategy(player_id, strategy_doc)
    
    def display_scenario_details(self, scenario_id: str = None):
        """
        Display detailed information about a scenario.
        
        Args:
            scenario_id: Scenario ID (uses current if None)
        """
        scenario_id = scenario_id or self.current_scenario_id
        if not scenario_id:
            raise ValueError("No scenario specified or currently set")
            
        # Get scenario
        scenario = self.competition_service.get_scenario(scenario_id)
        if not scenario:
            print(f"Scenario {scenario_id} not found")
            return
            
        # Display details
        html = f"""
        <h2>{scenario.name}</h2>
        <p><em>{scenario.description}</em></p>
        <h3>Key Parameters:</h3>
        <ul>
            <li><strong>R0:</strong> {scenario.r0}</li>
            <li><strong>Initial Resources:</strong> {scenario.initial_resources}</li>
            <li><strong>Difficulty:</strong> {scenario.difficulty}</li>
        </ul>
        
        <h3>Initial Infections:</h3>
        <ul>
        """
        
        for location, count in scenario.initial_infections.items():
            html += f"<li><strong>{location}:</strong> {count} cases</li>"
            
        html += """
        </ul>
        
        <h3>Additional Parameters:</h3>
        <ul>
        """
        
        for param, value in scenario.parameters.items():
            html += f"<li><strong>{param}:</strong> {value}</li>"
            
        html += "</ul>"
        
        display(HTML(html))
    
    def display_score(self, results: Dict[str, Any] = None):
        """
        Display score breakdown.
        
        Args:
            results: Results dictionary (uses last run if None)
        """
        if not results and hasattr(self.simulation, 'last_results'):
            results = self.simulation.last_results
            
        if not results:
            print("No results available to display")
            return
            
        # Create score breakdown
        html = """
        <h2>Competition Score Breakdown</h2>
        <table style="width:100%; border-collapse:collapse;">
            <tr style="background-color:#333366; color:white;">
                <th>Component</th>
                <th>Value</th>
                <th>Weight</th>
                <th>Contribution</th>
            </tr>
        """
        
        # Components
        components = [
            {"name": "Population Survived", "score": results.get("population_survived", 0), "weight": 0.30},
            {"name": "GDP Preserved", "score": results.get("gdp_preserved", 0), "weight": 0.20},
            {"name": "Infection Control", "score": results.get("infection_control", 0), "weight": 0.20},
            {"name": "Resource Efficiency", "score": results.get("resource_efficiency", 0), "weight": 0.15},
            {"name": "Time to Containment", "score": results.get("time_to_containment", 0), "weight": 0.15}
        ]
        
        # Add rows
        total_score = 0
        for comp in components:
            score = comp["score"]
            weight = comp["weight"]
            contribution = score * weight
            total_score += contribution
            
            html += f"""
            <tr>
                <td><strong>{comp["name"]}</strong></td>
                <td>{score:.4f}</td>
                <td>{weight:.2f}</td>
                <td>{contribution:.4f}</td>
            </tr>
            """
            
        # Add total
        html += f"""
        <tr style="background-color:#f2f2f2; font-weight:bold;">
            <td>Final Score</td>
            <td colspan="2"></td>
            <td>{total_score:.4f}</td>
        </tr>
        </table>
        """
        
        display(HTML(html))
    
    def get_player_id(self) -> str:
        """Get the current player ID."""
        return self.current_player_id
    
    def get_scenario_id(self) -> str:
        """Get the current scenario ID."""
        return self.current_scenario_id 