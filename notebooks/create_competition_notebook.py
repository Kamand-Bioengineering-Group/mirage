#!/usr/bin/env python3

"""
Script to generate the competition evaluation notebook.
This creates a Jupyter notebook for evaluating and submitting strategies
for the XPECTO epidemic competition.
"""

import json
import os
from pathlib import Path

# Define the notebook content as a dictionary
notebook = {
    "cells": [
        # Markdown cell: Introduction
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# XPECTO Epidemic 2.0 Competition Evaluation\n",
                "\n",
                "This notebook provides a standardized environment for evaluating your epidemic control strategy for the XPECTO competition. \n",
                "\n",
                "## Competition Rules and Requirements\n",
                "\n",
                "To ensure a fair competition, all submissions must adhere to the following requirements:\n",
                "\n",
                "1. **Player Registration**: You must register with your real name and email\n",
                "2. **Strategy Definition**: Your strategy must be defined as a function that accepts an engine parameter\n",
                "3. **Tampering Prevention**: All runs are logged with timestamps, environment information, and strategy code\n",
                "4. **Run Duration**: Official submissions must use the full 365-day simulation duration\n",
                "5. **Scenario Accuracy**: You must use the official competition scenarios without modifications\n",
                "6. **Attempt Limits**: You have a maximum of 3 official attempts per scenario\n",
                "\n",
                "## Submission Process\n",
                "\n",
                "After evaluating and testing your strategy, you should:\n",
                "\n",
                "1. Run a final official attempt with `is_practice=False`\n",
                "2. Save the generated submission file to include with your competition entry\n",
                "3. The submission file will include your strategy code, results, and verification data\n",
                "\n",
                "Let's begin by importing the necessary modules and setting up the evaluation environment."
            ]
        },
        
        # Code cell: Imports and Setup
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "%matplotlib inline\n",
                "import sys\n",
                "import os\n",
                "import json\n",
                "import inspect\n",
                "import platform\n",
                "import hashlib\n",
                "import uuid\n",
                "import pandas as pd\n",
                "import numpy as np\n",
                "import matplotlib.pyplot as plt\n",
                "import seaborn as sns\n",
                "from datetime import datetime\n",
                "from pathlib import Path\n",
                "from IPython.display import display, HTML\n",
                "\n",
                "# Add parent directory to path to allow importing from src\n",
                "sys.path.append('..')\n",
                "\n",
                "# Import competition modules\n",
                "from src.competition.testing.enhanced_engine import EnhancedEngine\n",
                "from src.competition.competition_manager import CompetitionManager\n",
                "from src.competition.evaluation.strategy_evaluator import StrategyEvaluator\n",
                "from src.competition.evaluation.visualization import EvaluationVisualizer\n",
                "\n",
                "# Setup paths\n",
                "SUBMISSION_DIR = Path('../notebooks/competition_submissions')\n",
                "SUBMISSION_DIR.mkdir(exist_ok=True, parents=True)\n",
                "\n",
                "# Print environment information for verification\n",
                "print(f\"Python Version: {platform.python_version()}\")\n",
                "print(f\"Operating System: {platform.system()} {platform.release()}\")\n",
                "print(f\"Evaluation Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\")"
            ]
        },
        
        # Markdown cell: Player Registration
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Player Registration\n",
                "\n",
                "Please enter your real name and email address. This information will be used to track your submissions and notify you of competition results."
            ]
        },
        
        # Code cell: Player Registration
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Player information - please use your real name and email\n",
                "PLAYER_NAME = \"Your Name\"\n",
                "PLAYER_EMAIL = \"your.email@example.com\"  # Optional but recommended\n",
                "\n",
                "# Initialize the competition system\n",
                "engine = EnhancedEngine()\n",
                "competition = CompetitionManager(data_dir=\"../practice_data\", engine=engine)\n",
                "\n",
                "# Register player\n",
                "player_id = competition.setup_player(name=PLAYER_NAME, email=PLAYER_EMAIL)\n",
                "print(f\"Player registered: {PLAYER_NAME} (ID: {player_id})\")\n",
                "\n",
                "# By default, we start in practice mode\n",
                "competition.toggle_practice_mode(is_practice=True)\n",
                "print(\"Practice mode enabled - attempts will not count toward your official score\")"
            ]
        },
        
        # Markdown cell: Available Scenarios
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Available Scenarios\n",
                "\n",
                "The competition includes several scenarios of varying difficulty. You can test your strategy against any of these scenarios. For official submissions, your strategy will be evaluated on all scenarios."
            ]
        },
        
        # Code cell: List and Select Scenarios
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# List available scenarios\n",
                "scenarios = competition.list_available_scenarios()\n",
                "\n",
                "# Display scenarios in a more readable format\n",
                "for i, scenario in enumerate(scenarios):\n",
                "    print(f\"Scenario {i+1}: {scenario['name']} (ID: {scenario['id']})\")\n",
                "    print(f\"  Difficulty: {scenario['difficulty']}\")\n",
                "    print(f\"  R0: {scenario['r0']}\")\n",
                "    print(f\"  Initial Resources: {scenario['initial_resources']}\")\n",
                "    print(\"\")\n",
                "\n",
                "# Select a scenario for evaluation\n",
                "SELECTED_SCENARIO = \"standard\"  # Change this to test different scenarios\n",
                "competition.set_scenario(SELECTED_SCENARIO)\n",
                "print(f\"Selected scenario: {SELECTED_SCENARIO}\")"
            ]
        },
        
        # Markdown cell: Define Strategy
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Define Your Strategy\n",
                "\n",
                "Now, define your epidemic control strategy function. This should be a function that takes an `engine` parameter and applies your strategy using the engine's intervention methods.\n",
                "\n",
                "Your strategy function can include:\n",
                "1. Initial resource allocation and lockdown settings\n",
                "2. Callback functions for adaptive response\n",
                "3. Logic based on the current state of the simulation\n",
                "\n",
                "The example below shows a basic strategy. Replace it with your own strategy implementation."
            ]
        },
        
        # Code cell: Strategy Definition
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "def my_strategy(engine):\n",
                "    \"\"\"\n",
                "    My competition strategy for epidemic control.\n",
                "    \n",
                "    Parameters:\n",
                "    -----------\n",
                "    engine : EnhancedEngine\n",
                "        The simulation engine instance\n",
                "    \"\"\"\n",
                "    # Initial settings\n",
                "    engine.set_lockdown_level(0.5)  # 50% lockdown\n",
                "    engine.allocate_resources('healthcare', 400)  # Allocate 400 resources to healthcare\n",
                "    engine.allocate_resources('economy', 300)  # Allocate 300 resources to economy support\n",
                "    engine.allocate_resources('research', 300)  # Allocate 300 resources to research\n",
                "    \n",
                "    # Define a callback function for adaptive response\n",
                "    def adaptive_response(step, state):\n",
                "        # Ensure we never divide by zero (total population might be zero in extreme cases)\n",
                "        total_population = max(1, state.population.total)\n",
                "        infection_rate = state.population.infected / total_population\n",
                "        \n",
                "        # Adjust lockdown based on infection rate\n",
                "        if infection_rate > 0.15:\n",
                "            # Severe outbreak - increase lockdown\n",
                "            engine.set_lockdown_level(0.8)\n",
                "            engine.allocate_resources('healthcare', 600)\n",
                "            engine.allocate_resources('economy', 200)\n",
                "            engine.allocate_resources('research', 200)\n",
                "        elif infection_rate > 0.05:\n",
                "            # Moderate outbreak - balanced approach\n",
                "            engine.set_lockdown_level(0.5)\n",
                "            engine.allocate_resources('healthcare', 400)\n",
                "            engine.allocate_resources('economy', 300)\n",
                "            engine.allocate_resources('research', 300)\n",
                "        else:\n",
                "            # Controlled situation - focus on economy\n",
                "            engine.set_lockdown_level(0.3)\n",
                "            engine.allocate_resources('healthcare', 200)\n",
                "            engine.allocate_resources('economy', 500)\n",
                "            engine.allocate_resources('research', 300)\n",
                "    \n",
                "    # Register the callback function for step-by-step adaptation\n",
                "    engine.register_step_callback(adaptive_response)\n",
                "\n",
                "# Get the source code of the strategy for logging\n",
                "strategy_source = inspect.getsource(my_strategy)\n",
                "print(\"Strategy defined.\")"
            ]
        },
        
        # Markdown cell: Test Run
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Test Run in Practice Mode\n",
                "\n",
                "Let's run a practice simulation with your strategy to see how it performs. This won't count toward your official attempts."
            ]
        },
        
        # Code cell: Run Practice Simulation
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Make sure we're in practice mode\n",
                "competition.toggle_practice_mode(is_practice=True)\n",
                "\n",
                "# Setup the simulation\n",
                "competition.setup_simulation()\n",
                "\n",
                "# Run the simulation with your strategy\n",
                "print(\"Running simulation in practice mode...\")\n",
                "practice_results = competition.run_simulation(\n",
                "    steps=365,  # Full year simulation\n",
                "    interventions=[my_strategy]\n",
                ")\n",
                "\n",
                "# Display results\n",
                "print(\"\\nSimulation Results:\")\n",
                "print(f\"Final Score: {practice_results.get('final_score', 0):.4f}\")\n",
                "print(f\"Population Survived: {practice_results.get('population_survived', 0):.1%}\")\n",
                "print(f\"GDP Preserved: {practice_results.get('gdp_preserved', 0):.1%}\")\n",
                "print(f\"Infection Control: {practice_results.get('infection_control', 0):.1%}\")\n",
                "print(f\"Resource Efficiency: {practice_results.get('resource_efficiency', 0):.1%}\")\n",
                "print(f\"Time to Containment: {practice_results.get('time_to_containment', 0)} days\")"
            ]
        },
        
        # Markdown cell: In-depth Analysis
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## In-depth Strategy Analysis\n",
                "\n",
                "Now let's use the evaluation module to get a more detailed analysis of your strategy's performance."
            ]
        },
        
        # Code cell: Evaluation
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Create strategy evaluator\n",
                "evaluator = StrategyEvaluator()\n",
                "visualizer = EvaluationVisualizer(evaluator)\n",
                "\n",
                "# Evaluate your strategy\n",
                "print(\"Performing detailed strategy analysis...\")\n",
                "evaluation = evaluator.evaluate_strategy(\n",
                "    name=\"My Strategy\",\n",
                "    strategy=my_strategy,\n",
                "    steps=365,  # Full year simulation\n",
                "    num_trials=1  # Just one run for this analysis\n",
                ")\n",
                "\n",
                "# Display evaluation results with grade\n",
                "print(f\"\\nStrategy Evaluation Results:\")\n",
                "print(f\"Score: {evaluation.score:.4f} (Grade: {evaluation.grade})\")\n",
                "print(f\"Population Survived: {evaluation.population_survived:.1%}\")\n",
                "print(f\"GDP Preserved: {evaluation.gdp_preserved:.1%}\")\n",
                "print(f\"Infection Control: {evaluation.infection_control:.1%}\")\n",
                "print(f\"Resource Efficiency: {evaluation.resource_efficiency:.1%}\")\n",
                "print(f\"Time to Containment: {evaluation.time_to_containment} days\")\n",
                "\n",
                "if evaluation.variant_control is not None:\n",
                "    print(f\"Variant Control: {evaluation.variant_control:.2f}\")\n",
                "\n",
                "# Generate a score breakdown visualization\n",
                "breakdown_fig = visualizer.plot_score_breakdown(\"My Strategy\")\n",
                "display(breakdown_fig)"
            ]
        },
        
        # Markdown cell: Metrics Visualization
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Performance Metrics Over Time\n",
                "\n",
                "Let's visualize how key metrics change over the course of the simulation.\n",
                "\n",
                "Note: If visualizations don't appear, make sure you've run the cell at the beginning of this notebook with `%matplotlib inline`. This ensures plots display properly in the notebook."
            ]
        },
        
        # Code cell: Visualization
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Plot infection curve\n",
                "fig1 = visualizer.plot_metric_over_time(\n",
                "    strategies=[\"My Strategy\"],\n",
                "    metric=\"infected\",\n",
                "    title=\"Infection Curve Over Time\"\n",
                ")\n",
                "display(fig1)  # Explicitly display the figure\n",
                "\n",
                "# Plot economic impact\n",
                "fig2 = visualizer.plot_metric_over_time(\n",
                "    strategies=[\"My Strategy\"],\n",
                "    metric=\"gdp\",\n",
                "    title=\"GDP Over Time\"\n",
                ")\n",
                "display(fig2)  # Explicitly display the figure"
            ]
        },
        
        # Markdown cell: Strategy Comparison
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Compare Multiple Strategies (Optional)\n",
                "\n",
                "If you want to compare different versions of your strategy, you can define additional strategies and evaluate them together."
            ]
        },
        
        # Code cell: Strategy Comparison
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Example alternative strategy for comparison\n",
                "def alternative_strategy(engine):\n",
                "    \"\"\"A different approach to compare against\"\"\"\n",
                "    # Higher initial lockdown, more focus on healthcare\n",
                "    engine.set_lockdown_level(0.7)\n",
                "    engine.allocate_resources('healthcare', 600)\n",
                "    engine.allocate_resources('economy', 200)\n",
                "    engine.allocate_resources('research', 200)\n",
                "    \n",
                "    def adaptive_response(step, state):\n",
                "        total_population = max(1, state.population.total)\n",
                "        infection_rate = state.population.infected / total_population\n",
                "        \n",
                "        if infection_rate < 0.03:\n",
                "            engine.set_lockdown_level(0.4)\n",
                "            engine.allocate_resources('economy', 400)\n",
                "            engine.allocate_resources('healthcare', 300)\n",
                "    \n",
                "    engine.register_step_callback(adaptive_response)\n",
                "\n",
                "# Compare strategies (optional)\n",
                "strategies = {\n",
                "    \"My Strategy\": my_strategy,\n",
                "    \"Alternative Strategy\": alternative_strategy\n",
                "}\n",
                "\n",
                "comparison_df = evaluator.compare_strategies(\n",
                "    strategies=strategies,\n",
                "    steps=365,\n",
                "    num_trials=1\n",
                ")\n",
                "\n",
                "print(\"Strategy Comparison:\")\n",
                "display(comparison_df)\n",
                "\n",
                "# Plot comparison\n",
                "comparison_fig = visualizer.plot_strategy_comparison()\n",
                "display(comparison_fig)\n",
                "\n",
                "# Create radar chart comparison\n",
                "radar_fig = visualizer.plot_radar_chart(list(strategies.keys()))\n",
                "display(radar_fig)"
            ]
        },
        
        # Markdown cell: Official Submission
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Creating Official Submission\n",
                "\n",
                "When you're satisfied with your strategy's performance, you can create an official submission. This will count toward your limit of 3 official attempts per scenario.\n",
                "\n",
                "**Important:** Check your remaining attempts before proceeding."
            ]
        },
        
        # Code cell: Check Remaining Attempts
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Check remaining official attempts\n",
                "remaining_attempts = competition.get_remaining_attempts()\n",
                "print(f\"Remaining official attempts for scenario '{SELECTED_SCENARIO}': {remaining_attempts}\")\n",
                "\n",
                "# Add a warning if this is the last attempt\n",
                "if remaining_attempts <= 1:\n",
                "    print(\"⚠️ WARNING: This is your last official attempt for this scenario!\")"
            ]
        },
        
        # Markdown cell: Official Submission Instructions
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "If you want to proceed with an official submission, run the next cell. This will:\n",
                "1. Switch to official mode (not practice)\n",
                "2. Run your strategy on the selected scenario\n",
                "3. Save all results and verification data to a submission file\n",
                "\n",
                "**Note:** Only run this when you're ready to submit your final strategy!"
            ]
        },
        
        # Code cell: Create Official Submission
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Function to create submission with verification data\n",
                "def create_official_submission(strategy_func, scenario_id):\n",
                "    # Collect environment data\n",
                "    environment_data = {\n",
                "        \"timestamp\": datetime.now().isoformat(),\n",
                "        \"python_version\": platform.python_version(),\n",
                "        \"os\": f\"{platform.system()} {platform.release()}\",\n",
                "        \"player_id\": competition.current_player_id,\n",
                "        \"player_name\": PLAYER_NAME,\n",
                "        \"scenario_id\": scenario_id,\n",
                "        \"submission_id\": str(uuid.uuid4())\n",
                "    }\n",
                "    \n",
                "    # Get strategy source code\n",
                "    strategy_source = inspect.getsource(strategy_func)\n",
                "    \n",
                "    # Create strategy hash for verification\n",
                "    strategy_hash = hashlib.sha256(strategy_source.encode()).hexdigest()\n",
                "    \n",
                "    # Toggle to official mode\n",
                "    competition.toggle_practice_mode(is_practice=False)\n",
                "    print(\"Switched to OFFICIAL mode - this attempt will count!\")\n",
                "    \n",
                "    # Setup and run simulation\n",
                "    competition.setup_simulation()\n",
                "    \n",
                "    # Record start time\n",
                "    start_time = datetime.now()\n",
                "    \n",
                "    # Run simulation with the strategy\n",
                "    print(f\"Running official simulation for scenario '{scenario_id}'...\")\n",
                "    results = competition.run_simulation(\n",
                "        steps=365,  # Full year is required for official submission\n",
                "        interventions=[strategy_func]\n",
                "    )\n",
                "    \n",
                "    # Record end time and duration\n",
                "    end_time = datetime.now()\n",
                "    duration = (end_time - start_time).total_seconds()\n",
                "    \n",
                "    # Create submission file\n",
                "    submission_data = {\n",
                "        \"environment\": environment_data,\n",
                "        \"strategy\": {\n",
                "            \"name\": strategy_func.__name__,\n",
                "            \"source\": strategy_source,\n",
                "            \"hash\": strategy_hash\n",
                "        },\n",
                "        \"execution\": {\n",
                "            \"start_time\": start_time.isoformat(),\n",
                "            \"end_time\": end_time.isoformat(),\n",
                "            \"duration_seconds\": duration\n",
                "        },\n",
                "        \"results\": results\n",
                "    }\n",
                "    \n",
                "    # Generate a unique filename\n",
                "    timestamp = datetime.now().strftime(\"%Y%m%d_%H%M%S\")\n",
                "    filename = f\"{PLAYER_NAME.replace(' ', '_')}_{scenario_id}_{timestamp}.json\"\n",
                "    filepath = SUBMISSION_DIR / filename\n",
                "    \n",
                "    # Save submission file\n",
                "    with open(filepath, 'w') as f:\n",
                "        json.dump(submission_data, f, indent=2)\n",
                "    \n",
                "    # Switch back to practice mode\n",
                "    competition.toggle_practice_mode(is_practice=True)\n",
                "    print(\"Switched back to practice mode\")\n",
                "    \n",
                "    return filepath, results\n",
                "\n",
                "# Uncomment and run the following line when you're ready to create an official submission\n",
                "# submission_file, official_results = create_official_submission(my_strategy, SELECTED_SCENARIO)"
            ]
        },
        
        # Markdown cell: Submission Verification
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Submission Verification\n",
                "\n",
                "After creating an official submission, you should verify that your submission file contains all the required information."
            ]
        },
        
        # Code cell: Verify Submission
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Function to verify a submission file\n",
                "def verify_submission_file(filepath):\n",
                "    try:\n",
                "        with open(filepath, 'r') as f:\n",
                "            submission = json.load(f)\n",
                "        \n",
                "        # Check essential components\n",
                "        required_sections = ['environment', 'strategy', 'execution', 'results']\n",
                "        missing_sections = [s for s in required_sections if s not in submission]\n",
                "        \n",
                "        if missing_sections:\n",
                "            print(f\"❌ ERROR: Missing required sections: {', '.join(missing_sections)}\")\n",
                "            return False\n",
                "        \n",
                "        # Verify strategy hash matches the source\n",
                "        strategy_source = submission['strategy']['source']\n",
                "        computed_hash = hashlib.sha256(strategy_source.encode()).hexdigest()\n",
                "        \n",
                "        if computed_hash != submission['strategy']['hash']:\n",
                "            print(\"❌ ERROR: Strategy hash doesn't match the source code - possible tampering\")\n",
                "            return False\n",
                "        \n",
                "        # Check for required results fields\n",
                "        required_results = ['final_score', 'population_survived', 'gdp_preserved']\n",
                "        missing_results = [r for r in required_results if r not in submission['results']]\n",
                "        \n",
                "        if missing_results:\n",
                "            print(f\"❌ ERROR: Missing required result fields: {', '.join(missing_results)}\")\n",
                "            return False\n",
                "        \n",
                "        # All checks passed\n",
                "        print(\"✅ Submission file successfully verified!\")\n",
                "        print(f\"📊 Final Score: {submission['results']['final_score']:.4f}\")\n",
                "        print(f\"👨‍👩‍👧‍👦 Population Survived: {submission['results']['population_survived']:.1%}\")\n",
                "        print(f\"💰 GDP Preserved: {submission['results']['gdp_preserved']:.1%}\")\n",
                "        print(f\"🔬 Infection Control: {submission['results']['infection_control']:.1%}\")\n",
                "        print(f\"⏱️ Execution Duration: {submission['execution']['duration_seconds']:.2f} seconds\")\n",
                "        print(f\"⏰ Submission Timestamp: {submission['environment']['timestamp']}\")\n",
                "        \n",
                "        return True\n",
                "    except Exception as e:\n",
                "        print(f\"❌ ERROR: Failed to verify submission file: {e}\")\n",
                "        return False\n",
                "\n",
                "# Uncomment and run after creating a submission\n",
                "# is_valid = verify_submission_file(submission_file)"
            ]
        },
        
        # Markdown cell: Conclusion
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Competition Submission Instructions\n",
                "\n",
                "To officially submit your strategy to the competition:\n",
                "\n",
                "1. Create your official submission by running the `create_official_submission` function\n",
                "2. Verify your submission file is valid by running the `verify_submission_file` function\n",
                "3. Submit both your notebook file (`*.ipynb`) and the generated JSON submission file\n",
                "\n",
                "Remember that you have a maximum of 3 official attempts per scenario. Choose wisely when to make your official submissions.\n",
                "\n",
                "### Fairness and Anti-Tampering Measures\n",
                "\n",
                "Each submission includes the following verification data:\n",
                "\n",
                "- **Timestamps**: When the simulation was run\n",
                "- **Environment**: Python version and OS information\n",
                "- **Strategy Code**: Full source code of your strategy function\n",
                "- **Strategy Hash**: SHA-256 hash of your strategy code for integrity verification\n",
                "- **Player Information**: Your registered player ID and name\n",
                "- **Execution Metrics**: Start time, end time, and duration of the simulation\n",
                "- **Full Results**: All simulation results for verification\n",
                "\n",
                "Any attempts to manipulate these verification mechanisms will result in disqualification."
            ]
        }
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "codemirror_mode": {
                "name": "ipython",
                "version": 3
            },
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.10.12"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

# Save the notebook to a file
with open("competition_evaluation.ipynb", "w") as f:
    json.dump(notebook, f, indent=2)

print("Successfully created competition_evaluation.ipynb")
