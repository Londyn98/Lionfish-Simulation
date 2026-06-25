"""
reef_zone.py
Represents a single spatial cell in the reef grid.
Each zone tracks its prey population, lionfish density,
carrying capacity, and ecological health state.
"""

from enum import Enum


class HealthState(Enum):
    HEALTHY   = "Healthy"
    DEGRADED  = "Degraded"
    COLLAPSED = "Collapsed"


# Prey depletion thresholds that trigger health transitions
THETA_1 = 0.50   # below 50% of K_prey  -> Degraded
THETA_2 = 0.20   # below 20% of K_prey  -> Collapsed
PHI     = 2.0    # lionfish density below this allows recovery
TAU     = 12     # minimum weeks before a Collapsed zone can recover


class ReefZone:
    """
    A single reef cell on the simulation grid.

    Attributes
    ----------
    zone_id : int
    x, y    : int   grid coordinates
    prey_population    : float  current native prey fish count
    prey_carrying_cap  : float  maximum sustainable prey count
    lionfish_density   : float  current lionfish count in this zone
    health_state       : HealthState
    weeks_collapsed    : int    how long this zone has been Collapsed
    """

    def __init__(self, zone_id: int, x: int, y: int,
                 prey_init: float, prey_k: float):
        self.zone_id           = zone_id
        self.x                 = x
        self.y                 = y
        self.prey_population   = prey_init
        self.prey_carrying_cap = prey_k
        self.lionfish_density  = 0.0
        self.health_state      = HealthState.HEALTHY
        self.weeks_collapsed   = 0

    # ------------------------------------------------------------------ #
    #  Health state machine                                                #
    # ------------------------------------------------------------------ #

    def update_health(self):
        """Transition health state based on current prey depletion."""
        ratio = self.prey_population / self.prey_carrying_cap

        if self.health_state == HealthState.HEALTHY:
            if ratio < THETA_1:
                self.health_state = HealthState.DEGRADED

        elif self.health_state == HealthState.DEGRADED:
            if ratio < THETA_2:
                self.health_state   = HealthState.COLLAPSED
                self.weeks_collapsed = 0
            elif ratio >= THETA_1 and self.lionfish_density < PHI:
                # Prey recovering and pressure low — zone heals
                self.health_state = HealthState.HEALTHY

        elif self.health_state == HealthState.COLLAPSED:
            self.weeks_collapsed += 1
            if (self.lionfish_density == 0
                    and self.weeks_collapsed >= TAU
                    and ratio >= THETA_2):
                self.health_state = HealthState.DEGRADED

    # ------------------------------------------------------------------ #
    #  Convenience                                                         #
    # ------------------------------------------------------------------ #

    def is_colonised(self) -> bool:
        """True if at least one lionfish is present."""
        return self.lionfish_density > 0

    def prey_ratio(self) -> float:
        return self.prey_population / self.prey_carrying_cap

    def __repr__(self):
        return (f"ReefZone(id={self.zone_id}, pos=({self.x},{self.y}), "
                f"prey={self.prey_population:.1f}, "
                f"lion={self.lionfish_density:.2f}, "
                f"health={self.health_state.value})")
