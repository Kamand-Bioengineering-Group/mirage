# XPECTO Game Architecture

This document explains the architecture of XPECTO Epidemic 2.0, detailing the various components of the game and how they interact with each other.

## System Overview

XPECTO Epidemic 2.0 is a simulation game where players develop strategies to manage an epidemic. The system is composed of several interconnected components that work together to create a realistic simulation environment.

```
┌─────────────────────────────────────────────────────────────────────┐
│                          XPECTO Architecture                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐     ┌───────────────┐     ┌─────────────────────┐  │
│  │             │     │               │     │                     │  │
│  │   Player    │────▶│  Competition  │────▶│  Simulation Engine  │  │
│  │  Interface  │     │    Manager    │     │                     │  │
│  │             │     │               │     │                     │  │
│  └─────────────┘     └───────────────┘     └─────────────────────┘  │
│         ▲                    │                       │              │
│         │                    │                       │              │
│         └────────────────────┼───────────────────────┘              │
│                              │                                      │
│                              ▼                                      │
│                     ┌───────────────┐                               │
│                     │               │                               │
│                     │   Storage &   │                               │
│                     │   Analytics   │                               │
│                     │               │                               │
│                     └───────────────┘                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Player Interface

**Role**: The entry point for players to interact with the game.

**Key Features**:
- Provides access to practice and competition modes
- Displays simulation results and analytics
- Allows strategy development and submission

**Key Files**:
- `notebooks/practice_playground.ipynb`: Interactive notebook for developing strategies

### 2. Competition Manager

**Role**: Manages the competition workflow, including player registration, scenario configuration, and attempt validation.

**Key Features**:
- Player registration and authentication
- Scenario management and configuration
- Competition attempt tracking and validation
- Result calculation and normalization

**Key Files**:
- `src/competition/competition_manager.py`: Core competition management logic
- `src/competition/competition_service.py`: Service layer for competition operations
- `src/competition/models.py`: Data models for competition entities

### 3. Simulation Engine

**Role**: The core simulation logic that models epidemic spread and intervention effects.

**Key Features**:
- Disease spread modeling (SIR models)
- Population health dynamics
- Economic impact simulation
- Resource allocation mechanics
- Intervention effectiveness modeling

**Engine Types**:
- `MockEngine`: Simplified engine for testing and practice
- `EnhancedEngine`: Advanced engine with variant system and complex dynamics

**Key Files**:
- `src/competition/testing/engine_adapter.py`: Contains the MockEngine
- `src/competition/testing/enhanced_engine.py`: Contains the EnhancedEngine
- `src/competition/engine.py`: Core simulation engine interface

### 4. Storage & Analytics

**Role**: Stores data about players, attempts, and results; provides analytical capabilities.

**Key Features**:
- Result storage and retrieval
- Performance analytics and visualization
- Historical data comparison
- Leaderboard generation

**Key Files**:
- `src/competition/storage.py`: Data storage interfaces
- `src/competition/analytics.py`: Analytical functions and visualization
- `src/competition/enhanced_storage.py`: Enhanced storage for complex data

## Detailed Component Breakdown

### 1. Simulation Components

#### 1.1 SimulationState

Represents the current state of the simulation at any given time step.

**Properties**:
- Population data (susceptible, infected, recovered, dead)
- Economic data (GDP, economic health)
- Time data (current step, containment status)
- Resource data (allocated resources, remaining resources)

#### 1.2 Disease Models

Mathematical models that determine how the disease spreads through the population.

**Types**:
- Standard SIR (Susceptible-Infected-Recovered)
- Enhanced SIR with variants and stochasticity
- Network-based spread models

#### 1.3 Intervention Mechanisms

Systems that translate player actions into simulation effects.

**Examples**:
- Lockdown effects on transmission
- Resource allocation effects on mortality and economy
- Travel restriction effects on spread patterns

### 2. Player-Focused Components

#### 2.1 Strategy Interface

Defines how player strategies interact with the simulation engine.

**Key Methods**:
- `apply(engine)`: Applies a strategy to the simulation engine
- `register_step_callback(callback)`: Registers a function to execute after each step

#### 2.2 Scenario System

Defines different epidemic scenarios with varying parameters.

**Scenario Types**:
- Standard (baseline difficulty)
- Challenging (higher difficulty)
- Specialized (focused on specific aspects)

#### 2.3 Scoring System

Evaluates player performance across multiple metrics.

**Key Metrics**:
- Population survived
- GDP preserved
- Infection control
- Resource efficiency
- Time to containment
- Variant control (Enhanced Engine only)

### 3. Advanced Features (Enhanced Engine)

#### 3.1 Variant System

Models the emergence and spread of disease variants with different characteristics.

**Features**:
- Dynamic variant emergence based on thresholds
- Variant-specific parameters (transmissibility, mortality, immune escape)
- Research targeting and variant-specific interventions

#### 3.2 Regional Modeling

Simulates different regions with varying characteristics.

**Region Types**:
- Urban (high density, high economic output)
- Rural (low density, lower economic output)

#### 3.3 Economic Sector Modeling

Models different economic sectors with varying responses to interventions.

**Sector Types**:
- Essential services
- In-person services
- Remote-capable services

## Data Flow

1. **Strategy Creation**: Player develops an intervention strategy
2. **Strategy Application**: Strategy is applied to the simulation engine
3. **Simulation Execution**: Engine runs the simulation with interventions
4. **Result Calculation**: Engine calculates performance metrics
5. **Score Normalization**: Results are normalized for comparison
6. **Result Storage**: Performance data is stored for analysis
7. **Feedback**: Player receives feedback on strategy performance

## Development and Extension

The XPECTO architecture is designed to be modular and extensible. New components can be added to enhance the simulation:

1. **New Scenario Types**: Adding new scenarios with different parameters
2. **Engine Enhancements**: Expanding the simulation engine with more complex models
3. **Additional Metrics**: Creating new ways to evaluate strategy performance
4. **UI Improvements**: Enhancing the player interface and visualization

## Key Interfaces

### Engine Interface
```python
class Engine:
    def reset(self):
        """Reset the simulation state."""
        
    def step(self):
        """Run one step of the simulation."""
        
    def run(self, steps, interventions=None):
        """Run simulation for specified steps with interventions."""
        
    def set_lockdown_level(self, level):
        """Set lockdown severity level."""
        
    def allocate_resources(self, category, amount):
        """Allocate resources to specified category."""
```

### Strategy Interface
```python
def strategy(engine):
    """Apply strategy to engine."""
    # Set initial conditions
    engine.set_lockdown_level(0.5)
    engine.allocate_resources('healthcare', 200)
    
    # Define dynamic response
    def step_callback(step, state):
        # Adjust strategy based on simulation state
        pass
    
    # Register callback
    engine.register_step_callback(step_callback)
```

## Conclusion

The XPECTO architecture provides a flexible framework for simulating epidemic management strategies. The modular design allows for continuous improvement and customization, while the standardized interfaces ensure compatibility across different components.

Players interact with the system primarily through strategy development, while the underlying components work together to provide a realistic and challenging simulation environment. 