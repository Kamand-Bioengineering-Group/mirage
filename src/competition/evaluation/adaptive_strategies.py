"""
Adaptive Strategy Evaluation - Tools for creating and evaluating adaptive strategies

This module provides:
1. Framework for creating adaptive strategies
2. Tools for evaluating how well strategies adapt to changing conditions
3. Comparison of adaptive vs. static strategies
"""

import random
import numpy as np
from typing import Dict, List, Any, Callable, Optional, Tuple, Union
from dataclasses import dataclass, field

# Import from within the project
from ..testing.enhanced_engine import EnhancedEngine
from .strategy_evaluator import StrategyEvaluator, StrategyEvaluation


@dataclass
class SimulationState:
    """Simplified representation of simulation state for strategy decision making."""
    step: int = 0
    infected: int = 0
    dead: int = 0
    total_population: int = 0
    gdp: float = 0.0
    initial_gdp: float = 0.0
    research_progress: float = 0.0
    
    @property
    def infection_rate(self) -> float:
        """Calculate infection rate."""
        if self.total_population <= 0:
            return 0.0
        return self.infected / self.total_population
    
    @property
    def mortality_rate(self) -> float:
        """Calculate mortality rate."""
        if self.total_population <= 0:
            return 0.0
        return self.dead / self.total_population
    
    @property
    def gdp_ratio(self) -> float:
        """Calculate GDP ratio."""
        if self.initial_gdp <= 0:
            return 0.0
        return self.gdp / self.initial_gdp


@dataclass
class StrategyAction:
    """Action to take in response to the current state."""
    lockdown_level: float = 0.0
    healthcare_allocation: float = 0.0
    economic_allocation: float = 0.0
    research_allocation: float = 0.0
    restrict_travel: bool = False


class AdaptiveStrategy:
    """
    Base class for adaptive strategies.
    
    An adaptive strategy adjusts interventions based on the current state of the simulation.
    """
    
    def __init__(self, name: str):
        """
        Initialize the adaptive strategy.
        
        Args:
            name: Name of the strategy
        """
        self.name = name
        self.state_history: List[SimulationState] = []
        self.action_history: List[StrategyAction] = []
    
    def decide_action(self, state: SimulationState) -> StrategyAction:
        """
        Decide what action to take based on the current state.
        
        This method should be overridden by subclasses.
        
        Args:
            state: Current state of the simulation
            
        Returns:
            Action to take
        """
        # Default implementation
        return StrategyAction(
            lockdown_level=0.5,
            healthcare_allocation=300,
            economic_allocation=300,
            research_allocation=300,
            restrict_travel=False
        )
    
    def apply(self, engine: EnhancedEngine) -> None:
        """
        Apply the strategy to the engine.
        
        This method is called once at the start of the simulation and sets up
        the callback for adaptive decision making.
        
        Args:
            engine: Simulation engine to apply the strategy to
        """
        # Initial action
        initial_state = SimulationState(
            step=0,
            infected=engine.state.population.infected,
            dead=engine.state.population.deaths,
            total_population=engine.state.population.total,
            gdp=engine.state.economy.current_gdp,
            initial_gdp=engine.state.economy.initial_gdp,
            research_progress=engine.state.research.progress
        )
        
        initial_action = self.decide_action(initial_state)
        self._apply_action(engine, initial_action)
        
        # Store initial state and action
        self.state_history.append(initial_state)
        self.action_history.append(initial_action)
        
        # Register callback for adaptive decision making
        def adapt_to_state(step: int, state):
            # Create simplified state representation
            current_state = SimulationState(
                step=step,
                infected=state.population.infected,
                dead=state.population.deaths,
                total_population=state.population.total,
                gdp=state.economy.current_gdp,
                initial_gdp=state.economy.initial_gdp,
                research_progress=state.research.progress
            )
            
            # Decide action based on current state
            action = self.decide_action(current_state)
            
            # Apply action
            self._apply_action(engine, action)
            
            # Store state and action
            self.state_history.append(current_state)
            self.action_history.append(action)
        
        # Register callback
        engine.register_step_callback(adapt_to_state)
    
    def _apply_action(self, engine: EnhancedEngine, action: StrategyAction) -> None:
        """
        Apply the action to the engine.
        
        Args:
            engine: Simulation engine
            action: Action to apply
        """
        engine.set_lockdown_level(action.lockdown_level)
        
        if action.healthcare_allocation > 0:
            engine.allocate_resources('healthcare', action.healthcare_allocation)
            
        if action.economic_allocation > 0:
            engine.allocate_resources('economic', action.economic_allocation)
            
        if action.research_allocation > 0:
            engine.allocate_resources('research', action.research_allocation)
            
        engine.restrict_travel(action.restrict_travel)


