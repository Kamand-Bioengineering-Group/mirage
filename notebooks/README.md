# XPECTO - Epidemic 2.0 Competition

## Overview

The XPECTO Epidemic 2.0 Competition is a competitive simulation where players develop strategies to combat an epidemic. This README provides information on how to participate, how scoring works, and tips for developing effective strategies.

## Getting Started

1. Make a copy of the `epidemic-competition.ipynb` notebook
2. Enter your name in the `PLAYER_NAME` variable
3. Run the setup cell to initialize the competition
4. Develop and implement your strategy
5. Run the simulation for the standard 730 steps (2 years)
6. Save your results to be added to the leaderboard

## Competition Features

### Standardized Initial Conditions

All players start with the same epidemic scenario to ensure fair competition. The initial conditions include:

- The same set of countries and population distribution
- The same initial infection rates
- The same available resources
- The same economic conditions

### Scoring System

Your performance is evaluated based on multiple components:

| Component | Weight | Description |
|-----------|--------|-------------|
| Population Survived | 30% | Percentage of the initial population that survived |
| GDP Preserved | 20% | How well you maintained economic prosperity |
| Infection Control | 20% | How effectively you controlled the spread of the epidemic |
| Resource Efficiency | 15% | How efficiently you used your resources |
| Time to Containment | 15% | How quickly you contained the epidemic |

### Strategic Components

The simulation allows for different strategic approaches:

1. **Healthcare Investment**
   - Building hospitals
   - Distributing medical supplies
   - Vaccination campaigns

2. **Containment Measures**
   - Quarantine facilities
   - Mask implementation
   - Sanitation implementation

3. **Economic Management**
   - Strategic lockdowns of economic zones
   - Maintaining essential infrastructure
   - Balancing health measures with economic activity

4. **Travel Restrictions**
   - Airport lockdowns
   - Port restrictions
   - Tourist zone controls

## Developing Your Strategy

### Strategic Considerations

1. **Early Detection and Containment**
   - Implement quarantine and sanitation measures early
   - Identify high-risk areas and prioritize interventions

2. **Resource Allocation**
   - Distribute limited resources efficiently
   - Invest in healthcare infrastructure strategically

3. **Travel Restrictions**
   - Control movement through airports and ports
   - Implement targeted restrictions rather than complete shutdowns

4. **Economic Balance**
   - Maintain essential economic activity
   - Implement targeted lockdowns rather than blanket restrictions

5. **Healthcare Infrastructure**
   - Build hospitals in high-density areas
   - Use aid kits and masks to slow the spread

### Sample Interventions

The notebook includes examples of various interventions:

- Mask Implementation
- Quarantine Facilities
- Airport Lockdowns
- Hospital Building
- Vaccine Distribution

Customize these interventions based on your strategy, targeting specific countries, states, and timing for maximum effect.

## Submitting Your Results

After completing the simulation:

1. Use `epidemic_two_engine.display_score()` to see your final score
2. Save your results with `epidemic_two_engine.save_results()`
3. The results will be saved to the specified `COMPETITION_RESULTS_DIR`
4. You can view the current leaderboard with `epidemic_two_engine.display_leaderboard()`

## Tips for Success

1. **Monitor in Real-Time** - Use Tensorboard to monitor the epidemic progression
2. **Adapt Your Strategy** - Be prepared to pivot based on how the epidemic evolves
3. **Balance All Factors** - Don't focus solely on infection control at the expense of the economy
4. **Timing Matters** - Early intervention is often more effective than reactive measures
5. **Analyze Past Attempts** - Learn from previous runs and refine your approach

Good luck, and may the best strategy win! 