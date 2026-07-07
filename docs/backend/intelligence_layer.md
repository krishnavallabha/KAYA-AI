# intelligence layer - detailed documentation

contains the analytical engine of flowsense, executing data reconciliation, Bayesian eta forecasting, and schedule network graph analysis.

## 1. material tracker reconciliation (`material_tracker.py`)
- **objective**: resolves conflicting status inputs across multiple signals for a single sku.
- **confidence weighting logic**:
  - **source credibility**: `MANUAL` (1.0), `VISION` (0.95), `PORTAL` (0.90), `EMAIL` (0.80).
  - **recency time-decay**: computes hours elapsed since the signal was logged ($t$). applies exponential decay:
    $$\text{confidence} = \text{credibility} \times e^{-\lambda t}$$
    where $\lambda = 0.05$ (meaning signal weight decays by 5% every hour).
  - **composite scoring**: adds a tiny status modifier to favor signals showing more advanced lifecycle stages if scores are identical:
    $$\text{score} = \text{confidence} + (\text{status\_stage} \times 0.01)$$
    where stages are: ordered=1, fabricating=2, shipped=3, in_transit=4, delivered=5.
- **reconciliation output**: updates the central database record for that material with the reconciled status and location.

## 2. fabrication-to-delivery forecaster (`forecaster.py`)
- **objective**: calculates arrival estimates (eta), 90% confidence boundaries, and probability of delays.
- **parameters**:
  - **historical profiles**:
    - `SteelCorp Ltd`: mean delay of 5 days, standard deviation of 3.5 days.
    - `ConcreteSupply Co`: mean delay of 2 days, standard deviation of 1.2 days.
    - `DEFAULT`: mean delay of 3 days, standard deviation of 2.5 days.
  - **stage modifiers**: modifier values scale mean delay and uncertainty as progress advances:
    - `ORDERED`: delay mult = 1.0, std dev mult = 1.2.
    - `SHIPPED`: delay mult = 0.5, std dev mult = 0.8.
    - `DELIVERED`: delay mult = 0.0, std dev mult = 0.0.
- **probability calculation**:
  - calculates expected eta = $\text{promised\_date} + \text{expected\_delay}$.
  - uses cumulative distribution function (`scipy.stats.norm.cdf`) to find:
    $$\text{delay\_probability} = 1.0 - P(\text{Arrival} \leq \text{Promised})$$
    based on the z-score:
    $$Z = \frac{\text{promised\_date} - \text{forecast\_date}}{\text{std\_dev\_days}}$$

## 3. cascade impact engine (`cascade_engine.py`)
- **objective**: builds the schedule graph and checks how material delays propagate downstream.
- **graph engine**: uses `networkx` to build a directed graph (`nx.DiGraph`).
  - **nodes**: activities, with attributes `name`, `start`, `end`, `is_critical`, and `delay_days`.
  - **edges**: precedence relationships (e.g. Finish-to-Start).
- **traversal logic**:
  - maps materials to target activities. if material eta is later than task start date, initial `delay_days` is set.
  - runs `nx.topological_sort` to get tasks ordered by schedule sequence.
  - propagates delays using breadth-first search (bfs):
    $$\text{successor\_delay} = \max(\text{current\_successor\_delay}, \text{predecessor\_delay})$$
  - if a critical path task gets delayed, `critical_path_impacted` is marked `True`.
