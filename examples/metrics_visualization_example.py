import sys
import os
import pandas as pd
import matplotlib.pyplot as plt

# Add project root to system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

# Import necessary modules
from src.competition import CompetitionManager
from src.competition.testing.engine_adapter import MockEngine
from src.visualization.metrics_visualization import (
    create_metrics_dataframe,
    plot_metrics_dashboard,
    visualize_metrics
)

def main():
    """Example of metrics visualization with error handling."""
    # Set up the competition system
    mock_engine = MockEngine()
    competition = CompetitionManager(data_dir="data", engine=mock_engine)
    player_id = competition.setup_player(name="test_player")
    competition.toggle_practice_mode(is_practice=True)
    
    # Set the scenario
    competition.set_scenario("standard")
    
    # Example strategy function
    def simple_strategy(engine):
        """Simple strategy for demonstration."""
        engine.set_lockdown_level(0.5)
        engine.allocate_resources('healthcare', 300)
        engine.allocate_resources('economic', 200)
        
        def step_callback(step, state):
            infection_rate = state.population.infected / state.population.total
            if infection_rate > 0.1:
                engine.set_lockdown_level(0.8)
                engine.allocate_resources('healthcare', 500)
            elif infection_rate < 0.01:
                engine.set_lockdown_level(0.2)
                engine.allocate_resources('economic', 400)
        
        engine.register_step_callback(step_callback)
    
    # Setup and run simulation
    competition.setup_simulation()
    sim_results = competition.run_simulation(
        steps=365,
        interventions=[simple_strategy]
    )
    
    print("Simulation completed!")
    
    # Get detailed metrics
    print("Getting detailed metrics...")
    metrics = competition.get_detailed_metrics()
    
    if metrics:
        print(f"Retrieved {len(metrics)} data points")
        
        # Method 1: Using the complete visualization utility
        print("\nMethod 1: Using visualize_metrics function")
        fig1 = visualize_metrics(metrics, save_path="metrics_visualization.png")
        plt.show()
        
        # Method 2: Creating DataFrame then visualizing
        print("\nMethod 2: Using create_metrics_dataframe and plot_metrics_dashboard")
        metrics_df = create_metrics_dataframe(metrics)
        
        # Check if infection_rate column exists
        if 'infection_rate' in metrics_df.columns:
            print("✓ infection_rate column exists in the DataFrame")
        else:
            print("✗ infection_rate column is missing - will be added with default values")
        
        # Print available columns
        print(f"\nAvailable columns: {', '.join(metrics_df.columns)}")
        
        # Plot the dashboard
        fig2 = plot_metrics_dashboard(metrics_df, save_path="metrics_dashboard.png")
        plt.show()
        
        # Method 3: Manual plotting with try-except for safety
        print("\nMethod 3: Manual plotting with error handling")
        try:
            plt.figure(figsize=(12, 6))
            
            # Try to plot infection rate
            try:
                plt.plot(metrics_df['step'], metrics_df['infection_rate'], 'r-', label='Infection Rate')
                print("✓ Successfully plotted infection_rate")
            except KeyError as e:
                print(f"✗ Error plotting infection_rate: {e}")
                # If infection_rate is missing, try to calculate it
                if 'infected' in metrics_df.columns and 'survived' in metrics_df.columns and 'dead' in metrics_df.columns:
                    total_pop = metrics_df['infected'] + metrics_df['survived'] + metrics_df['dead']
                    metrics_df['infection_rate'] = metrics_df['infected'] / total_pop.replace(0, 1)
                    plt.plot(metrics_df['step'], metrics_df['infection_rate'], 'r-', label='Infection Rate (calculated)')
                    print("✓ Calculated and plotted infection_rate")
            
            plt.title('Infection Rate Over Time')
            plt.xlabel('Days')
            plt.ylabel('Rate')
            plt.legend()
            plt.tight_layout()
            plt.savefig("manual_infection_plot.png")
            plt.show()
            
        except Exception as e:
            print(f"✗ Error in manual plotting: {e}")
    else:
        print("No metrics available. Make sure you've run a simulation first.")

if __name__ == "__main__":
    main() 