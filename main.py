"""
main.py
Entry point for the Lionfish Invasion Simulation.

Usage
-----
  python main.py                      # default 2-year run, no culling
  python main.py --steps 52           # 1-year run
  python main.py --culling            # enable culling interventions
  python main.py --steps 104 --culling --seed 7
"""

import argparse
from simulation.simulation_model import SimulationModel
from simulation.lotka_volterra   import LotkaVolterraParams
from simulation.dispersal_model  import DispersalParams
from visualizer                  import generate_all_plots


def parse_args():
    parser = argparse.ArgumentParser(
        description="Lionfish Invasion Simulation — CS 4632"
    )
    parser.add_argument("--steps",    type=int,   default=104,
                        help="Number of weekly time steps (default: 104 = 2 yrs)")
    parser.add_argument("--grid-w",   type=int,   default=10,
                        help="Grid width  (default: 10)")
    parser.add_argument("--grid-h",   type=int,   default=8,
                        help="Grid height (default: 8)")
    parser.add_argument("--seed-n",   type=int,   default=5,
                        help="Initial lionfish count (default: 5)")
    parser.add_argument("--culling",  action="store_true",
                        help="Enable periodic culling interventions")
    parser.add_argument("--cull-rate", type=float, default=0.60,
                        help="Fraction of lionfish removed per cull (default: 0.60)")
    parser.add_argument("--seed",     type=int,   default=42,
                        help="Random seed for reproducibility (default: 42)")
    parser.add_argument("--no-plots", action="store_true",
                        help="Skip generating visualisation plots")
    return parser.parse_args()


def main():
    args = parse_args()

    # Build model
    model = SimulationModel(
        grid_w           = args.grid_w,
        grid_h           = args.grid_h,
        n_seed_lionfish  = args.seed_n,
        seed_zone        = (0, args.grid_h // 2),  # mid-left edge (coast entry)
        total_steps      = args.steps,
        culling_enabled  = args.culling,
        culling_rate     = args.cull_rate,
        culling_interval = 12,
        lv_params        = LotkaVolterraParams(
            r_prey  = 0.30,
            k_prey  = 500.0,
            alpha   = 0.002,   # per-lionfish per-prey per-week predation rate
            beta    = 0.10,
            delta_l = 0.0004,
        ),
        disp_params      = DispersalParams(
            sigma            = 2.5,
            current_dir      = 0.0,     # east-ward drift
            current_strength = 0.40,
            max_dist         = 5,
            survival_rate    = 0.05,
        ),
        random_seed = args.seed,
    )

    # Run simulation
    model.run(verbose=True)

    # Generate plots
    if not args.no_plots:
        records = model.collector.records
        generate_all_plots(model, records)
        print("\nPlots saved to output/")


if __name__ == "__main__":
    main()