class PhaseBasedStrategy(AdaptiveStrategy):
    """
    A strategy that changes behavior based on distinct phases of the epidemic.
    
    Phases:
    1. Initial Containment: Focus on containment, testing, and preparation
    2. Surge Response: High lockdown, healthcare focus
    3. Maintenance: Balanced approach
    4. Recovery: Economic focus with monitoring
    5. End Game: Research focus with targeted containment
    """
    
    def __init__(self, name: str = "Phase-Based Strategy"):
        """Initialize the phase-based strategy."""
        super().__init__(name)
        self.current_phase = 1
        self.phase_transitions = {
            # Phase 1 -> 2: When infection rate exceeds 10%
            1: lambda state: state.infection_rate > 0.1,
            
            # Phase 2 -> 3: When infection rate starts dropping
            2: lambda state: (len(self.state_history) >= 2 and 
                            state.infection_rate < self.state_history[-2].infection_rate),
            
            # Phase 3 -> 4: When infection rate is below 5%
            3: lambda state: state.infection_rate < 0.05,
            
            # Phase 4 -> 5: When research progress exceeds 50%
            4: lambda state: state.research_progress > 0.5
        }
    
    def decide_action(self, state: SimulationState) -> StrategyAction:
        """
        Decide action based on the current phase and state.
        
        Args:
            state: Current state of the simulation
            
        Returns:
            Action to take
        """
        # Check for phase transition
        if self.current_phase in self.phase_transitions:
            transition_condition = self.phase_transitions[self.current_phase]
            if transition_condition(state):
                self.current_phase += 1
        
        # Phase 1: Initial Containment
        if self.current_phase == 1:
            return StrategyAction(
                lockdown_level=0.4,
                healthcare_allocation=400,
                economic_allocation=300,
                research_allocation=300,
                restrict_travel=True
            )
            
        # Phase 2: Surge Response
        elif self.current_phase == 2:
            return StrategyAction(
                lockdown_level=0.8,
                healthcare_allocation=600,
                economic_allocation=200,
                research_allocation=200,
                restrict_travel=True
            )
            
        # Phase 3: Maintenance
        elif self.current_phase == 3:
            return StrategyAction(
                lockdown_level=0.5,
                healthcare_allocation=400,
                economic_allocation=400,
                research_allocation=200,
                restrict_travel=state.infection_rate > 0.1
            )
            
        # Phase 4: Recovery
        elif self.current_phase == 4:
            return StrategyAction(
                lockdown_level=0.3,
                healthcare_allocation=300,
                economic_allocation=600,
                research_allocation=100,
                restrict_travel=False
            )
            
        # Phase 5: End Game
        else:
            return StrategyAction(
                lockdown_level=0.2,
                healthcare_allocation=200,
                economic_allocation=400,
                research_allocation=400,
                restrict_travel=False
            )


