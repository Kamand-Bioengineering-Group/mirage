import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def create_metrics_dataframe(metrics):
    """
    Create a metrics DataFrame from the detailed metrics list returned by get_detailed_metrics.
    Ensures all required columns exist by adding them with default values if missing.
    
    Args:
        metrics: List of dictionaries containing metrics at each time step
        
    Returns:
        pandas.DataFrame: DataFrame with all required metrics columns
    """
    if not metrics:
        return pd.DataFrame()
    
    # Create DataFrame from the metrics list
    metrics_df = pd.DataFrame(metrics)
    
    # Define required columns with default values
    required_columns = {
        'step': lambda: np.arange(len(metrics_df)) if 'step' not in metrics_df else None,
        'infected': 0,
        'infection_rate': 0,
        'dead': 0,
        'survived': 0,
        'gdp': 0,
        'gdp_ratio': 0,
        'healthcare_resources': 0,
        'economic_resources': 0,
        'research_resources': 0,
        'lockdown_level': 0
    }
    
    # Add any missing columns with default values
    for column, default in required_columns.items():
        if column not in metrics_df:
            if callable(default):
                value = default()
                if value is not None:
                    metrics_df[column] = value
            else:
                metrics_df[column] = default
    
    # Calculate infection_rate if missing but infected and total population are available
    if 'infection_rate' not in metrics_df.columns:
        if 'infected' in metrics_df and 'survived' in metrics_df and 'dead' in metrics_df:
            total_population = metrics_df['survived'] + metrics_df['dead'] + metrics_df['infected']
            metrics_df['infection_rate'] = metrics_df['infected'] / total_population.replace(0, 1)  # Avoid div by zero
        else:
            metrics_df['infection_rate'] = 0  # Ensure column exists with default value
    return metrics_df

def plot_metrics_dashboard(metrics_df, figsize=(14, 8), save_path=None):
    """
    Create a dashboard of key metrics plots: infection rate, GDP, resource allocation, etc.
    Handles missing columns gracefully.
    
    Args:
        metrics_df: DataFrame containing metrics data
        figsize: Figure size tuple (width, height)
        save_path: Optional path to save the figure
        
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    if metrics_df.empty:
        print("No metrics data available for visualization")
        return None
    
    fig = plt.figure(figsize=figsize)
    
    # Plot infection rate over time
    plt.subplot(2, 2, 1)
    try:
        if 'infection_rate' in metrics_df.columns:
            plt.plot(metrics_df['step'], metrics_df['infection_rate'], 'r-', linewidth=2)
            plt.title('Infection Rate Over Time', fontsize=14)
            plt.xlabel('Days', fontsize=12)
            plt.ylabel('Infection Rate', fontsize=12)
            plt.grid(True, alpha=0.3)
        else:
            plt.text(0.5, 0.5, 'Infection rate data not available', 
                    horizontalalignment='center', verticalalignment='center')
            plt.title('Infection Rate (Missing)', fontsize=14)
    except Exception as e:
        plt.text(0.5, 0.5, f'Error plotting infection rate: {str(e)}', 
                horizontalalignment='center', verticalalignment='center')
    
    # Plot GDP over time
    plt.subplot(2, 2, 2)
    try:
        if 'gdp' in metrics_df.columns:
            plt.plot(metrics_df['step'], metrics_df['gdp'], 'g-', linewidth=2)
            plt.title('GDP Over Time', fontsize=14)
            plt.xlabel('Days', fontsize=12)
            plt.ylabel('GDP', fontsize=12)
            plt.grid(True, alpha=0.3)
        else:
            plt.text(0.5, 0.5, 'GDP data not available', 
                    horizontalalignment='center', verticalalignment='center')
            plt.title('GDP (Missing)', fontsize=14)
    except Exception as e:
        plt.text(0.5, 0.5, f'Error plotting GDP: {str(e)}', 
                horizontalalignment='center', verticalalignment='center')
    
    # Plot resource allocation over time
    plt.subplot(2, 2, 3)
    try:
        has_resource_data = ('healthcare_resources' in metrics_df.columns or 
                           'economic_resources' in metrics_df.columns or 
                           'research_resources' in metrics_df.columns)
        
        if has_resource_data:
            if 'healthcare_resources' in metrics_df.columns:
                plt.plot(metrics_df['step'], metrics_df['healthcare_resources'], 'b-', label='Healthcare')
            if 'economic_resources' in metrics_df.columns:
                plt.plot(metrics_df['step'], metrics_df['economic_resources'], 'y-', label='Economic')
            if 'research_resources' in metrics_df.columns:
                plt.plot(metrics_df['step'], metrics_df['research_resources'], 'c-', label='Research')
            
            plt.title('Resource Allocation Over Time', fontsize=14)
            plt.xlabel('Days', fontsize=12)
            plt.ylabel('Resources', fontsize=12)
            plt.legend()
            plt.grid(True, alpha=0.3)
        else:
            plt.text(0.5, 0.5, 'Resource allocation data not available', 
                    horizontalalignment='center', verticalalignment='center')
            plt.title('Resource Allocation (Missing)', fontsize=14)
    except Exception as e:
        plt.text(0.5, 0.5, f'Error plotting resources: {str(e)}', 
                horizontalalignment='center', verticalalignment='center')
    
    # Plot lockdown level over time
    plt.subplot(2, 2, 4)
    try:
        if 'lockdown_level' in metrics_df.columns:
            plt.plot(metrics_df['step'], metrics_df['lockdown_level'], 'k-', linewidth=2)
            plt.title('Lockdown Level Over Time', fontsize=14)
            plt.xlabel('Days', fontsize=12)
            plt.ylabel('Lockdown Level', fontsize=12)
            plt.grid(True, alpha=0.3)
        else:
            plt.text(0.5, 0.5, 'Lockdown level data not available', 
                    horizontalalignment='center', verticalalignment='center')
            plt.title('Lockdown Level (Missing)', fontsize=14)
    except Exception as e:
        plt.text(0.5, 0.5, f'Error plotting lockdown level: {str(e)}', 
                horizontalalignment='center', verticalalignment='center')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
    
    return fig

def visualize_metrics(metrics, save_path=None):
    """
    Convenience function to visualize metrics directly from get_detailed_metrics output.
    
    Args:
        metrics: List of dictionaries from get_detailed_metrics
        save_path: Optional path to save the figure
        
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    metrics_df = create_metrics_dataframe(metrics)
    return plot_metrics_dashboard(metrics_df, save_path=save_path) 