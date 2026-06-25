"""
lotka_volterra.py
MODEL 1 — Extended Lotka-Volterra Predator-Prey System

Implements the coupled ODE system for lionfish (predator) and
native reef fish (prey), adapted from Albins & Hixon (2008).

  dP/dt = r_P * P * (1 - P/K_P) - alpha * P * L
  dL/dt = beta * alpha * P * L  - delta_L * L  + lambda_imm

Key adaptation: delta_L is very small (~0.02/yr) because
lionfish have no effective natural predators in Atlantic waters.
"""

from dataclasses import dataclass


@dataclass
class LotkaVolterraParams:
    """Biological parameters for the LV model."""
    r_prey:    float = 0.30    # prey intrinsic weekly growth rate
    k_prey:    float = 500.0   # prey carrying capacity per zone
    alpha:     float = 0.002   # predation rate (per lionfish per prey per week)
    beta:      float = 0.10    # lionfish conversion efficiency
    delta_l:   float = 0.0004  # lionfish natural mortality (weekly; ~2%/yr)


class LotkaVolterraModel:
    """
    Solves one discrete time step (Euler method, dt = 1 week) of the
    extended Lotka-Volterra system per reef zone.

    Parameters
    ----------
    params : LotkaVolterraParams
    """

    def __init__(self, params: LotkaVolterraParams | None = None):
        self.p = params or LotkaVolterraParams()

    # ------------------------------------------------------------------ #
    #  ODE right-hand sides                                               #
    # ------------------------------------------------------------------ #

    def dprey_dt(self, prey: float, lion: float) -> float:
        """Rate of change of prey population."""
        logistic_growth = self.p.r_prey * prey * (1.0 - prey / self.p.k_prey)
        predation_loss  = self.p.alpha * prey * lion
        return logistic_growth - predation_loss

    def dlion_dt(self, prey: float, lion: float,
                 lambda_imm: float = 0.0) -> float:
        """
        Rate of change of lionfish population.
        lambda_imm = larval immigration from dispersal model (larvae/week).
        """
        growth    = self.p.beta * self.p.alpha * prey * lion
        mortality = self.p.delta_l * lion
        return growth - mortality + lambda_imm

    # ------------------------------------------------------------------ #
    #  Step solver                                                         #
    # ------------------------------------------------------------------ #

    def solve_step(self, prey: float, lion: float,
                   lambda_imm: float = 0.0,
                   dt: float = 1.0) -> tuple[float, float]:
        """
        Advance one time step using Euler integration.

        Parameters
        ----------
        prey       : current prey population
        lion       : current lionfish density
        lambda_imm : larval immigration this step
        dt         : step size in weeks (default 1)

        Returns
        -------
        (new_prey, new_lion) — both clamped to >= 0
        """
        new_prey = prey + self.dprey_dt(prey, lion) * dt
        new_lion = lion + self.dlion_dt(prey, lion, lambda_imm) * dt
        return max(0.0, new_prey), max(0.0, new_lion)

    # ------------------------------------------------------------------ #
    #  Analytics                                                           #
    # ------------------------------------------------------------------ #

    def basic_reproduction_number(self, prey_init: float) -> float:
        """
        Compute R0 for lionfish: expected reproductive success
        when introduced into a fully healthy prey population.
        R0 = (beta * alpha * K_prey) / delta_L
        """
        if self.p.delta_l == 0:
            return float('inf')
        return (self.p.beta * self.p.alpha * prey_init) / self.p.delta_l

    def __repr__(self):
        p = self.p
        return (f"LotkaVolterraModel(r={p.r_prey}, K={p.k_prey}, "
                f"alpha={p.alpha}, beta={p.beta}, delta_L={p.delta_l})")
