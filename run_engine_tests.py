#!/usr/bin/env python3

"""
Engine Test Runner

This script runs all tests for the different epidemic simulation engines:
1. Basic strategy tests for MockEngine
2. Enhanced Engine vs MockEngine comparison
3. Integration tests for the Enhanced Engine

Usage:
    python run_engine_tests.py [--runs N] [--seed SEED] [--output-dir DIR]
"""

import os
import sys
import argparse
import subprocess
import time
from pathlib import Path

def run_command(cmd, description):
    """Run a command and print its output."""
    print(f"\n{'=' * 80}")
    print(f"=== {description}")
    print(f"{'=' * 80}\n")
    
    print(f"Running: {' '.join(cmd)}\n")
    start_time = time.time()
    
    process = subprocess.Popen(
        cmd, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT, 
        text=True,
        bufsize=1
    )
    
    # Print output in real-time
    for line in iter(process.stdout.readline, ''):
        print(line, end='')
    
    process.stdout.close()
    return_code = process.wait()
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\nCommand completed in {duration:.2f} seconds with return code: {return_code}")
    return return_code == 0

def main():
    """Run all engine tests."""
    parser = argparse.ArgumentParser(description='Run all engine tests')
    parser.add_argument('--runs', type=int, default=3, help='Number of runs per strategy (default: 3)')
    parser.add_argument('--seed', type=int, default=42, help='Random seed for reproducibility (default: 42)')
    parser.add_argument('--output-dir', type=str, default='test_results', help='Output directory for test results')
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    test_results = []
    
    # 1. Run basic MockEngine tests
    cmd = [
        sys.executable, 
        "tests/engine_strategy_test.py",
    ]
    success = run_command(cmd, "Basic MockEngine Strategy Tests")
    test_results.append(("Basic MockEngine Tests", success))
    
    # 2. Run enhanced engine comparison
    cmd = [
        sys.executable,
        "tests/enhanced_engine_test.py",
        f"--runs={args.runs}",
        f"--seed={args.seed}",
        f"--output-prefix={output_dir}/",
    ]
    success = run_command(cmd, "Enhanced Engine vs MockEngine Comparison")
    test_results.append(("Enhanced Engine Comparison", success))
    
    # 3. Run a simple integration test with the CompetitionManager
    test_script = """
import sys
import os
from pathlib import Path

# Add project root to path to ensure imports work
sys.path.append(str(Path(__file__).parent.parent))

from src.competition import CompetitionManager
from src.competition.testing.enhanced_engine import EnhancedEngine

# Create an EnhancedEngine instance
engine = EnhancedEngine(seed=42)

# Create a CompetitionManager with the EnhancedEngine
competition = CompetitionManager(data_dir="integration_test_data", engine=engine)

# Test setup_player
player_id = competition.setup_player(name="Integration Test Player")
print(f"Player registered: {player_id}")

# Toggle practice mode
competition.toggle_practice_mode(is_practice=True)
print("Practice mode enabled")

# Set scenario
competition.set_scenario("standard")
print("Scenario set to: standard")

# Set up simulation
competition.setup_simulation()
print("Simulation set up successfully")

# Define a simple intervention strategy
def test_strategy(engine):
    engine.set_lockdown_level(0.5)
    engine.allocate_resources('healthcare', 300)
    engine.allocate_resources('economic', 300)
    engine.allocate_resources('research', 200)
    engine.restrict_travel(True)
    
    def monitor_and_respond(step, state):
        infection_rate = state.population.infected / state.population.total
        if infection_rate > 0.1:
            engine.set_lockdown_level(0.7)
            engine.allocate_resources('healthcare', 50)
        else:
            engine.set_lockdown_level(0.3)
            engine.allocate_resources('economic', 50)
    
    engine.register_step_callback(monitor_and_respond)

# Run simulation
results = competition.run_simulation(steps=100, interventions=[test_strategy])
print("Simulation completed successfully")

# Display the results
competition.display_score(results)

print("\\nIntegration Test Passed: EnhancedEngine works with CompetitionManager")
"""
    
    # Write test script to a file
    integration_test_path = output_dir / "integration_test.py"
    with open(integration_test_path, "w") as f:
        f.write(test_script)
    
    # Run the integration test
    cmd = [sys.executable, str(integration_test_path)]
    success = run_command(cmd, "EnhancedEngine Integration Test")
    test_results.append(("Integration Test", success))
    
    # Print summary of all test results
    print("\n" + "=" * 80)
    print("=== TEST SUMMARY")
    print("=" * 80)
    
    all_passed = True
    for test_name, result in test_results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")
        all_passed = all_passed and result
    
    print("\nOverall Test Result:", "PASSED" if all_passed else "FAILED")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main()) 