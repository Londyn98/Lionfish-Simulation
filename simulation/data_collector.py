"""
data_collector.py
Records per-step simulation metrics and exports to CSV and JSON.

Tracked metrics
---------------
- Total lionfish population
- Mean prey population across all zones
- Spread radius (farthest colonised zone from origin)
- Zone counts by health state (Healthy / Degraded / Collapsed)
- Lionfish R0 estimate
- Prey depletion rate (delta P / delta t)
"""

import csv
import json
import math
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .simulation_model import SimulationModel


class DataCollector:
    """
    Collects and persists simulation metrics.

    Parameters
    ----------
    output_dir : str  path to write CSV and JSON output
    origin     : tuple (x, y)  seed zone coordinates for spread radius calc
    """

    def __init__(self, output_dir: str = "output", origin: tuple = (0, 0)):
        self.output_dir   = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.origin       = origin
        self.records: list[dict] = []
        self._prev_mean_prey: float | None = None

    # ------------------------------------------------------------------ #
    #  Per-step recording                                                  #
    # ------------------------------------------------------------------ #

    def record_step(self, step: int, model) -> dict:
        """
        Capture all metrics for the current simulation step.
        Returns the record dict for immediate use (e.g. printing).
        """
        zones = list(model.zones.values())

        total_lion  = sum(z.lionfish_density for z in zones)
        mean_prey   = sum(z.prey_population  for z in zones) / len(zones)
        n_healthy   = sum(1 for z in zones if z.health_state.value == "Healthy")
        n_degraded  = sum(1 for z in zones if z.health_state.value == "Degraded")
        n_collapsed = sum(1 for z in zones if z.health_state.value == "Collapsed")
        spread_r    = self._spread_radius(zones)
        n_colonised = sum(1 for z in zones if z.is_colonised())

        # Prey depletion rate (change since last step)
        if self._prev_mean_prey is not None:
            depletion_rate = self._prev_mean_prey - mean_prey
        else:
            depletion_rate = 0.0
        self._prev_mean_prey = mean_prey

        record = {
            "step":           step,
            "total_lionfish": round(total_lion, 2),
            "mean_prey":      round(mean_prey, 2),
            "spread_radius":  round(spread_r, 2),
            "zones_colonised": n_colonised,
            "zones_healthy":  n_healthy,
            "zones_degraded": n_degraded,
            "zones_collapsed": n_collapsed,
            "prey_depletion_rate": round(depletion_rate, 4),
            "total_agents":   len([a for a in model.agents if a.alive]),
        }
        self.records.append(record)
        return record

    # ------------------------------------------------------------------ #
    #  Spread radius calculation                                           #
    # ------------------------------------------------------------------ #

    def _spread_radius(self, zones) -> float:
        """Distance (in grid cells) from origin to farthest colonised zone."""
        ox, oy = self.origin
        max_d  = 0.0
        for z in zones:
            if z.is_colonised():
                d = math.sqrt((z.x - ox)**2 + (z.y - oy)**2)
                if d > max_d:
                    max_d = d
        return max_d

    # ------------------------------------------------------------------ #
    #  Export                                                              #
    # ------------------------------------------------------------------ #

    def export_csv(self, filename: str = "metrics.csv"):
        """Write all records to a CSV file."""
        if not self.records:
            return
        path = self.output_dir / filename
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.records[0].keys())
            writer.writeheader()
            writer.writerows(self.records)
        print(f"[DataCollector] CSV written → {path}")

    def export_json(self, filename: str = "metrics.json"):
        """Write all records to a JSON file."""
        path = self.output_dir / filename
        with open(path, "w") as f:
            json.dump(self.records, f, indent=2)
        print(f"[DataCollector] JSON written → {path}")

    # ------------------------------------------------------------------ #
    #  Quick summary                                                       #
    # ------------------------------------------------------------------ #

    def summary(self) -> str:
        if not self.records:
            return "No data recorded."
        last = self.records[-1]
        first = self.records[0]
        return (
            f"Steps recorded : {len(self.records)}\n"
            f"Final lionfish : {last['total_lionfish']}\n"
            f"Final mean prey: {last['mean_prey']}\n"
            f"Spread radius  : {last['spread_radius']} cells\n"
            f"Zones colonised: {last['zones_colonised']}\n"
            f"Health states  : "
            f"H={last['zones_healthy']} "
            f"D={last['zones_degraded']} "
            f"C={last['zones_collapsed']}\n"
            f"Prey Δ (total) : "
            f"{first['mean_prey'] - last['mean_prey']:.1f} fish/zone"
        )
