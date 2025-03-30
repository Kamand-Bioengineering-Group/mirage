import sys
import os
from pathlib import Path

# Add the parent directory to the Python path to find src modules
sys.path.append(str(Path(__file__).parent.parent.absolute()))

from src.competition.testing.enhanced_engine import EnhancedEngine
from src.competition.competition_manager import CompetitionManager

# Create an EnhancedEngine instance
engine = EnhancedEngine()

# Create a CompetitionManager with the EnhancedEngine
cm = CompetitionManager(data_dir='practice_data', engine=engine)

# Setup player
player_id = cm.setup_player(name='Test Player')
cm.toggle_practice_mode(is_practice=True)
cm.set_scenario('standard')
cm.setup_simulation()

# Define a test strategy function
def test_strategy(engine):
    engine.set_lockdown_level(0.5)
    engine.allocate_resources('healthcare', 400)
    engine.allocate_resources('economy', 300)
    engine.allocate_resources('research', 300)

# Run the simulation with the test strategy for 365 days
results = cm.run_simulation(steps=365, interventions=[test_strategy])

# Print the final score
print('Final score:', results.get('final_score', 0))
