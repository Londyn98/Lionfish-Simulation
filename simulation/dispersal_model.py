"""
dispersal_model.py
MODEL 2 — Reaction-Diffusion Larval Dispersal

Models the spatial spread of lionfish larvae via ocean currents,
based on Cowen et al. (2006) and Okubo & Levin (2001).

Larvae released during spawning drift according to a directional
dispersal kernel and settle in destination reef zones.

The discrete dispersal kernel is:
    w_{i',j'} proportional to exp(-d / sigma) * current_bias(direction)

where d is grid distance and sigma is the mean dispersal scale.
"""

import random
import math
from dataclasses import dataclass, field


@dataclass
class DispersalParams:
    """Parameters controlling larval dispersal."""
    sigma:           float = 2.5    # dispersal length scale (grid cells)
    current_dir:     float = 0.0    # dominant current direction (radians; 0 = east)
    current_strength: float = 0.4   # bias strength [0 = isotropic, 1 = fully directed]
    max_dist:        int   = 5      # maximum dispersal distance (grid cells)
    survival_rate:   float = 0.35   # fraction of larvae settling (zone-scale model)


class DispersalModel:
    """
    Computes larval dispersal weights from a source zone to all
    reachable destination zones, then distributes larvae accordingly.

    Parameters
    ----------
    params : DispersalParams
    grid_w : int  grid width
    grid_h : int  grid height
    """

    def __init__(self, grid_w: int, grid_h: int,
                 params: DispersalParams | None = None):
        self.grid_w = grid_w
        self.grid_h = grid_h
        self.p      = params or DispersalParams()

    # ------------------------------------------------------------------ #
    #  Kernel computation                                                  #
    # ------------------------------------------------------------------ #

    def _dispersal_weight(self, dx: int, dy: int) -> float:
        """
        Compute unnormalised weight for dispersal offset (dx, dy).
        Combines an isotropic Gaussian decay with a directional bias
        aligned to the prevailing current.
        """
        dist = math.sqrt(dx**2 + dy**2)
        if dist == 0 or dist > self.p.max_dist:
            return 0.0

        # Isotropic decay
        gaussian = math.exp(-dist / self.p.sigma)

        # Directional current bias
        if dist > 0:
            angle    = math.atan2(dy, dx)
            alignment = math.cos(angle - self.p.current_dir)
            bias     = 1.0 + self.p.current_strength * alignment
        else:
            bias = 1.0

        return gaussian * bias

    def compute_kernel(self, src_x: int, src_y: int) -> dict:
        """
        Return a dict of {(dest_x, dest_y): probability} for all
        reachable destination cells from (src_x, src_y).
        Probabilities are normalised to sum to 1.
        """
        raw = {}
        r = self.p.max_dist
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                dest_x = src_x + dx
                dest_y = src_y + dy
                if 0 <= dest_x < self.grid_w and 0 <= dest_y < self.grid_h:
                    w = self._dispersal_weight(dx, dy)
                    if w > 0:
                        raw[(dest_x, dest_y)] = w

        total = sum(raw.values())
        if total == 0:
            return {}
        return {k: v / total for k, v in raw.items()}

    # ------------------------------------------------------------------ #
    #  Dispersal execution                                                 #
    # ------------------------------------------------------------------ #

    def disperse_larvae(self, src_x: int, src_y: int,
                        n_larvae: int) -> dict:
        """
        Distribute n_larvae from source zone to destination zones.

        Returns
        -------
        dict {(dest_x, dest_y): int n_settled}
        Only surviving larvae (survival_rate applied) are returned.
        """
        surviving = int(round(n_larvae * self.p.survival_rate))
        if surviving == 0:
            return {}

        kernel = self.compute_kernel(src_x, src_y)
        if not kernel:
            return {}

        destinations = list(kernel.keys())
        weights      = list(kernel.values())

        settled: dict = {}
        for _ in range(surviving):
            dest = random.choices(destinations, weights=weights, k=1)[0]
            settled[dest] = settled.get(dest, 0) + 1

        return settled

    # ------------------------------------------------------------------ #
    #  Analytical wave speed (Okubo & Levin 2001, Ch. 8)                  #
    # ------------------------------------------------------------------ #

    def invasion_wave_speed(self, r_lion: float) -> float:
        """
        Theoretical minimum wave speed:  c* = 2 * sqrt(D * r_lion)
        where D is approximated from sigma^2 / 2.
        """
        D = (self.p.sigma ** 2) / 2.0
        return 2.0 * math.sqrt(D * r_lion)

    def __repr__(self):
        return (f"DispersalModel(sigma={self.p.sigma}, "
                f"max_dist={self.p.max_dist}, "
                f"survival={self.p.survival_rate})")
