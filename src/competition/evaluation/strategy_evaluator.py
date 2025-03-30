"""
Strategy Evaluator - Evaluates performance of intervention strategies

This module provides tools for:
1. Evaluating strategy performance
2. Comparing multiple strategies
3. Generating insights about strategy effectiveness
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Callable, Optional, Union
import matplotlib.pyplot as plt
from scipy import stats
import time
import json
from dataclasses import dataclass, field
from pathlib import Path
import random

# Import from within the project
from ..testing.enhanced_engine import EnhancedEngine


@dataclass
class StrategyEvaluation:
    """Result of evaluating a strategy."""
    
    name: str
    score: float
    population_survived: float
    gdp_preserved: float
    infection_control: float
    resource_efficiency: float
    time_to_containment: float
    variant_control: Optional[float] = None
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def grade(self) -> str:
        """Calculate letter grade based on score."""
        if self.score >= 0.85:
            return "A+"
        elif self.score >= 0.80:
            return "A"
        elif self.score >= 0.75:
            return "A-"
        elif self.score >= 0.70:
            return "B+"
        elif self.score >= 0.65:
            return "B"
        elif self.score >= 0.60:
            return "B-" 
        elif self.score >= 0.55:
            return "C+"
        elif self.score >= 0.50:
            return "C"
        elif self.score >= 0.45:
            return "C-"
        elif self.score >= 0.40:
            return "D+"
        elif self.score >= 0.35:
            return "D"
        else:
            return "F"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "score": self.score, 
            "grade": self.grade,
            "population_survived": self.population_survived,
            "gdp_preserved": self.gdp_preserved,
            "infection_control": self.infection_control,
            "resource_efficiency": self.resource_efficiency,
            "time_to_containment": self.time_to_containment,
            "variant_control": self.variant_control,
            "performance_metrics": self.performance_metrics,
            "raw_data": self.raw_data
        }
    
    @classmethod
    def from_results(cls, name: str, results: Dict[str, Any]) -> 'StrategyEvaluation':
        """Create an evaluation from simulation results."""
        return cls(
            name=name,
            score=results.get("final_score", 0),
            population_survived=results.get("population_survived", 0),
            gdp_preserved=results.get("gdp_preserved", 0),
            infection_control=results.get("infection_control", 0),
            resource_efficiency=results.get("resource_efficiency", 0),
            time_to_containment=results.get("time_to_containment", 0),
            variant_control=results.get("variant_control", None),
            performance_metrics=results.get("performance_metrics", {}),
            raw_data=results.get("raw_data", {})
        )


class StrategyEvaluator:
    """
    Evaluates and compares epidemic intervention strategies.
    
    This class provides tools for:
    1. Running simulations with different strategies
    2. Calculating performance metrics
    3. Comparing strategies
    4. Visualization of results
    """
    
    def __init__(self, engine: Optional[EnhancedEngine] = None, random_seed: Optional[int] = None):
        """
        Initialize the strategy evaluator.
        
        Args:
            engine: Optional simulation engine to use
            random_seed: Random seed for reproducible results
        """
        # Set random seed if provided
        if random_seed is not None:
            random.seed(random_seed)
            np.random.seed(random_seed)
        
        # Create engine if not provided
        self.engine = engine if engine is not None else EnhancedEngine(seed=random_seed)
        
        # Store evaluation results
        self.evaluations: Dict[str, StrategyEvaluation] = {}
        
        # Store time series data for visualization
        self.time_series_data: Dict[str, List[Dict[str, Any]]] = {}
        
    def evaluate_strategy(self, 
                         name: str, 
                         strategy: Callable[[EnhancedEngine], None], 
                         steps: int = 365,
                         num_trials: int = 1,
                         reset_between_trials: bool = True) -> StrategyEvaluation:
        """
        Evaluate a strategy by running simulations and calculating performance metrics.
        
        Args:
            name: Name of the strategy
            strategy: Function that applies the strategy to the engine
            steps: Number of simulation steps to run
            num_trials: Number of trials to run for statistical significance
            reset_between_trials: Whether to reset the engine between trials
            
        Returns:
            Evaluation results
        """
        if num_trials <= 0:
            raise ValueError("Number of trials must be positive")
            
        # Store trial results
        trial_results = []
        time_series = []
        
        # Run trials
        for trial in range(num_trials):
            # Reset engine if configured or first trial
            if reset_between_trials or trial == 0:
                self.engine.reset()
                
            # Run simulation with strategy
            results = self.engine.run(steps=steps, interventions=[strategy])
            
            # Collect results
            trial_results.append(results)
            
            # Create basic time series data if not provided by the engine
            if "metrics_history" not in results:
                # Generate minimal time series data from raw_data
                if "raw_data" in results:
                    basic_metrics = {
                        "step": steps,
                        "infected": results["raw_data"].get("infected", 0),
                        "dead": results["raw_data"].get("deaths", 0),
                        "total_population": results["raw_data"].get("total_population", 0),
                        "gdp": results["raw_data"].get("current_gdp", 0),
                        "initial_gdp": results["raw_data"].get("initial_gdp", 0)
                    }
                    
                    # Store as a single-step time series
                    time_series.append([basic_metrics])
            else:
                # Use provided metrics history
                time_series.append(results["metrics_history"])
        
        # Calculate average results
        avg_results = self._average_results(trial_results)
        
        # Record time series data
        if time_series:
            # Use the first trial's time series as representative
            self.time_series_data[name] = time_series[0]
        
        # Create and store evaluation
        evaluation = StrategyEvaluation.from_results(name, avg_results)
        self.evaluations[name] = evaluation
        
        return evaluation
    
    def _average_results(self, results_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate average results across multiple trials.
        
        Args:
            results_list: List of results dictionaries
            
        Returns:
            Averaged results
        """
        if not results_list:
            return {}
        
        # Create a new results dictionary
        avg_results = {}
        
        # Identify numeric fields to average
        numeric_keys = [
            "final_score", "raw_score", "normalized_score",
            "population_survived", "gdp_preserved", "infection_control",
            "resource_efficiency", "time_to_containment", "variant_control"
        ]
        
        # Calculate averages for numeric fields
        for key in numeric_keys:
            values = [r.get(key, 0) for r in results_list]
            avg_results[key] = sum(values) / len(values)
        
        # Use the last result's raw_data and other non-averaged fields
        last_result = results_list[-1]
        for key, value in last_result.items():
            if key not in avg_results and key not in ["metrics_history"]:
                avg_results[key] = value
        
        return avg_results
    
    def compare_strategies(self, 
                          strategies: Dict[str, Callable[[EnhancedEngine], None]],
                          steps: int = 365,
                          num_trials: int = 1) -> pd.DataFrame:
        """
        Compare multiple strategies and return results as a DataFrame.
        
        Args:
            strategies: Dictionary mapping strategy names to strategy functions
            steps: Number of simulation steps to run
            num_trials: Number of trials to run for each strategy
            
        Returns:
            DataFrame with strategy comparison results
        """
        # Evaluate each strategy
        for name, strategy in strategies.items():
            self.evaluate_strategy(name, strategy, steps, num_trials)
        
        # Compile results into a DataFrame
        comparison_data = []
        for name, evaluation in self.evaluations.items():
            comparison_data.append({
                "Strategy": name,
                "Score": evaluation.score,
                "Grade": evaluation.grade,
                "Population": f"{evaluation.population_survived:.1%}",
                "GDP": f"{evaluation.gdp_preserved:.1%}",
                "Infection Control": f"{evaluation.infection_control:.1%}",
                "Resource Efficiency": f"{evaluation.resource_efficiency:.1%}"
            })
        
        # Create and return DataFrame
        df = pd.DataFrame(comparison_data)
        if not df.empty:
            # Sort by score in descending order
            df = df.sort_values("Score", ascending=False)
        
        return df
    
    def create_strategy_report(self, output_file: Optional[str] = None) -> str:
        """
        Generate a detailed report of all evaluated strategies.
        
        Args:
            output_file: Optional path to save the report
            
        Returns:
            Report text
        """
        if not self.evaluations:
            return "No strategies have been evaluated yet."
        
        # Build report text
        report = []
        report.append("# Strategy Evaluation Report\n")
        
        # Summary table
        report.append("## Summary\n")
        comparison_df = self.compare_strategies({})  # Empty dict to use existing evaluations
        report.append(comparison_df.to_markdown(index=False))
        report.append("\n")
        
        # Individual strategy details
        report.append("## Detailed Analysis\n")
        for name, evaluation in self.evaluations.items():
            report.append(f"### {name}\n")
            report.append(f"- **Score**: {evaluation.score:.4f} (Grade: {evaluation.grade})")
            report.append(f"- **Population Survived**: {evaluation.population_survived:.1%}")
            report.append(f"- **GDP Preserved**: {evaluation.gdp_preserved:.1%}")
            report.append(f"- **Infection Control**: {evaluation.infection_control:.1%}")
            
            # Include variant information if available
            if evaluation.variant_control is not None:
                report.append(f"- **Variant Control**: {evaluation.variant_control:.2f}")
            
            # Performance insights
            metrics = evaluation.performance_metrics
            if metrics:
                report.append("\n**Performance Insights:**\n")
                if "multi_objective_score" in metrics:
                    report.append(f"- Multi-objective Balance: {metrics['multi_objective_score']:.3f}")
            
            report.append("\n")
        
        # Join the report into a single string
        report_text = "\n".join(report)
        
        # Save the report if a file path is provided
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
        
        return report_text
    
    def save_evaluations(self, output_file: str) -> bool:
        """
        Save all evaluations to a JSON file.
        
        Args:
            output_file: Path to save the evaluations
            
        Returns:
            Success status
        """
        try:
            # Convert evaluations to dictionary
            data = {name: eval.to_dict() for name, eval in self.evaluations.items()}
            
            # Save to file
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving evaluations: {e}")
            return False
    
    def load_evaluations(self, input_file: str) -> bool:
        """
        Load evaluations from a JSON file.
        
        Args:
            input_file: Path to load the evaluations from
            
        Returns:
            Success status
        """
        try:
            # Load from file
            with open(input_file, 'r') as f:
                data = json.load(f)
            
            # Convert to evaluations
            for name, eval_data in data.items():
                # Create evaluation object
                evaluation = StrategyEvaluation(
                    name=eval_data["name"],
                    score=eval_data["score"],
                    population_survived=eval_data["population_survived"],
                    gdp_preserved=eval_data["gdp_preserved"],
                    infection_control=eval_data["infection_control"],
                    resource_efficiency=eval_data["resource_efficiency"],
                    time_to_containment=eval_data["time_to_containment"],
                    variant_control=eval_data.get("variant_control"),
                    performance_metrics=eval_data.get("performance_metrics", {}),
                    raw_data=eval_data.get("raw_data", {})
                )
                
                # Store evaluation
                self.evaluations[name] = evaluation
            
            return True
        except Exception as e:
            print(f"Error loading evaluations: {e}")
            return False 