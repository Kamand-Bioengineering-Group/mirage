# XPECTO Epidemic 2.0 Competition Scoring System

## Overview

The XPECTO Epidemic 2.0 Competition uses a comprehensive scoring system that evaluates players' performance across multiple dimensions. The final score is calculated on a 0-1 scale, where 1 represents perfect performance. Each component is weighted based on its importance to the overall goal of epidemic management.

## Scoring Components

### 1. Population Survived (30% of final score)
**Formula**: `(initial_population - dead_population) / initial_population`

- **Range**: 0 to 1
- **Example**: 
  - Initial population: 1,000,000
  - Dead: 100,000
  - Score: (1,000,000 - 100,000) / 1,000,000 = 0.9
  - Weighted contribution: 0.9 * 0.30 = 0.27

### 2. GDP Preserved (20% of final score)
**Formula**: `min(1.0, max(0.0, (gdp_change + 1.0) / 2.0))`
where `gdp_change = (final_gdp - initial_gdp) / initial_gdp`

- **Range**: 0 to 1
- **Example**:
  - Initial GDP: 1,000,000
  - Final GDP: 900,000
  - GDP change: -0.1 (-10%)
  - Score: ((-0.1 + 1.0) / 2.0) = 0.45
  - Weighted contribution: 0.45 * 0.20 = 0.09

### 3. Infection Control (20% of final score)
**Formula**: `1.0 - max_infection_rate`
where `max_infection_rate = max(infected_population / total_population)` across all steps

- **Range**: 0 to 1
- **Example**:
  - Maximum infection rate: 15%
  - Score: 1.0 - 0.15 = 0.85
  - Weighted contribution: 0.85 * 0.20 = 0.17

### 4. Resource Efficiency (15% of final score)
**Formula**: Complex calculation based on results achieved per resources spent
```python
if total_resources_spent > 0:
    lives_saved_per_resource = population_survived_score / log(1 + total_resources_spent)
    infections_controlled_per_resource = infection_control_score / log(1 + total_resources_spent)
    resource_efficiency_score = min(1.0, max(0.0, (lives_saved_per_resource + infections_controlled_per_resource) / 2 * 5.0))
else:
    resource_efficiency_score = 0.5 * (population_survived_score + infection_control_score)
```

- **Range**: 0 to 1
- **Example**:
  - Resources spent: 10,000
  - Population survived score: 0.9
  - Infection control score: 0.85
  - Score: 0.75 (normalized efficiency metric)
  - Weighted contribution: 0.75 * 0.15 = 0.1125

### 5. Time to Containment (15% of final score)
**Formula**: `1.0 - (containment_step / total_steps)`
where containment is achieved when infection rate consistently decreases

- **Range**: 0 to 1
- **Example**:
  - Containment achieved at step 200
  - Total steps: 730
  - Score: 1.0 - (200/730) = 0.726
  - Weighted contribution: 0.726 * 0.15 = 0.1089

## Final Score Calculation

The final score is the sum of all weighted component scores:

```python
final_score = (
    (population_survived * 0.30) +
    (gdp_preserved * 0.20) +
    (infection_control * 0.20) +
    (resource_efficiency * 0.15) +
    (time_to_containment * 0.15)
)
```

Using the example above:
```
Final Score = 0.27 + 0.09 + 0.17 + 0.1125 + 0.1089 = 0.7514
```

## Determining the Winner

### Competition Process

1. **Standardized Conditions**
   - All players start with identical:
     - Country configurations
     - Initial infection rates
     - Available resources
     - Economic conditions

2. **Simulation Duration**
   - Each player runs the simulation for exactly 730 steps (2 years)
   - Players cannot modify the simulation duration

3. **Result Recording**
   - After each simulation:
     - Final scores are calculated
     - Results are saved to JSON files
     - Leaderboard is updated

### Winner Selection

1. **Primary Criterion: Final Score**
   - Players are ranked by their final score
   - The player with the highest final score wins

