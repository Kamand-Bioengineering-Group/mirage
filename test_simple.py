import sys
import os
sys.path.append("..")
from src.competition.testing.enhanced_engine import EnhancedEngine
from src.competition.competition_manager import CompetitionManager

engine = EnhancedEngine()
cm = CompetitionManager(data_dir="practice_data", engine=engine)

# Setup player
player_id = cm.setup_player(name='Test Player')
cm.toggle_practice_mode(is_practice=True)
cm.set_scenario("standard")
setup = cm.setup_simulation()

def test_strategy(state):
    return {"lockdown_level": 0.5, "allocation": {"healthcare": 400, "economy": 300, "research": 300}}

results = cm.run_simulation(test_strategy, 365)
print("Final score:", results.get("final_score", 0)) 