class ResponseCurveStrategy(AdaptiveStrategy):
    """
    A strategy that uses response curves to adjust interventions smoothly.
    
    This strategy adjusts lockdown level and resource allocation based on
    continuous response curves, rather than discrete thresholds.
    """
    
    def __init__(self, name: str = "Response Curve Strategy"):
        """Initialize the response curve strategy."""
        super().__init__(name)
    
    def decide_action(self, state: SimulationState) -> StrategyAction:
        """
        Decide action based on response curves.
        
        Args:
            state: Current state of the simulation
            
        Returns:
            Action to take
        """
        # Calculate lockdown level based on infection rate
        infection_response = self._sigmoid_response(state.infection_rate, midpoint=0.1, steepness=30)
        base_lockdown = infection_response * 0.8  # Max lockdown of 0.8
        
        # Adjust lockdown based on hospital capacity and economic factors
        mortality_factor = self._sigmoid_response(state.mortality_rate, midpoint=0.05, steepness=50)
        economic_factor = 1 - state.gdp_ratio  # Higher when economy is suffering
        
        # Balance health and economic concerns
        if economic_factor > 0.5 and state.infection_rate < 0.1:
            # Economy suffering but infections under control - reduce lockdown
            lockdown_level = max(0.1, base_lockdown - 0.2)
        elif mortality_factor > 0.7:
            # High mortality - increase lockdown
            lockdown_level = min(0.9, base_lockdown + 0.2)
        else:
            lockdown_level = base_lockdown
            
        # Adjust resource allocation based on needs
        healthcare_need = infection_response * 600  # More infections -> more healthcare
        economic_need = (1 - state.gdp_ratio) * 600  # Lower GDP -> more economic support
        research_need = 300  # Base research allocation
        
        # Boost research if well into the epidemic
        if state.step > 100:
            research_need += 200
            
        # Ensure total allocation is reasonable
        total_allocation = healthcare_need + economic_need + research_need
        if total_allocation > 1000:
            # Scale down proportionally
            scale_factor = 1000 / total_allocation
            healthcare_need *= scale_factor
            economic_need *= scale_factor
            research_need *= scale_factor
            
        return StrategyAction(
            lockdown_level=lockdown_level,
            healthcare_allocation=healthcare_need,
            economic_allocation=economic_need,
            research_allocation=research_need,
            restrict_travel=state.infection_rate > 0.15
        )
    
    def _sigmoid_response(self, x: float, midpoint: float, steepness: float) -> float:
        """
        Calculate sigmoid response curve.
        
        Args:
            x: Input value
            midpoint: Midpoint of the response curve
            steepness: Steepness of the response curve
            
        Returns:
            Response value between 0 and 1
        """
        return 1 / (1 + np.exp(-steepness * (x - midpoint)))