2. **Tiebreaker Rules** (in case of equal final scores):
   1. Higher Population Survived score
   2. Higher Infection Control score
   3. Higher Resource Efficiency score
   4. Earlier Time to Containment
   5. Higher GDP Preserved score

### Multiple Attempts

1. **Attempt Limits**
   - Each player is allowed up to 3 attempts
   - Only their best score is considered for final ranking

2. **Result Verification**
   - All attempts must be:
     - Completed with standard settings
     - Run for the full 730 steps
     - Saved with proper documentation

### Final Leaderboard

The final leaderboard displays:
1. Rank
2. Player Name
3. Final Score
4. Component Scores
   - Population Survived
   - GDP Preserved
   - Infection Control
   - Resource Efficiency
   - Time to Containment

Example Leaderboard:
```
Rank | Player | Final Score | Pop. Survived | GDP | Infection | Resource | Time
-----|---------|-------------|---------------|-----|-----------|----------|------
1    | Alice   | 0.8514     | 0.95         | 0.82| 0.88      | 0.79     | 0.85
2    | Bob     | 0.8123     | 0.92         | 0.79| 0.85      | 0.75     | 0.80
3    | Charlie | 0.7891     | 0.88         | 0.81| 0.82      | 0.72     | 0.75
```

## Score Tracking

During the simulation:
1. Use `epidemic_two_engine.display_score()` to view current scores
2. Monitor Tensorboard for real-time metrics
3. Save final results with `epidemic_two_engine.save_results()`
4. View rankings with `epidemic_two_engine.display_leaderboard()`

## Competition Rules

1. **No Modifications**
   - Players cannot modify the scoring system
   - Initial conditions must remain standard
   - Simulation duration is fixed

2. **Fair Play**
   - All interventions must use provided functions
   - No direct manipulation of simulation state
   - No exploitation of system bugs

3. **Result Submission**
   - Results must include:
     - Player identification
     - Complete metrics history
     - Intervention log
     - Final state data

4. **Disqualification**
   - Attempts to manipulate scoring system
   - Use of non-standard initial conditions
   - Incomplete simulation runs
   - Missing or corrupted result data

## Production Performance Optimizations

### 1. Metric Calculation Optimizations

1. **Cached Metrics**
   - Population metrics cached at fixed intervals (e.g., every 10 steps)
   - GDP changes tracked through delta updates instead of full recalculation
   - Max infection rate updated only when current rate exceeds cached maximum

2. **Resource Efficiency Optimization**
   - Pre-compute logarithmic values for common resource amounts
   - Update resource efficiency score at checkpoints rather than every step
   - Cache intermediate calculation results

3. **Time to Containment Optimization**
   - Use a sliding window to detect containment instead of full history
   - Track infection rate trends with exponential moving average
   - Early stopping if containment criteria met

### 2. Storage and Processing

1. **Batch Processing**
   - Accumulate metrics in memory for N steps
   - Bulk update scores at checkpoints
   - Asynchronous writes to storage

2. **Data Storage**
   - Use efficient binary format for metrics history
   - Implement data retention policies
   - Compress historical data

3. **Leaderboard Updates**
   - Cache leaderboard calculations
   - Update rankings incrementally
   - Implement pagination for large datasets

### 3. Implementation Guidelines

1. **Memory Management**
   ```python
   # Example of optimized metric tracking
   class MetricTracker:
       def __init__(self, cache_interval=10):
           self.cache_interval = cache_interval
           self.metrics_cache = {}
           self.step_counter = 0
           
       def update_metrics(self, current_stats):
           self.step_counter += 1
           if self.step_counter % self.cache_interval == 0:
               # Bulk update cached metrics
               self.update_cache(current_stats)
           else:
               # Quick delta updates
               self.update_deltas(current_stats)
   ```

