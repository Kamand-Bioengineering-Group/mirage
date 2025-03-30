"""
Visualization - Visualize results of strategy evaluations

This module provides tools for:
1. Visualizing time series data from simulations
2. Comparing strategy performances
3. Creating interactive visualizations for analysis
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union
import seaborn as sns
from scipy import stats
from pathlib import Path
import os

# Import from within the project
from .strategy_evaluator import StrategyEvaluator, StrategyEvaluation


class EvaluationVisualizer:
    """
    Visualizes results from strategy evaluations.
    
    This class provides methods for:
    1. Plotting time series data
    2. Creating comparative visualizations
    3. Generating summary charts
    """
    
    def __init__(self, evaluator: Optional[StrategyEvaluator] = None):
        """
        Initialize the visualizer.
        
        Args:
            evaluator: StrategyEvaluator to visualize results from
        """
        self.evaluator = evaluator
        
        # Set default style for plots
        sns.set_style("whitegrid")
        self.colors = sns.color_palette("viridis", 10)
        
    def set_evaluator(self, evaluator: StrategyEvaluator) -> None:
        """
        Set the strategy evaluator to use.
        
        Args:
            evaluator: The StrategyEvaluator to use
        """
        self.evaluator = evaluator
    
    def plot_metric_over_time(self, 
                             strategies: List[str],
                             metric: str,
                             title: Optional[str] = None,
                             figsize: Tuple[int, int] = (10, 6),
                             output_file: Optional[str] = None) -> None:
        """
        Plot a metric over time for multiple strategies.
        
        Args:
            strategies: List of strategy names to include
            metric: Name of the metric to plot
            title: Optional title for the plot
            figsize: Figure size as (width, height)
            output_file: Optional path to save the figure
        """
        if self.evaluator is None:
            raise ValueError("No evaluator set. Call set_evaluator() first.")
            
        if not strategies:
            raise ValueError("No strategies provided")
            
        # Create figure
        fig = plt.figure(figsize=figsize)
        
        # Plot each strategy
        for i, strategy in enumerate(strategies):
            if strategy not in self.evaluator.time_series_data:
                print(f"Warning: No time series data found for strategy '{strategy}'")
                continue
                
            # Get time series data
            time_series = self.evaluator.time_series_data[strategy]
            
            # Extract metric values
            steps = []
            values = []
            
            for step, data in enumerate(time_series):
                if metric in data:
                    steps.append(step)
                    values.append(data[metric])
                    
            if not steps:
                print(f"Warning: Metric '{metric}' not found in time series data for strategy '{strategy}'")
                continue
                
            # Plot the data
            plt.plot(steps, values, label=strategy, color=self.colors[i % len(self.colors)])
            
        # Add labels and title
        plt.xlabel("Simulation Step")
        plt.ylabel(metric.replace("_", " ").title())
        
        if title:
            plt.title(title)
        else:
            plt.title(f"{metric.replace('_', ' ').title()} Over Time")
            
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        
        # Save if output file provided
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches="tight")
            print(f"Figure saved to {output_file}")
        
        # Display the plot inline (return the figure rather than showing it)
        return fig
    
    def plot_strategy_comparison(self,
                               metrics: List[str] = None,
                               figsize: Tuple[int, int] = (12, 8),
                               output_file: Optional[str] = None) -> None:
        """
        Create a bar chart comparing strategies across multiple metrics.
        
        Args:
            metrics: List of metrics to include (default: basic metrics)
            figsize: Figure size as (width, height)
            output_file: Optional path to save the figure
        """
        if self.evaluator is None:
            raise ValueError("No evaluator set. Call set_evaluator() first.")
            
        if not self.evaluator.evaluations:
            raise ValueError("No evaluations available")
            
        # Default metrics if none provided
        if metrics is None:
            metrics = ["population_survived", "gdp_preserved", "infection_control", "resource_efficiency"]
            
        # Get evaluation data
        strategies = list(self.evaluator.evaluations.keys())
        
        # Create a DataFrame for plotting
        data = []
        for strategy_name in strategies:
            evaluation = self.evaluator.evaluations[strategy_name]
            for metric in metrics:
                if hasattr(evaluation, metric):
                    data.append({
                        "Strategy": strategy_name,
                        "Metric": metric.replace("_", " ").title(),
                        "Value": getattr(evaluation, metric)
                    })
                    
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Create figure
        fig = plt.figure(figsize=figsize)
        
        # Create grouped bar chart
        sns.barplot(x="Strategy", y="Value", hue="Metric", data=df)
        
        # Add labels and title
        plt.title("Strategy Comparison")
        plt.ylabel("Score")
        plt.ylim(0, 1)
        
        # Rotate x-axis labels if needed
        if len(strategies) > 4:
            plt.xticks(rotation=45)
            
        plt.legend(title="Metric")
        plt.grid(True)
        plt.tight_layout()
        
        # Save if output file provided
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches="tight")
            print(f"Figure saved to {output_file}")
            
        # Return the figure instead of calling show
        return fig
    
    def plot_score_breakdown(self,
                           strategy_name: str,
                           figsize: Tuple[int, int] = (10, 6),
                           output_file: Optional[str] = None) -> None:
        """
        Plot a breakdown of components contributing to a strategy's score.
        
        Args:
            strategy_name: Name of the strategy to analyze
            figsize: Figure size as (width, height)
            output_file: Optional path to save the figure
        """
        if self.evaluator is None:
            raise ValueError("No evaluator set. Call set_evaluator() first.")
            
        if strategy_name not in self.evaluator.evaluations:
            raise ValueError(f"Strategy '{strategy_name}' not found")
            
        # Get evaluation
        evaluation = self.evaluator.evaluations[strategy_name]
        
        # Components to include in breakdown
        components = [
            "population_survived",
            "gdp_preserved", 
            "infection_control",
            "resource_efficiency",
            "time_to_containment"
        ]
        
        # Add variant control if available
        if evaluation.variant_control is not None:
            components.append("variant_control")
            
        # Get values
        values = [getattr(evaluation, comp) for comp in components]
        labels = [comp.replace("_", " ").title() for comp in components]
        
        # Create figure
        fig = plt.figure(figsize=figsize)
        
        # Create horizontal bar chart
        bars = plt.barh(labels, values, color=self.colors[:len(components)])
        
        # Add values to bars
        for bar in bars:
            width = bar.get_width()
            plt.text(width + 0.01, bar.get_y() + bar.get_height()/2, 
                    f"{width:.2f}", va='center')
            
        # Add labels and title
        plt.title(f"Score Components for {strategy_name}")
        plt.xlabel("Score Contribution")
        plt.xlim(0, 1)
        plt.grid(True)
        
        plt.tight_layout()
        
        # Save if output file provided
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches="tight")
            print(f"Figure saved to {output_file}")
            
        # Return the figure instead of calling show
        return fig
    
    def plot_radar_chart(self,
                        strategies: List[str],
                        metrics: List[str] = None,
                        figsize: Tuple[int, int] = (10, 8),
                        output_file: Optional[str] = None) -> None:
        """
        Create a radar chart comparing strategies across multiple metrics.
        
        Args:
            strategies: List of strategy names to include
            metrics: List of metrics to include (default: basic metrics)
            figsize: Figure size as (width, height)
            output_file: Optional path to save the figure
        """
        if self.evaluator is None:
            raise ValueError("No evaluator set. Call set_evaluator() first.")
            
        if not strategies:
            raise ValueError("No strategies provided")
            
        # Default metrics if none provided
        if metrics is None:
            metrics = ["population_survived", "gdp_preserved", "infection_control", 
                      "resource_efficiency", "time_to_containment"]
            
        # Create figure
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, polar=True)
        
        # Number of metrics/angles
        N = len(metrics)
        
        # Create angles for radar chart
        angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
        angles += angles[:1]  # Close the loop
        
        # Define axis labels
        labels = [metric.replace("_", " ").title() for metric in metrics]
        
        # Plot each strategy
        for i, strategy in enumerate(strategies):
            if strategy not in self.evaluator.evaluations:
                print(f"Warning: No evaluation found for strategy '{strategy}'")
                continue
                
            # Get evaluation
            evaluation = self.evaluator.evaluations[strategy]
            
            # Get values for radar chart
            values = [getattr(evaluation, metric) for metric in metrics]
            values += values[:1]  # Close the loop
            
            # Plot the strategy
            ax.plot(angles, values, linewidth=2, label=strategy, color=self.colors[i % len(self.colors)])
            ax.fill(angles, values, alpha=0.1, color=self.colors[i % len(self.colors)])
            
        # Add axis labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels)
        
        # Set y axis limits
        ax.set_ylim(0, 1)
        
        # Add title and legend
        plt.title("Strategy Comparison Radar Chart")
        plt.legend(loc="upper right", bbox_to_anchor=(0.1, 0.1))
        
        # Save if output file provided
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches="tight")
            print(f"Figure saved to {output_file}")
            
        # Return the figure instead of calling show
        return fig
    
    def create_evaluation_dashboard(self, 
                                  strategies: List[str],
                                  output_dir: str) -> None:
        """
        Create a complete evaluation dashboard with multiple visualizations.
        
        Args:
            strategies: List of strategy names to include
            output_dir: Directory to save the dashboard files
        """
        if self.evaluator is None:
            raise ValueError("No evaluator set. Call set_evaluator() first.")
            
        if not strategies:
            raise ValueError("No strategies provided")
            
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate visualizations
        
        # 1. Strategy comparison bar chart
        comparison_path = os.path.join(output_dir, "strategy_comparison.png")
        self.plot_strategy_comparison(output_file=comparison_path)
        
        # 2. Radar chart
        radar_path = os.path.join(output_dir, "radar_chart.png")
        self.plot_radar_chart(strategies, output_file=radar_path)
        
        # 3. Time-series plots for key metrics
        metrics = ["infected", "dead", "gdp"]
        for metric in metrics:
            metric_path = os.path.join(output_dir, f"{metric}_over_time.png")
            self.plot_metric_over_time(strategies, metric, output_file=metric_path)
            
        # 4. Score breakdown for each strategy
        for strategy in strategies:
            breakdown_path = os.path.join(output_dir, f"{strategy}_breakdown.png")
            self.plot_score_breakdown(strategy, output_file=breakdown_path)
            
        # 5. Generate report
        report_path = os.path.join(output_dir, "evaluation_report.md")
        report = self.evaluator.create_strategy_report(output_file=report_path)
        
        print(f"Dashboard created in {output_dir}")
        print(f"To view the report, open {report_path}")
        
    def plot_infection_curves(self,
                             strategies: List[str],
                             figsize: Tuple[int, int] = (12, 6),
                             output_file: Optional[str] = None) -> None:
        """
        Plot infection curves for multiple strategies.
        
        Args:
            strategies: List of strategy names to include
            figsize: Figure size as (width, height)
            output_file: Optional path to save the figure
        """
        if self.evaluator is None:
            raise ValueError("No evaluator set. Call set_evaluator() first.")
            
        if not strategies:
            raise ValueError("No strategies provided")
            
        # Create figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # Plot infection curves
        for i, strategy in enumerate(strategies):
            if strategy not in self.evaluator.time_series_data:
                print(f"Warning: No time series data found for strategy '{strategy}'")
                continue
                
            # Get time series data
            time_series = self.evaluator.time_series_data[strategy]
            
            # Extract infected count and rates
            steps = []
            infected = []
            infection_rates = []
            
            for step, data in enumerate(time_series):
                if "infected" in data and "total_population" in data and data["total_population"] > 0:
                    steps.append(step)
                    infected.append(data["infected"])
                    infection_rates.append(data["infected"] / data["total_population"])
                    
            if not steps:
                print(f"Warning: Infection data not found for strategy '{strategy}'")
                continue
                
            # Plot absolute numbers
            ax1.plot(steps, infected, label=strategy, color=self.colors[i % len(self.colors)])
            
            # Plot infection rates
            ax2.plot(steps, infection_rates, label=strategy, color=self.colors[i % len(self.colors)])
            
        # Configure absolute numbers plot
        ax1.set_title("Infected Population")
        ax1.set_xlabel("Simulation Step")
        ax1.set_ylabel("Number of Infected")
        ax1.legend()
        ax1.grid(True)
        
        # Configure infection rate plot
        ax2.set_title("Infection Rate")
        ax2.set_xlabel("Simulation Step")
        ax2.set_ylabel("Proportion of Population Infected")
        ax2.set_ylim(0, 1)
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        
        # Save if output file provided
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches="tight")
            print(f"Figure saved to {output_file}")
            
        # Return the figure instead of calling show
        return fig
    
    def plot_economic_impact(self,
                           strategies: List[str],
                           figsize: Tuple[int, int] = (10, 6),
                           output_file: Optional[str] = None) -> None:
        """
        Plot economic impact over time for multiple strategies.
        
        Args:
            strategies: List of strategy names to include
            figsize: Figure size as (width, height)
            output_file: Optional path to save the figure
        """
        if self.evaluator is None:
            raise ValueError("No evaluator set. Call set_evaluator() first.")
            
        if not strategies:
            raise ValueError("No strategies provided")
            
        # Create figure
        plt.figure(figsize=figsize)
        
        # Plot GDP for each strategy
        for i, strategy in enumerate(strategies):
            if strategy not in self.evaluator.time_series_data:
                print(f"Warning: No time series data found for strategy '{strategy}'")
                continue
                
            # Get time series data
            time_series = self.evaluator.time_series_data[strategy]
            
            # Extract GDP values
            steps = []
            gdp_values = []
            gdp_ratios = []
            
            initial_gdp = None
            
            for step, data in enumerate(time_series):
                if "gdp" in data:
                    if initial_gdp is None and step == 0:
                        initial_gdp = data["gdp"]
                        
                    steps.append(step)
                    gdp_values.append(data["gdp"])
                    
                    if initial_gdp is not None and initial_gdp > 0:
                        gdp_ratios.append(data["gdp"] / initial_gdp)
                    else:
                        gdp_ratios.append(1.0)
                    
            if not steps:
                print(f"Warning: GDP data not found for strategy '{strategy}'")
                continue
                
            # Plot GDP ratio
            plt.plot(steps, gdp_ratios, label=strategy, color=self.colors[i % len(self.colors)])
            
        # Add labels and title
        plt.title("Economic Impact Over Time")
        plt.xlabel("Simulation Step")
        plt.ylabel("GDP Ratio (relative to initial)")
        plt.ylim(0, 1.1)  # Allow for slight growth
        
        plt.legend()
        plt.tight_layout()
        
        # Save if output file provided
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches="tight")
            print(f"Figure saved to {output_file}")
            
        plt.show() 