class RLInspiredStrategy(AdaptiveStrategy):
    """
    A strategy inspired by reinforcement learning principles.
    
    This strategy:
    1. Explores different actions early in the simulation
    2. Exploits successful actions as it learns what works
    3. Assigns values to actions based on observed outcomes
    """
    
    def __init__(self, name: str = "RL-Inspired Strategy"):
        """Initialize the RL-inspired strategy."""
        super().__init__(name)
        
        # Action-value estimates
        self.action_values = {}
        
        # Exploration parameter (decreases over time)
        self.initial_epsilon = 0.3
        
        # Learning rate
        self.alpha = 0.1
        
        # Discount factor
        self.gamma = 0.9
        
        # Action space (discrete for simplicity)
        self.lockdown_levels = [0.0, 0.3, 0.5, 0.7, 0.9]
        self.allocation_levels = [0, 200, 400, 600, 800]
        
        # Previous action and reward
        self.prev_action = None
        self.prev_state = None
    
    def decide_action(self, state: SimulationState) -> StrategyAction:
        """
        Decide action using epsilon-greedy strategy.
        
        Args:
            state: Current state of the simulation
            
        Returns:
            Action to take
        """
        # Decrease exploration over time
        epsilon = self.initial_epsilon * (1 - min(1.0, state.step / 200))
        
        # Calculate reward from previous action
        if self.prev_action is not None and self.prev_state is not None:
            reward = self._calculate_reward(self.prev_state, state)
            self._update_action_value(self.prev_state, self.prev_action, reward, state)
        
        # Discretize state for action-value lookup
        discrete_state = self._discretize_state(state)
        
        # Epsilon-greedy action selection
        if random.random() < epsilon:
            # Explore: select random action
            action = self._random_action()
        else:
            # Exploit: select best action for this state
            action = self._best_action(discrete_state)
        
        # Store state and action for next update
        self.prev_state = state
        self.prev_action = action
        
        return action
    
    def _discretize_state(self, state: SimulationState) -> tuple:
        """
        Discretize the state for action-value lookup.
        
        Args:
            state: Simulation state
            
        Returns:
            Tuple representing discretized state
        """
        # Discretize infection rate into bins
        if state.infection_rate < 0.05:
            infection_bin = 0
        elif state.infection_rate < 0.1:
            infection_bin = 1
        elif state.infection_rate < 0.2:
            infection_bin = 2
        else:
            infection_bin = 3
            
        # Discretize GDP ratio into bins
        if state.gdp_ratio < 0.3:
            gdp_bin = 0
        elif state.gdp_ratio < 0.6:
            gdp_bin = 1
        else:
            gdp_bin = 2
            
        # Discretize research progress
        research_bin = int(state.research_progress * 4)
        
        return (infection_bin, gdp_bin, research_bin)
    
    def _random_action(self) -> StrategyAction:
        """
        Generate a random action.
        
        Returns:
            Random action
        """
        return StrategyAction(
            lockdown_level=random.choice(self.lockdown_levels),
            healthcare_allocation=random.choice(self.allocation_levels),
            economic_allocation=random.choice(self.allocation_levels),
            research_allocation=random.choice(self.allocation_levels),
            restrict_travel=random.choice([True, False])
        )
    
    def _best_action(self, discrete_state: tuple) -> StrategyAction:
        """
        Select the best action for the given state.
        
        Args:
            discrete_state: Discretized state
            
        Returns:
            Best action
        """
        # If we haven't seen this state before, return a balanced action
        if discrete_state not in self.action_values or not self.action_values[discrete_state]:
            return StrategyAction(
                lockdown_level=0.5,
                healthcare_allocation=400,
                economic_allocation=300,
                research_allocation=300,
                restrict_travel=True
            )
            
        # Find the action with the highest value
        best_action_key = max(self.action_values[discrete_state], 
                           key=lambda k: self.action_values[discrete_state][k])
        
        # Convert action key back to StrategyAction
        lockdown, healthcare, economic, research, travel = best_action_key
        
        return StrategyAction(
            lockdown_level=lockdown,
            healthcare_allocation=healthcare,
            economic_allocation=economic,
            research_allocation=research,
            restrict_travel=travel
        )
    
    def _calculate_reward(self, prev_state: SimulationState, current_state: SimulationState) -> float:
        """
        Calculate reward based on state transition.
        
        Args:
            prev_state: Previous state
            current_state: Current state
            
        Returns:
            Reward value
        """
        # Components of the reward function
        health_reward = 0.0
        economic_reward = 0.0
        
        # Health component (reward for reducing infections, penalize deaths)
        if current_state.infection_rate < prev_state.infection_rate:
            health_reward += 1.0
        
        death_increase = current_state.mortality_rate - prev_state.mortality_rate
        health_reward -= death_increase * 10.0
        
        # Economic component (reward for maintaining GDP)
        gdp_change = current_state.gdp_ratio - prev_state.gdp_ratio
        economic_reward += gdp_change * 5.0
        
        # Research component (reward for research progress)
        research_reward = (current_state.research_progress - prev_state.research_progress) * 3.0
        
        # Combined reward
        reward = health_reward + economic_reward + research_reward
        
        return reward
    
    def _update_action_value(self, 
                           prev_state: SimulationState, 
                           action: StrategyAction, 
                           reward: float, 
                           current_state: SimulationState) -> None:
        """
        Update action-value estimate using Q-learning update rule.
        
        Args:
            prev_state: Previous state
            action: Action taken
            reward: Reward received
            current_state: Resulting state
        """
        # Discretize states
        prev_discrete = self._discretize_state(prev_state)
        current_discrete = self._discretize_state(current_state)
        
        # Convert action to hashable key
        action_key = (
            action.lockdown_level,
            action.healthcare_allocation,
            action.economic_allocation,
            action.research_allocation,
            action.restrict_travel
        )
        
        # Initialize action values if needed
        if prev_discrete not in self.action_values:
            self.action_values[prev_discrete] = {}
            
        if action_key not in self.action_values[prev_discrete]:
            self.action_values[prev_discrete][action_key] = 0.0
            
        # Get current value estimate
        current_value = self.action_values[prev_discrete][action_key]
        
        # Get maximum value in new state
        if current_discrete in self.action_values and self.action_values[current_discrete]:
            max_next_value = max(self.action_values[current_discrete].values())
        else:
            max_next_value = 0.0
            
        # Q-learning update rule
        new_value = current_value + self.alpha * (
            reward + self.gamma * max_next_value - current_value
        )
        
        # Update action value
        self.action_values[prev_discrete][action_key] = new_value


