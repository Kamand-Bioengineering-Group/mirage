# XPECTO Epidemic 2.0 Competition Rules

## Overview

The XPECTO Epidemic 2.0 Competition challenges participants to develop effective strategies for managing a simulated epidemic. Players must balance public health outcomes, economic impacts, and resource utilization to achieve the highest possible score across standardized scenarios.

## Eligibility

- The competition is open to all participants who have registered through the competition system
- Each participant must use their real name for identification
- Participants may only register once and submit results under a single player ID

## Competition Structure

### Scenarios

All participants will compete on the same standardized scenarios:

1. **Standard Scenario** - A base difficulty outbreak with moderate parameters
2. **Challenging Scenario** - A more difficult scenario with multiple infection sites and higher R0
3. **Specialized Scenarios** (optional) - Additional scenarios testing specific aspects of epidemic management

### Competition Phases

The competition consists of two phases:

1. **Practice Phase** - Unlimited attempts, results not counted for ranking
2. **Official Phase** - Limited attempts per scenario, results count for final rankings

## Attempt Rules

### Practice Attempts

- Unlimited practice attempts are allowed per scenario
- Practice attempts will be recorded but do not count for leaderboard rankings
- Practice results can be viewed by the player but are not visible to other competitors

### Official Attempts

- Each participant is limited to **3 official attempts per scenario**
- Only the best score for each scenario is used for ranking
- Official attempts cannot be deleted or retracted once submitted
- The time limit for each attempt is a maximum of 730 simulation steps (representing 2 years)

## Scoring System

### Scoring Components

Scores are calculated on a 0-1 scale based on weighted performance metrics:

1. **Population Survived (30%)** - Percentage of the initial population that survived
   - Calculation: `(initial_population - dead_population) / initial_population`
   - Higher values are better

2. **GDP Preserved (20%)** - Maintenance of economic prosperity
   - Calculation: Based on normalized GDP change 
   - Higher values are better

3. **Infection Control (20%)** - Effectiveness in preventing widespread infection
   - Calculation: `1.0 - max_infection_rate`
   - Higher values (lower infection rates) are better

4. **Resource Efficiency (15%)** - Efficiency in using available resources
   - Calculation: Results achieved per resources spent
   - Higher values are better

5. **Time to Containment (15%)** - Speed of epidemic containment
   - Calculation: Earlier containment yields higher scores
   - Higher values are better

### Final Score Calculation

The final score is a weighted average of the component scores:

```
final_score = (
    population_survived * 0.30 +
    gdp_preserved * 0.20 +
    infection_control * 0.20 +
    resource_efficiency * 0.15 +
    time_to_containment * 0.15
)
```

### Ranking

Players are ranked based on:

1. For each individual scenario: The best official attempt score
2. For overall ranking: The average of the best official scores across all required scenarios

## Strategy Documentation

Each participant must submit a strategy document explaining their approach:

- The document should explain the key principles of your strategy
- Technical implementation details should be included
- The document must be submitted before the competition deadline
- Strategy documents will be made available to all participants after the competition concludes

## Competition Management

### Standardization

- All scenarios use fixed seeds to ensure reproducibility
- Initial conditions are identical for all participants
- The simulation engine version is fixed throughout the competition period

### Disqualification

Participants may be disqualified for:

- Attempting to exploit bugs or vulnerabilities in the simulation engine
- Using multiple accounts or identities
- Sharing solutions during the competition period
- Submitting results that cannot be reproduced by competition administrators

### Tiebreaker Rules

In case of tied scores, the following tiebreakers will be applied in order:

1. Higher score in the Challenging scenario
2. Higher score in specialized scenarios (if applicable)
3. Earlier submission timestamp of the highest-scoring attempt

## Technical Requirements

### System Requirements

- Python 3.8 or higher
- Required libraries as specified in the competition setup documentation
- Sufficient computational resources to run simulations (at least 4GB RAM recommended)

### Submission Format

All official attempts must be submitted through the competition system:

1. Use the provided CompetitionManager API
2. Ensure all interventions are properly registered
3. Verify that the attempt is marked as "official" before submission

## Timeline

- **Practice Phase**: [Start Date] to [End Date]
- **Official Phase**: [Start Date] to [End Date]
- **Results Announcement**: [Announcement Date]

## Prizes and Recognition

- First Place: [Prize Details]
- Second Place: [Prize Details]
- Third Place: [Prize Details]
- Honorable Mentions: [Recognition Details]

Winners will be announced at [Announcement Event/Platform] and featured on the XPECTO project website.

## Questions and Support

For questions regarding rules, technical issues, or any other competition-related matters:

- Email: [Support Email]
- Forum: [Support Forum URL]
- Office Hours: [Schedule Details]

## Rule Changes

The competition organizers reserve the right to modify these rules for clarity or to address unforeseen circumstances. Any changes will be communicated to all participants.

---

By participating in the XPECTO Epidemic 2.0 Competition, you agree to abide by these rules and the decisions of the competition organizers. 