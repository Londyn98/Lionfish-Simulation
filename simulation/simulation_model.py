"""
simulation_model.py
Central simulation controller.

Orchestrates the weekly time-step loop:
  1. Spawning
  2. Larval dispersal
  3. Predation (agent-level)
  4. Prey logistic growth (Lotka-Volterra)
  5. Reef health update
  6. Optional culling
  7. Natural mortality
  8. Data collection
"""

import random
from .reef_zone       import ReefZone
from .lionfish_agent  import LionfishAgent
from .lotka_volterra  import LotkaVolterraModel, LotkaVolterraParams
from .dispersal_model import DispersalModel, DispersalParams
from .data_collector  import DataCollector


class SimulationModel:
    """
    Lionfish invasion simulation.

    Parameters
    ----------
    grid_w, grid_h   : grid dimensions (zones)
    n_seed_lionfish  : initial lionfish count placed at origin
    seed_zone        : (x, y) of the invasion origin zone
    total_steps      : number of weekly steps to run
    culling_enabled  : whether culling interventions are active
    culling_rate     : fraction of lionfish removed per cull event
    culling_interval : weeks between cull events
    lv_params        : LotkaVolterraParams (optional)
    disp_params      : DispersalParams (optional)
    prey_init_scale  : multiplier on K_prey for initial prey population
    random_seed      : for reproducibility
    """

    def __init__(
        self,
        grid_w: int            = 10,
        grid_h: int            = 8,
        n_seed_lionfish: int   = 5,
        seed_zone: tuple       = (0, 4),
        total_steps: int       = 104,       # 2 years
        culling_enabled: bool  = False,
        culling_rate: float    = 0.60,
        culling_interval: int  = 12,
        lv_params              = None,
        disp_params            = None,
        prey_init_scale: float = 0.80,
        random_seed: int | None = 42,
    ):
        if random_seed is not None:
            random.seed(random_seed)

        self.grid_w          = grid_w
        self.grid_h          = grid_h
        self.total_steps     = total_steps
        self.current_step    = 0
        self.culling_enabled  = culling_enabled
        self.culling_rate     = culling_rate
        self.culling_interval = culling_interval
        self.seed_zone        = seed_zone

        # Sub-models
        self.lv_model   = LotkaVolterraModel(lv_params or LotkaVolterraParams())
        self.disp_model = DispersalModel(grid_w, grid_h, disp_params or DispersalParams())
        self.collector  = DataCollector(origin=seed_zone)

        # State
        self.zones: dict[tuple, ReefZone] = {}
        self.agents: list[LionfishAgent]  = []
        self._next_agent_id: int          = 0

        self._build_grid(prey_init_scale)
        self._build_zone_id_map()
        self._seed_lionfish(n_seed_lionfish)

    # ------------------------------------------------------------------ #
    #  Initialisation                                                      #
    # ------------------------------------------------------------------ #

    def _build_grid(self, prey_scale: float):
        """Create ReefZone objects for every cell in the grid."""
        zone_id = 0
        for x in range(self.grid_w):
            for y in range(self.grid_h):
                k_prey    = random.uniform(350, 650)   # heterogeneous capacity
                prey_init = k_prey * prey_scale
                self.zones[(x, y)] = ReefZone(
                    zone_id  = zone_id,
                    x=x, y=y,
                    prey_init  = prey_init,
                    prey_k     = k_prey,
                )
                zone_id += 1

    def _seed_lionfish(self, n: int):
        """Place initial lionfish agents at the seed zone."""
        sx, sy = self.seed_zone
        zone   = self.zones[(sx, sy)]
        for _ in range(n):
            agent = LionfishAgent(
                agent_id = self._next_agent_id,
                zone_id  = zone.zone_id,
                age      = random.randint(8, 52),   # already mature
            )
            self.agents.append(agent)
            self._next_agent_id += 1
        zone.lionfish_density = float(n)

    # ------------------------------------------------------------------ #
    #  Main loop                                                           #
    # ------------------------------------------------------------------ #

    def run(self, verbose: bool = True):
        """Run the full simulation for total_steps weeks."""
        print(f"\n{'='*55}")
        print(f"  Lionfish Invasion Simulation")
        print(f"  Grid: {self.grid_w}x{self.grid_h}  |  Steps: {self.total_steps}")
        print(f"  Culling: {'ON' if self.culling_enabled else 'OFF'}")
        print(f"{'='*55}\n")

        for step in range(self.total_steps):
            self.current_step = step
            self._step(step)
            if verbose and (step % 8 == 0 or step < 10):
                r = self.collector.records[-1]
                print(f"  Week {step:>4} | "
                      f"Lion: {r['total_lionfish']:>9,.0f} | "
                      f"Prey: {r['mean_prey']:>7.1f} | "
                      f"Spread: {r['spread_radius']:>5.1f} cells | "
                      f"Zones: {r['zones_colonised']:>3} | "
                      f"H/D/C: {r['zones_healthy']}/{r['zones_degraded']}/{r['zones_collapsed']}")

        self.collector.export_csv()
        self.collector.export_json()
        print(f"\n{'='*55}")
        print("  Simulation complete.\n")
        print(self.collector.summary())
        print(f"{'='*55}\n")

    def _step(self, step: int):
        """Execute one weekly time step."""

        # 1. Spawning & larval production
        pending_larvae: dict[tuple, int] = {}   # {(x,y): n_larvae}
        new_agents: list[LionfishAgent]  = []

        for agent in self.agents:
            if not agent.alive:
                continue
            zone = self._zone_of(agent)
            offspring = agent.attempt_reproduction(zone, self._next_agent_id)
            if offspring:
                self._next_agent_id += len(offspring)
                # Offspring disperse rather than staying in place
                src_x, src_y = zone.x, zone.y
                n_larvae      = len(offspring)
                settled       = self.disp_model.disperse_larvae(src_x, src_y, n_larvae)
                for (dx, dy), count in settled.items():
                    pending_larvae[(dx, dy)] = pending_larvae.get((dx, dy), 0) + count

        # 2. Settle dispersed larvae as new juvenile agents
        for (dest_x, dest_y), count in pending_larvae.items():
            dest_zone = self.zones.get((dest_x, dest_y))
            if dest_zone is None:
                continue
            for _ in range(count):
                juv = LionfishAgent(
                    agent_id = self._next_agent_id,
                    zone_id  = dest_zone.zone_id,  # correct zone_id
                    age      = 0,
                )
                new_agents.append(juv)
                self._next_agent_id += 1

        self.agents.extend(new_agents)

        # 3. Predation — each live agent feeds in its zone
        for agent in self.agents:
            if agent.alive:
                agent.feed(self._zone_of(agent))

        # 4. Prey logistic growth (Lotka-Volterra per zone)
        for zone in self.zones.values():
            new_prey, _ = self.lv_model.solve_step(
                prey       = zone.prey_population,
                lion       = zone.lionfish_density,
                lambda_imm = 0.0,
            )
            zone.prey_population = min(new_prey, zone.prey_carrying_cap)

        # 5. Reef health transitions
        for zone in self.zones.values():
            zone.update_health()

        # 6. Culling
        if self.culling_enabled and step > 0 and step % self.culling_interval == 0:
            self._apply_culling()

        # 7. Natural mortality & recompute zone densities
        self.agents = [a for a in self.agents if not a.age_and_die()]
        self._update_zone_densities()

        # 8. Data collection
        self.collector.record_step(step, self)

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def _build_zone_id_map(self):
        """Build a fast zone_id -> (x,y) lookup."""
        self._zone_id_map = {z.zone_id: pos for pos, z in self.zones.items()}

    def _zone_of(self, agent: LionfishAgent) -> ReefZone:
        """Return the ReefZone containing this agent (by zone_id)."""
        pos = self._zone_id_map.get(agent.zone_id)
        if pos:
            return self.zones[pos]
        return self.zones[self.seed_zone]

    def _update_zone_densities(self):
        """Recount live agents per zone and update lionfish_density."""
        counts: dict = {pos: 0.0 for pos in self.zones}
        zone_id_map  = {z.zone_id: pos for pos, z in self.zones.items()}
        for agent in self.agents:
            if agent.alive:
                pos = zone_id_map.get(agent.zone_id)
                if pos:
                    counts[pos] += 1
        for pos, zone in self.zones.items():
            zone.lionfish_density = counts[pos]

    def _apply_culling(self):
        """Remove a fraction of live lionfish agents from all zones."""
        to_cull = [a for a in self.agents
                   if a.alive and random.random() < self.culling_rate]
        removed = 0
        for agent in to_cull:
            agent.alive = False
            removed += 1
        if removed:
            self._update_zone_densities()
            print(f"  [Culling] Week {self.current_step}: {removed} lionfish removed.")

    def get_grid_snapshot(self) -> dict:
        """
        Return current state of all zones as a dict keyed by (x, y).
        Useful for visualization.
        """
        return {
            pos: {
                "lionfish_density": zone.lionfish_density,
                "prey_population":  zone.prey_population,
                "health_state":     zone.health_state.value,
                "prey_ratio":       zone.prey_ratio(),
            }
            for pos, zone in self.zones.items()
        }