2. **Efficient Score Updates**
   ```python
   # Example of optimized score calculation
   class ScoreManager:
       def __init__(self):
           self.cached_scores = {}
           self.log_lookup = self._precompute_logs()
           
       def _precompute_logs(self):
           # Pre-compute common logarithmic values
           return {i: log(1 + i) for i in range(0, 10001, 100)}
           
       def get_resource_efficiency(self, resources):
           # Use pre-computed logs for common values
           log_value = self.log_lookup.get(resources)
           if log_value is None:
               log_value = log(1 + resources)
           return self._calculate_efficiency(log_value)
   ```

3. **Async Processing**
   ```python
   # Example of async leaderboard updates
   class LeaderboardManager:
       def __init__(self):
           self.scores_queue = Queue()
           self.update_thread = Thread(target=self._process_updates)
           
       async def update_leaderboard(self, player_score):
           await self.scores_queue.put(player_score)
           
       async def _process_updates(self):
           while True:
               scores = await self.batch_get_scores()
               if scores:
                   await self._bulk_update_rankings(scores)
   ```

### 4. Monitoring and Scaling

1. **Performance Metrics**
   - Track calculation time per component
   - Monitor memory usage
   - Log processing bottlenecks

2. **Auto-scaling Triggers**
   - Scale based on player count
   - Adjust cache intervals dynamically
   - Balance memory vs. computation

3. **Fallback Mechanisms**
   - Simplified scoring for high load
   - Degraded service modes
   - Circuit breakers for critical components

### 5. Deployment Recommendations

1. **Infrastructure**
   - Use dedicated scoring servers
   - Implement caching layers (Redis/Memcached)
   - Consider serverless for scaling

2. **Database**
   - Partition data by time periods
   - Index frequently accessed metrics
   - Archive historical data

3. **API Design**
   - Implement rate limiting
   - Use websockets for real-time updates
   - Cache common API responses

These optimizations ensure the scoring system remains responsive even with:
- Large number of concurrent players
- Extended simulation durations
- Complex scoring calculations
- Real-time leaderboard updates 

## Competition Format and Replayability

### 1. Practice Phase (2 weeks)
- Players get unlimited practice attempts
- Use practice attempts to:
  - Learn the simulation mechanics
  - Test different strategies
  - Understand scoring components
  - Practice runs don't count towards final ranking

### 2. Competition Phase (1 week)
1. **Three Official Attempts**
   - Each player gets exactly 3 competition attempts
   - Best score counts for final ranking
   - All attempts must be completed within the competition week

2. **Fixed Scenarios**
   - Two predefined scenarios:
     - **Scenario A**: Standard outbreak conditions
     - **Scenario B**: More challenging conditions (higher R0, limited resources)
   - Players must complete both scenarios
   - Final ranking based on average score across both scenarios

3. **Strategy Development**
   - Use practice phase learnings
   - Document strategy choices
   - Track resource allocation decisions
   - Record intervention timing

### 3. Result Submission

1. **Required Documentation**
   - Strategy summary (max 500 words)
   - Key decision points
   - Resource allocation breakdown
   - Final metrics achieved

2. **Verification Process**
   - All submissions reviewed for:
     - Complete 730-step runs
     - Standard initial conditions
     - Valid intervention sequences
     - No simulation exploits

### 4. Competition Timeline

1. **Week 1-2: Practice Phase**
   - Access to simulation
   - Strategy development
   - System familiarization
   - Documentation review

2. **Week 3: Competition Phase**
   - Official attempts
   - Result submissions
   - Strategy documentation
   - Final leaderboard updates

3. **Week 4: Results and Analysis**
   - Winner announcement
   - Top strategy showcase
   - Performance analysis
   - Competition insights

### 5. Learning Resources

1. **Basic Documentation**
   - System mechanics
   - Scoring explanation
   - Available interventions
   - Basic strategies

2. **Example Scenarios**
   - Sample run-throughs
   - Common pitfalls
   - Effective interventions
   - Resource management tips

These focused features ensure:
- Clear competition structure
- Fair attempt distribution
- Strategy development opportunity
- Meaningful comparison of results
- Manageable scope for a one-off event 