# Lionfish Invasion Simulation
### CS 4632 — Modeling and Simulation | Kennesaw State University

A spatially explicit, agent-based simulation of the invasive spread of *Pterois volitans* (red lionfish) along the U.S. Atlantic coast, modelling population dynamics, larval dispersal, and reef ecosystem degradation.

---

## Project Overview

Lionfish are one of the most ecologically damaging marine invasions ever recorded. With no effective natural predators in Atlantic waters, they suppress native reef fish populations by up to 79% (Albins & Hixon, 2008). This simulation integrates:

- **Extended Lotka-Volterra equations** — predator-prey population dynamics per reef zone
- **Reaction-Diffusion dispersal model** — larval spread via probabilistic ocean current kernels
- **Compartmental reef health model** — zone health transitions (Healthy → Degraded → Collapsed)

---

## Repository Structure

```
Lionfish-Simulation/
├── main.py                  # Entry point — run this
├── requirements.txt         # Python dependencies
├── visualizer.py            # Plot generation (4 chart types)
├── simulation/
│   ├── __init__.py
│   ├── simulation_model.py  # Central controller & time-step loop
│   ├── reef_zone.py         # ReefZone entity + HealthState enum
│   ├── lionfish_agent.py    # LionfishAgent with full lifecycle
│   ├── lotka_volterra.py    # Model 1: LV predator-prey ODE solver
│   ├── dispersal_model.py   # Model 2: Reaction-diffusion larval dispersal
│   └── data_collector.py    # Metrics recording → CSV + JSON
├── output/                  # Generated plots and data (gitignored)
└── docs/                    # Project documents (proposals, reports)
```

---

## Setup & Run Instructions

### 1. Clone the repository
```bash
git clone https://github.com/Londyn98/Lionfish-Simulation.git
cd Lionfish-Simulation
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the simulation
```bash
# Default: 2-year run (104 weeks), 10x8 grid, no culling
python main.py

# 1-year run with culling interventions enabled
python main.py --steps 52 --culling

# Custom grid and seed population
python main.py --grid-w 15 --grid-h 10 --seed-n 10

# Skip plot generation
python main.py --no-plots

# Full options
python main.py --help
```

### 5. View outputs
After running, check the `output/` folder:
- `metrics.csv` — per-step data for all tracked metrics
- `metrics.json` — same data in JSON format
- `plot_populations.png` — lionfish vs prey time series
- `plot_reef_health.png` — reef health state area chart
- `plot_spread_radius.png` — spatial invasion spread over time
- `plot_heatmap.png` — grid-level lionfish density + health heatmap

---

## Command-Line Options

| Flag | Default | Description |
|------|---------|-------------|
| `--steps` | 104 | Number of weekly time steps |
| `--grid-w` | 10 | Grid width (zones) |
| `--grid-h` | 8 | Grid height (zones) |
| `--seed-n` | 5 | Initial lionfish count |
| `--culling` | off | Enable culling interventions |
| `--cull-rate` | 0.60 | Fraction removed per cull event |
| `--seed` | 42 | Random seed for reproducibility |
| `--no-plots` | off | Skip plot generation |

---

## Models & Algorithms

### Model 1 — Extended Lotka-Volterra (lotka_volterra.py)
```
dP/dt = r_P * P * (1 - P/K_P) - α * P * L
dL/dt = β * α * P * L - δ_L * L + Λ(t)
```
Native prey follow logistic growth, reduced by lionfish predation. Lionfish mortality δ_L is near-zero (~0.02/yr) reflecting the absence of Atlantic predators.

### Model 2 — Reaction-Diffusion Dispersal (dispersal_model.py)
Larval dispersal kernel combines Gaussian distance decay with directional current bias:
```
w(dx, dy) ∝ exp(-dist / σ) * (1 + strength * cos(θ - θ_current))
```
Larvae survive at rate `survival_rate` and settle in destination zones according to normalised weights.

### Model 3 — Reef Health State Machine (reef_zone.py)
Three-state compartmental model:
- **Healthy** → **Degraded** when prey < 50% of K
- **Degraded** → **Collapsed** when prey < 20% of K
- Recovery allowed when lionfish density drops below threshold

---

## Tracked Metrics

| Metric | Description |
|--------|-------------|
| `total_lionfish` | Total live lionfish agents |
| `mean_prey` | Mean prey population across all zones |
| `spread_radius` | Distance from origin to farthest colonised zone |
| `zones_colonised` | Number of zones with at least one lionfish |
| `zones_healthy/degraded/collapsed` | Zone counts by health state |
| `prey_depletion_rate` | Week-over-week change in mean prey |

---

## Requirements

- Python 3.10+
- matplotlib >= 3.7.0
- numpy >= 1.24.0

No external simulation framework required — built from scratch.

---

## References

- Albins, M.A. & Hixon, M.A. (2008). *Marine Ecology Progress Series*, 367, 233–238.
- Schofield, P.J. (2009). *Aquatic Invasions*, 4(3), 473–479.
- Cowen, R.K. et al. (2006). *Science*, 311(5760), 522–527.
- Okubo, A. & Levin, S.A. (2001). *Diffusion and Ecological Problems*, Springer.
- Côté, I.M. et al. (2013). *Biological Conservation*, 164, 50–61.
