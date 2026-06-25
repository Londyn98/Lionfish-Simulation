"""
lionfish_agent.py
Individual lionfish agent with lifecycle: feeding, aging,
reproduction, and natural mortality.
"""

import random
from dataclasses import dataclass, field
from typing import Optional


# ── Biological constants (Albins & Hixon 2008; Côté et al. 2013) ─────────── #
MATURITY_AGE      = 8        # weeks before reproductive maturity
MAX_AGE           = 520      # ~10 years in weeks
NATURAL_MORTALITY = 0.004    # weekly probability of natural death (~2%/yr realistic)
PREDATION_RATE    = 0.025    # fraction of zone prey consumed per lionfish per week
SPAWN_INTERVAL    = 4        # weeks between spawning events
MEAN_CLUTCH       = 30       # mean larvae per spawn (zone-scale model)
ENERGY_THRESHOLD  = 0.10     # min prey ratio needed to reproduce


@dataclass
class LionfishAgent:
    """
    A single Pterois volitans individual.

    Parameters
    ----------
    agent_id  : unique integer identifier
    zone_id   : current reef zone
    age       : age in weeks (default 0 = newly settled juvenile)
    sex       : 'M' or 'F'
    """

    agent_id : int
    zone_id  : int
    age      : int   = 0
    sex      : str   = field(default_factory=lambda: random.choice(['M', 'F']))
    alive    : bool  = True
    _weeks_since_spawn: int = field(default=0, repr=False)

    # ------------------------------------------------------------------ #
    #  Properties                                                          #
    # ------------------------------------------------------------------ #

    @property
    def is_mature(self) -> bool:
        return self.age >= MATURITY_AGE

    # ------------------------------------------------------------------ #
    #  Per-step actions                                                    #
    # ------------------------------------------------------------------ #

    def feed(self, zone) -> float:
        """
        Lionfish feeds in zone.  Prey dynamics are handled by the
        Lotka-Volterra model at the zone level; this method records
        energy gain for the agent and returns a symbolic consumption value.
        """
        if not self.alive:
            return 0.0
        # Energy proxy: proportion of carrying capacity currently available
        return zone.prey_ratio() * PREDATION_RATE

    def attempt_reproduction(self, zone, next_id: int) -> list:
        """
        If mature, female, prey available, and spawn interval elapsed,
        produce a Poisson-distributed clutch of larvae.
        Returns list of new LionfishAgent objects (juveniles, same zone).
        """
        if not self.alive or not self.is_mature or self.sex != 'F':
            return []

        self._weeks_since_spawn += 1
        if self._weeks_since_spawn < SPAWN_INTERVAL:
            return []

        if zone.prey_ratio() < ENERGY_THRESHOLD:
            return []

        self._weeks_since_spawn = 0
        clutch_size = max(0, int(random.gauss(MEAN_CLUTCH, MEAN_CLUTCH * 0.3)))
        offspring = []
        for i in range(clutch_size):
            offspring.append(LionfishAgent(
                agent_id=next_id + i,
                zone_id=zone.zone_id,
                age=0
            ))
        return offspring

    def age_and_die(self) -> bool:
        """
        Age the agent by one week; apply stochastic natural mortality.
        Returns True if the agent died this step.
        """
        if not self.alive:
            return False
        self.age += 1
        if self.age > MAX_AGE or random.random() < NATURAL_MORTALITY:
            self.alive = False
            return True
        return False

    def __repr__(self):
        return (f"LionfishAgent(id={self.agent_id}, zone={self.zone_id}, "
                f"age={self.age}wk, sex={self.sex}, alive={self.alive})")