class AdaptiveStrategyEvaluator:
    """
    Evaluator for adaptive strategies.
    
    This class extends the basic StrategyEvaluator with methods specific to
    adaptive strategies.
    """
    
    def __init__(self, evaluator: StrategyEvaluator):
        """
        Initialize the adaptive strategy evaluator.
        
        Args:
            evaluator: Base strategy evaluator to use for evaluation
        """
        self.evaluator = evaluator
    
    def evaluate_adaptive_strategy(self, 
                                 strategy: AdaptiveStrategy, 
                                 steps: int = 365,
                                 num_trials: int = 1) -> StrategyEvaluation:
        """
        Evaluate an adaptive strategy.
        
        Args:
            strategy: Adaptive strategy to evaluate
            steps: Number of simulation steps
            num_trials: Number of trials to run
            
        Returns:
            Strategy evaluation
        """
        # Create wrapper function for the strategy
        def strategy_wrapper(engine):
            strategy.apply(engine)
            
        # Use the base evaluator to evaluate the strategy
        return self.evaluator.evaluate_strategy(
            strategy.name,
            strategy_wrapper,
            steps=steps,
            num_trials=num_trials
        )
    
    def compare_adaptive_strategies(self, 
                                  strategies: List[AdaptiveStrategy],
                                  steps: int = 365,
                                  num_trials: int = 1) -> None:
        """
        Compare multiple adaptive strategies.
        
        Args:
            strategies: List of adaptive strategies to compare
            steps: Number of simulation steps
            num_trials: Number of trials to run
        """
        # Create dictionary of strategy functions
        strategy_funcs = {}
        for strategy in strategies:
            def create_wrapper(strat):
                return lambda engine: strat.apply(engine)
                
            strategy_funcs[strategy.name] = create_wrapper(strategy)
            
        # Use the base evaluator to compare strategies
        return self.evaluator.compare_strategies(
            strategy_funcs,
            steps=steps,
            num_trials=num_trials
        )
    
    def analyze_strategy_adaptability(self, 
                                   strategy: AdaptiveStrategy,
                                   steps: int = 365) -> Dict[str, Any]:
        """
        Analyze how well a strategy adapts to changing conditions.
        
        Args:
            strategy: Adaptive strategy to analyze
            steps: Number of simulation steps
            
        Returns:
            Analysis results
        """
        # First, evaluate the strategy to populate state and action history
        self.evaluate_adaptive_strategy(strategy, steps=steps, num_trials=1)
        
        # Analyze adaptability
        if not strategy.state_history or not strategy.action_history:
            return {"adaptability_score": 0.0, "error": "No history available"}
            
        # Calculate change in actions
        action_changes = []
        for i in range(1, len(strategy.action_history)):
            prev_action = strategy.action_history[i-1]
            curr_action = strategy.action_history[i]
            
            # Calculate how much the action changed
            lockdown_change = abs(curr_action.lockdown_level - prev_action.lockdown_level)
            healthcare_change = abs(curr_action.healthcare_allocation - prev_action.healthcare_allocation)
            economic_change = abs(curr_action.economic_allocation - prev_action.economic_allocation)
            research_change = abs(curr_action.research_allocation - prev_action.research_allocation)
            travel_change = 1.0 if curr_action.restrict_travel != prev_action.restrict_travel else 0.0
            
            # Normalize and combine
            total_change = (
                lockdown_change +
                healthcare_change / 800 +
                economic_change / 800 +
                research_change / 800 +
                travel_change
            ) / 5
            
            action_changes.append(total_change)
            
        # Calculate how much the state changed
        state_changes = []
        for i in range(1, len(strategy.state_history)):
            prev_state = strategy.state_history[i-1]
            curr_state = strategy.state_history[i]
            
            # Calculate how much the state changed
            infection_change = abs(curr_state.infection_rate - prev_state.infection_rate)
            gdp_change = abs(curr_state.gdp_ratio - prev_state.gdp_ratio)
            
            # Normalize and combine
            total_change = (infection_change + gdp_change) / 2
            state_changes.append(total_change)
            
        # Calculate correlation between state changes and action changes
        if len(action_changes) > 1 and len(state_changes) > 1:
            # Correlation between state changes and next action changes
            correlation = np.corrcoef(state_changes[:-1], action_changes[1:])[0, 1]
        else:
            correlation = 0.0
            
        # Calculate adaptability metrics
        avg_action_change = sum(action_changes) / len(action_changes) if action_changes else 0
        action_change_variability = np.std(action_changes) if len(action_changes) > 1 else 0
        
        adaptability_score = (
            0.4 * abs(correlation) +  # How much actions respond to state changes
            0.4 * avg_action_change +  # How much the strategy changes actions
            0.2 * action_change_variability  # Variety of adaptations
        )
        
        return {
            "adaptability_score": adaptability_score,
            "state_action_correlation": correlation,
            "avg_action_change": avg_action_change,
            "action_change_variability": action_change_variability,
            "action_changes": action_changes,
            "state_changes": state_changes
        } 