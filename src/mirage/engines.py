
class EngineV1:
    """Basic epidemic simulation engine for the XPECTO competition."""
    
    def __init__(self):
        self.lockdown_level = 0.0
        self.resources = {'healthcare': 0, 'economic': 0, 'testing': 0, 'research': 0}
        self.step_callbacks = []
        self.simulation_parameters = {'strategy_type': None, 'effectiveness': 0.5}
        
    def set_lockdown_level(self, level):
        """Set the global lockdown level (0.0 to 1.0)."""
        self.lockdown_level = max(0.0, min(1.0, level))
        
    def allocate_resources(self, resource_type, amount):
        """Allocate resources to a specific area."""
        if resource_type in self.resources:
            self.resources[resource_type] = amount
            
    def register_step_callback(self, callback):
        """Register a callback function to be called at each step."""
        self.step_callbacks.append(callback)
        
    def set_simulation_parameter(self, param_name, value):
        """Set custom simulation parameters to differentiate strategies."""
        self.simulation_parameters[param_name] = value
        
    def run_simulation(self, steps=365):
        """Run the simulation for a specified number of steps."""
        # Mock simulation state
        sim_state = SimulationState()
        
        # Apply effectiveness from strategy to results
        effectiveness = self.simulation_parameters.get('effectiveness', 0.5)
        strategy_type = self.simulation_parameters.get('strategy_type', 'basic')
        
        # Adjust results based on strategy type and effectiveness
        if strategy_type == 'basic':
            sim_state.population.survived = 0.993 
            sim_state.economy.gdp_preserved = 0.3 * effectiveness
            sim_state.infection_control = 0.8 * effectiveness
            sim_state.resource_efficiency = 0.6 * effectiveness
            sim_state.time_to_containment = 0.7 * effectiveness
            
        elif strategy_type == 'progressive':
            sim_state.population.survived = 0.995
            sim_state.economy.gdp_preserved = 0.4 * effectiveness
            sim_state.infection_control = 0.9 * effectiveness
            sim_state.resource_efficiency = 0.6 * effectiveness
            sim_state.time_to_containment = 0.8 * effectiveness
            
        elif strategy_type == 'healthcare':
            sim_state.population.survived = 0.998
            sim_state.economy.gdp_preserved = 0.2 * effectiveness
            sim_state.infection_control = 0.95 * effectiveness
            sim_state.resource_efficiency = 0.5 * effectiveness
            sim_state.time_to_containment = 0.6 * effectiveness
            
        elif strategy_type == 'economy':
            sim_state.population.survived = 0.98
            sim_state.economy.gdp_preserved = 0.8 * effectiveness
            sim_state.infection_control = 0.7 * effectiveness
            sim_state.resource_efficiency = 0.7 * effectiveness
            sim_state.time_to_containment = 0.5 * effectiveness
            
        elif strategy_type == 'adaptive':
            sim_state.population.survived = 0.997
            sim_state.economy.gdp_preserved = 0.6 * effectiveness
            sim_state.infection_control = 0.9 * effectiveness
            sim_state.resource_efficiency = 0.8 * effectiveness
            sim_state.time_to_containment = 0.85 * effectiveness
            
        elif strategy_type == 'regional':
            sim_state.population.survived = 0.996
            sim_state.economy.gdp_preserved = 0.5 * effectiveness
            sim_state.infection_control = 0.85 * effectiveness
            sim_state.resource_efficiency = 0.75 * effectiveness
            sim_state.time_to_containment = 0.8 * effectiveness
            
        elif strategy_type == 'phase_based':
            sim_state.population.survived = 0.999
            sim_state.economy.gdp_preserved = 0.7 * effectiveness
            sim_state.infection_control = 0.95 * effectiveness
            sim_state.resource_efficiency = 0.9 * effectiveness
            sim_state.time_to_containment = 0.9 * effectiveness
        
        else:  # Default
            sim_state.population.survived = 0.99
            sim_state.economy.gdp_preserved = 0.5 * effectiveness
            sim_state.infection_control = 0.8 * effectiveness
            sim_state.resource_efficiency = 0.7 * effectiveness
            sim_state.time_to_containment = 0.75 * effectiveness
        
        # Execute callbacks
        for step in range(steps):
            state_copy = copy.deepcopy(sim_state)
            for callback in self.step_callbacks:
                callback(step, state_copy)
        
        return sim_state

class SimulationState:
    """Class to hold simulation state."""
    
    def __init__(self):
        self.population = Population()
        self.economy = Economy()
        self.infection_control = 0.0  
        self.resource_efficiency = 0.0
        self.time_to_containment = 0.0

class Population:
    """Class to hold population data."""
    
    def __init__(self):
        self.total = 1000000
        self.infected = 5000
        self.recovered = 0
        self.deaths = 0
        self.survived = 0.99  # 99% survival rate
        
class Economy:
    """Class to hold economy data."""
    
    def __init__(self):
        self.gdp_preserved = 0.5  # 50% of GDP preserved
