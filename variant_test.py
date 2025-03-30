#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Variant Test Script for Enhanced Engine

This script demonstrates the variant capabilities of the EnhancedEngine,
showcasing how different strategies can be used to combat disease variants.
"""

import os
import sys
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Import competition components
from src.competition.testing.enhanced_engine import EnhancedEngine

def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f"=== {title} ===")
    print("=" * 80 + "\n")

class VariantStrategy:
    """Base class for strategies that handle variants."""
    
    def __init__(self, name):
        self.name = name
        self.history = []
        self.target_variant = None
        
    def apply(self, engine):
        """Apply the strategy to the engine."""
        # Define what happens when this strategy is applied
        # Will be overridden by subclasses
        raise NotImplementedError("Subclasses must implement apply method")
    
    def reset(self):
        """Reset the strategy history."""
        self.history = []
        self.target_variant = None

class IgnoreVariantsStrategy(VariantStrategy):
    """A strategy that ignores variants and applies a standard approach."""
    
    def __init__(self):
        super().__init__("Ignore Variants")
    
    def apply(self, engine):
        """Apply standard balanced approach regardless of variants."""
        # Initial setup
        engine.set_lockdown_level(0.4)
        engine.allocate_resources('healthcare', 300)
        engine.allocate_resources('economic', 100)
        engine.allocate_resources('research', 200)
        engine.restrict_travel(False)
        
        # Define a callback for dynamic response
        def monitor_and_respond(step, state):
            # Access infection rate from state
            infection_rate = state.population.infected / state.population.total
            
            # Only respond to infection rate, ignoring variants
            if infection_rate > 0.1:
                engine.set_lockdown_level(0.6)
                engine.allocate_resources('healthcare', 50)
            elif infection_rate > 0.05:
                engine.set_lockdown_level(0.4)
                engine.allocate_resources('research', 50)
            else:
                engine.set_lockdown_level(0.2)
                engine.allocate_resources('economic', 50)
        
        # Register the callback
        engine.register_step_callback(monitor_and_respond)

class TargetDominantVariantStrategy(VariantStrategy):
    """A strategy that targets the most prevalent variant."""
    
    def __init__(self):
        super().__init__("Target Dominant Variant")
    
    def apply(self, engine):
        """Apply strategy that targets the dominant variant."""
        # Initial setup with research focus
        engine.set_lockdown_level(0.3)
        engine.allocate_resources('healthcare', 200)
        engine.allocate_resources('research', 400)
        engine.allocate_resources('economic', 100)
        engine.restrict_travel(True)
        
        # Store strategy instance for callback
        strategy = self
        
        # Define a callback for dynamic response
        def monitor_and_respond(step, state):
            # Get variant information
            variants = engine.get_variant_status()
            
            # Find the most prevalent variant
            if variants:
                dominant_variant = max(variants, key=lambda v: v['prevalence'])
                variant_name = dominant_variant['name']
                
                # Update the target variant
                if strategy.target_variant != variant_name:
                    strategy.target_variant = variant_name
                    print(f"Step {step}: Targeting {variant_name} variant")
                
                # Target research at this variant
                research_amount = 50 + (dominant_variant['prevalence'] * 100)
                engine.target_research(variant_name, research_amount)
                
                # Adjust lockdown based on variant transmissibility
                transmissibility = dominant_variant.get('r0_modifier', dominant_variant.get('transmissibility', 1.5))
                engine.set_lockdown_level(min(0.8, transmissibility * 0.4))
                
                # Adjust healthcare based on variant severity
                severity = dominant_variant.get('mortality_modifier', dominant_variant.get('severity', 1.3))
                engine.allocate_resources('healthcare', int(severity * 100))
            else:
                # No variants active yet - focus on research
                engine.allocate_resources('research', 100)
                engine.set_lockdown_level(0.2)
        
        # Register the callback
        engine.register_step_callback(monitor_and_respond)

class AdaptiveVariantStrategy(VariantStrategy):
    """
    A strategy that adapts to the current variant situation,
    changing lockdown levels based on variant transmissibility
    and allocating research to the most severe variant.
    """
    
    def __init__(self):
        super().__init__("Adaptive Variant Strategy")
    
    def apply(self, engine):
        """Apply adaptive strategy based on variant characteristics."""
        # Initial setup with balanced approach
        engine.set_lockdown_level(0.2)
        engine.allocate_resources('healthcare', 200)
        engine.allocate_resources('research', 500)
        engine.allocate_resources('economic', 100)
        engine.restrict_travel(False)
        
        # Store strategy instance for callback
        strategy = self
        
        # Define a callback for dynamic response
        def monitor_and_respond(step, state):
            # Get variant information
            variants = engine.get_variant_status()
            infection_rate = state.population.infected / state.population.total
            
            if not variants:
                # No variants active yet - standard approach
                if infection_rate > 0.1:
                    engine.set_lockdown_level(0.5)
                    engine.allocate_resources('healthcare', 100)
                else:
                    engine.set_lockdown_level(0.2)
                    engine.allocate_resources('research', 100)
                return
            
            # Find the most transmissible and most severe variants
            most_transmissible = max(variants, key=lambda v: v.get('r0_modifier', v.get('transmissibility', 1.0)))
            most_severe = max(variants, key=lambda v: v.get('mortality_modifier', v.get('severity', 1.0)))
            
            # Adapt lockdown level based on transmissibility
            transmissibility = most_transmissible.get('r0_modifier', most_transmissible.get('transmissibility', 1.5))
            lockdown_level = min(0.8, transmissibility * 0.5)
            engine.set_lockdown_level(lockdown_level)
            
            # Target research at the most severe variant
            target_name = most_severe['name']
            
            # Update the target variant
            if strategy.target_variant != target_name:
                strategy.target_variant = target_name
                print(f"Step {step}: Targeting most severe variant: {target_name}")
            
            # Adjust healthcare allocation based on severity
            severity = most_severe.get('mortality_modifier', most_severe.get('severity', 1.3))
            healthcare_allocation = min(500, int(severity * 300))
            engine.allocate_resources('healthcare', healthcare_allocation)
            
            # Target research at this variant
            engine.target_research(target_name, 100)
            
            # Restrict travel if highly transmissible variants are dominant
            engine.restrict_travel(transmissibility > 1.5)
            
            # Economic support increases as lockdown gets stricter
            engine.allocate_resources('economic', int(lockdown_level * 200))
        
        # Register the callback
        engine.register_step_callback(monitor_and_respond)

class PreemptiveVariantStrategy(VariantStrategy):
    """
    A strategy that preemptively invests in research and vaccines,
    anticipating variant emergence.
    """
    
    def __init__(self):
        super().__init__("Preemptive Variant Strategy")
    
    def apply(self, engine):
        """Apply preemptive strategy to prevent variant dominance."""
        # Initial setup with heavy research focus
        engine.set_lockdown_level(0.1)
        engine.allocate_resources('healthcare', 100)
        engine.allocate_resources('research', 700)
        engine.allocate_resources('economic', 100)
        engine.restrict_travel(False)
        
        # Store strategy instance for callback
        strategy = self
        
        # Define a callback for dynamic response
        def monitor_and_respond(step, state):
            # Get variant information
            variants = engine.get_variant_status()
            
            # Before day 20, focus on research and vaccines
            if step < 20:
                engine.set_lockdown_level(0.1)
                engine.allocate_resources('research', 150)
                return
            
            # After day 20, adapt based on variant situation
            if variants:
                # Choose the variant with highest immune escape to target
                immune_escape_variant = max(variants, key=lambda v: v.get('immune_escape', 0))
                variant_name = immune_escape_variant['name']
                
                # Update the target variant
                if strategy.target_variant != variant_name:
                    strategy.target_variant = variant_name
                    print(f"Step {step}: Targeting variant with highest immune escape: {variant_name}")
                
                # Target research at this variant
                engine.target_research(variant_name, 200)
                
                # Set lockdown based on variant prevalence
                highest_prevalence = max([v['prevalence'] for v in variants])
                engine.set_lockdown_level(min(0.7, highest_prevalence * 0.8))
                
                # Healthcare allocation based on severity of all variants
                avg_severity = 0
                for v in variants:
                    severity = 0
                    if 'mortality_modifier' in v:
                        severity = v['mortality_modifier']
                    elif 'severity' in v:
                        severity = v['severity']
                    else:
                        severity = 1.0
                    avg_severity += severity * v['prevalence']
                avg_severity /= len(variants)
                engine.allocate_resources('healthcare', int(avg_severity * 300))
                
                # Economic support to offset lockdown
                economic_support = int((engine.get_lockdown_level() ** 0.5) * 300)
                engine.allocate_resources('economic', economic_support)
            else:
                # No variants yet, continue preemptive approach
                engine.set_lockdown_level(0.2)
                engine.allocate_resources('research', 100)
                engine.allocate_resources('healthcare', 50)
                engine.allocate_resources('economic', 50)
        
        # Register the callback
        engine.register_step_callback(monitor_and_respond)

def run_simulation(engine, strategy, steps=100, seed=None):
    """Run a simulation with the given strategy."""
    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)
    
    # Reset the engine and strategy
    engine.reset()
    strategy.reset()
    
    # Apply the strategy to the engine
    strategy.apply(engine)
    
    # Setup data tracking
    days = []
    infected = []
    deaths = []
    gdp = []
    lockdown_levels = []
    variant_data = {
        'Alpha': [],
        'Beta': [],
        'Gamma': []
    }
    
    # Store initial state
    days.append(0)
    infected.append(engine.state.population.infected)
    deaths.append(engine.state.population.deaths)
    gdp.append(engine.state.economy.current_gdp / engine.state.economy.initial_gdp)
    lockdown_levels.append(engine.get_lockdown_level())
    
    # Track variant prevalence (initially zero)
    for variant_name in variant_data:
        variant_data[variant_name].append(0)
    
    # Run the simulation
    contained = False
    for day in range(1, steps + 1):
        # Run a single step
        engine.run(steps=1)
        
        # Track data
        days.append(day)
        infected.append(engine.state.population.infected)
        deaths.append(engine.state.population.deaths)
        gdp.append(engine.state.economy.current_gdp / engine.state.economy.initial_gdp)
        lockdown_levels.append(engine.get_lockdown_level())
        
        # Track variant prevalence
        variants = engine.get_variant_status()
        for variant_name in variant_data:
            found = False
            for v in variants:
                if v['name'] == variant_name:
                    variant_data[variant_name].append(v['prevalence'])
                    found = True
                    break
            if not found:
                variant_data[variant_name].append(0)
        
        # Check if the simulation is contained
        if engine.state.simulation.contained:
            contained = True
            break
    
    # Get final results - use 1 step to avoid division by zero
    results = engine.run(steps=1)
    
    # Add our tracked data
    results['days_simulated'] = len(days)
    results['peak_infected'] = max(infected)
    results['total_deaths'] = deaths[-1]
    results['final_gdp'] = gdp[-1]
    
    # Add time series data
    results['time_series'] = {
        'days': days,
        'infected': infected,
        'deaths': deaths,
        'gdp': gdp,
        'lockdown_levels': lockdown_levels,
        'variants': variant_data
    }
    
    # Store variant information at the end
    results['variants'] = engine.get_variant_status()
    
    return results

def plot_results(results_dict, title="Simulation Results"):
    """Plot the results of multiple strategies."""
    fig = plt.figure(figsize=(15, 20))
    
    # Create subplots
    ax1 = plt.subplot(4, 1, 1)  # Infections
    ax2 = plt.subplot(4, 1, 2)  # Deaths
    ax3 = plt.subplot(4, 1, 3)  # Variants
    ax4 = plt.subplot(4, 1, 4)  # Lockdown Levels
    
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
    variant_colors = {'Alpha': 'r', 'Beta': 'g', 'Gamma': 'b'}
    
    # Plot infections, deaths, and lockdown for each strategy
    for i, (strategy_name, results) in enumerate(results_dict.items()):
        time_series = results['time_series']
        color = colors[i % len(colors)]
        
        # Plot infections
        ax1.plot(time_series['days'], time_series['infected'], 
                label=strategy_name, color=color)
        
        # Plot deaths
        ax2.plot(time_series['days'], time_series['deaths'], 
                label=strategy_name, color=color)
        
        # Plot lockdown levels
        ax4.plot(time_series['days'], time_series['lockdown_levels'],
                label=strategy_name, color=color)
        
        # Plot variant prevalence for the first strategy only (to avoid clutter)
        if i == 0:
            for variant_name, prevalence in time_series['variants'].items():
                if any(prevalence):  # Only plot if the variant appears
                    ax3.plot(time_series['days'], prevalence, 
                            label=f"{variant_name} Variant", 
                            color=variant_colors[variant_name])
    
    # Set labels and legends
    ax1.set_title("Infections Over Time")
    ax1.set_xlabel("Day")
    ax1.set_ylabel("Infected Population")
    ax1.legend()
    ax1.grid(True)
    
    ax2.set_title("Deaths Over Time")
    ax2.set_xlabel("Day")
    ax2.set_ylabel("Total Deaths")
    ax2.legend()
    ax2.grid(True)
    
    ax3.set_title("Variant Prevalence Over Time")
    ax3.set_xlabel("Day")
    ax3.set_ylabel("Prevalence (%)")
    ax3.legend()
    ax3.grid(True)
    
    ax4.set_title("Lockdown Levels Over Time")
    ax4.set_xlabel("Day")
    ax4.set_ylabel("Lockdown Level (0-1)")
    ax4.legend()
    ax4.grid(True)
    
    plt.tight_layout()
    plt.suptitle(title, fontsize=16)
    plt.subplots_adjust(top=0.95)
    
    # Save the figure
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"variant_comparison_{timestamp}.png"
    plt.savefig(filename)
    print(f"Results saved to {filename}")
    
    return fig

def print_strategy_results(strategy_name, results):
    """Print the results for a strategy."""
    print(f"\nResults for {strategy_name}:")
    print(f"  Population Survived: {results['population_survived']:.4f}")
    print(f"  GDP Preserved: {results['gdp_preserved']:.4f}")
    print(f"  Infection Control: {results['infection_control']:.4f}")
    print(f"  Variant Control: {results.get('variant_control', 'N/A')}")
    print(f"  Final Score: {results['final_score']:.4f}")
    print(f"  Days Simulated: {results['days_simulated']}")
    print(f"  Peak Infected: {results['peak_infected']}")
    print(f"  Total Deaths: {results['total_deaths']}")
    
    # Print variant information at the end of simulation
    if 'variants' in results and results['variants']:
        print("\n  Final Variant Status:")
        for variant in results['variants']:
            print(f"    {variant['name']} Variant:")
            print(f"      Prevalence: {variant['prevalence']:.1f}%")
            # Check for keys in variant data structure
            if 'r0_modifier' in variant:
                print(f"      Transmissibility: {variant['r0_modifier']:.1f}x base")
            elif 'transmissibility' in variant:
                print(f"      Transmissibility: {variant['transmissibility']:.1f}x base")
                
            if 'mortality_modifier' in variant:
                print(f"      Severity: {variant['mortality_modifier']:.1f}x base")
            elif 'severity' in variant:
                print(f"      Severity: {variant['severity']:.1f}x base")
                
            if 'immune_escape' in variant:
                print(f"      Immune Escape: {variant['immune_escape']:.1f}%")

def compare_strategies():
    """Compare different variant-handling strategies."""
    print_section("Variant Strategy Comparison")
    
    # Create engine with higher variant emergence rate for testing
    engine = EnhancedEngine()
    
    # Increase the variant emergence rate for more interesting test
    engine.disease_params["variant_emergence_rate"] = 0.05
    engine.disease_params["variant_prevalence_increase"] = 0.1
    
    # Initialize the engine properly
    engine.initial_population = 1000000
    engine.reset()
    
    # Create strategies
    strategies = [
        IgnoreVariantsStrategy(),
        TargetDominantVariantStrategy(),
        AdaptiveVariantStrategy(),
        PreemptiveVariantStrategy()
    ]
    
    # Run simulations
    results_dict = {}
    for strategy in strategies:
        print(f"\nRunning simulation with {strategy.name} strategy...")
        results = run_simulation(engine, strategy, steps=120, seed=42)
        results_dict[strategy.name] = results
        print_strategy_results(strategy.name, results)
    
    # Create comparison table
    data = []
    for strategy_name, results in results_dict.items():
        data.append({
            'Strategy': strategy_name,
            'Population Survived': results['population_survived'],
            'GDP Preserved': results['gdp_preserved'],
            'Infection Control': results['infection_control'],
            'Variant Control': results.get('variant_control', 'N/A'),
            'Final Score': results['final_score'],
            'Days to Containment': results['days_simulated'],
            'Peak Infected': results['peak_infected'],
            'Total Deaths': results['total_deaths']
        })
    
    comparison_df = pd.DataFrame(data)
    comparison_df = comparison_df.set_index('Strategy')
    
    print("\nStrategy Comparison:")
    print(comparison_df)
    
    # Plot results
    plot_results(results_dict, "Variant Strategy Comparison")
    
    return comparison_df, results_dict

if __name__ == "__main__":
    print_section("Enhanced Engine Variant Test")
    compare_strategies() 