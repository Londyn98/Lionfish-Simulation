"""
visualizer.py
Produces plots for the lionfish invasion simulation.

Charts generated
----------------
1. Population time series   — lionfish vs prey over time
2. Reef health area chart   — H / D / C zone counts over time
3. Spread radius over time  — how far the invasion has reached
4. Grid heatmap (snapshot)  — lionfish density across the reef grid
"""

import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")            # headless — no display required
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import numpy as np


# ── Colour palette (matches project theme) ─────────────────────────────────
C_LION    = "#CC5500"   # lionorange
C_PREY    = "#22783C"   # reefgreen
C_HEALTH  = "#005B96"   # oceanblue
C_DEGRADE = "#E07B00"
C_COLLAPSE= "#8B0000"
C_BG      = "#F5F5F5"


def load_metrics(json_path: str = "output/metrics.json") -> list[dict]:
    with open(json_path) as f:
        return json.load(f)


def plot_population_timeseries(records: list[dict],
                                out_path: str = "output/plot_populations.png"):
    """Chart 1 — Lionfish vs Prey population over time."""
    steps = [r["step"] for r in records]
    lion  = [r["total_lionfish"] for r in records]
    prey  = [r["mean_prey"]      for r in records]

    fig, ax1 = plt.subplots(figsize=(10, 5), facecolor=C_BG)
    ax2 = ax1.twinx()

    ax1.plot(steps, lion, color=C_LION,  lw=2.0, label="Total Lionfish")
    ax2.plot(steps, prey, color=C_PREY,  lw=2.0, linestyle="--", label="Mean Prey / Zone")

    ax1.set_xlabel("Week", fontsize=12)
    ax1.set_ylabel("Lionfish Count",      color=C_LION,  fontsize=11)
    ax2.set_ylabel("Mean Prey Population", color=C_PREY, fontsize=11)
    ax1.tick_params(axis="y", labelcolor=C_LION)
    ax2.tick_params(axis="y", labelcolor=C_PREY)

    handles = [
        mpatches.Patch(color=C_LION, label="Total Lionfish"),
        mpatches.Patch(color=C_PREY, label="Mean Prey / Zone"),
    ]
    ax1.legend(handles=handles, loc="upper left", fontsize=10)
    ax1.set_title("Lionfish vs Native Prey Population Over Time", fontsize=14, pad=12)
    ax1.set_facecolor(C_BG)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"[Visualizer] Saved → {out_path}")


def plot_reef_health(records: list[dict],
                     out_path: str = "output/plot_reef_health.png"):
    """Chart 2 — Stacked area chart of zone health states."""
    steps     = [r["step"]            for r in records]
    healthy   = [r["zones_healthy"]   for r in records]
    degraded  = [r["zones_degraded"]  for r in records]
    collapsed = [r["zones_collapsed"] for r in records]

    fig, ax = plt.subplots(figsize=(10, 5), facecolor=C_BG)
    ax.stackplot(steps,
                 healthy, degraded, collapsed,
                 labels=["Healthy", "Degraded", "Collapsed"],
                 colors=[C_HEALTH, C_DEGRADE, C_COLLAPSE],
                 alpha=0.85)

    ax.set_xlabel("Week", fontsize=12)
    ax.set_ylabel("Number of Reef Zones", fontsize=11)
    ax.set_title("Reef Health State Distribution Over Time", fontsize=14, pad=12)
    ax.legend(loc="upper right", fontsize=10)
    ax.set_facecolor(C_BG)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"[Visualizer] Saved → {out_path}")


def plot_spread_radius(records: list[dict],
                       out_path: str = "output/plot_spread_radius.png"):
    """Chart 3 — Invasion spread radius over time."""
    steps  = [r["step"]         for r in records]
    radius = [r["spread_radius"] for r in records]
    coloni = [r["zones_colonised"] for r in records]

    fig, ax1 = plt.subplots(figsize=(10, 5), facecolor=C_BG)
    ax2 = ax1.twinx()

    ax1.plot(steps, radius, color=C_LION,   lw=2.0, label="Spread Radius (cells)")
    ax2.plot(steps, coloni, color="#7B3FBE", lw=1.5, linestyle=":", label="Zones Colonised")

    ax1.set_xlabel("Week", fontsize=12)
    ax1.set_ylabel("Spread Radius (grid cells)", color=C_LION,   fontsize=11)
    ax2.set_ylabel("Zones Colonised",             color="#7B3FBE", fontsize=11)
    ax1.tick_params(axis="y", labelcolor=C_LION)
    ax2.tick_params(axis="y", labelcolor="#7B3FBE")

    handles = [
        mpatches.Patch(color=C_LION,    label="Spread Radius"),
        mpatches.Patch(color="#7B3FBE", label="Zones Colonised"),
    ]
    ax1.legend(handles=handles, loc="upper left", fontsize=10)
    ax1.set_title("Spatial Invasion Spread Over Time", fontsize=14, pad=12)
    ax1.set_facecolor(C_BG)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"[Visualizer] Saved → {out_path}")


def plot_grid_heatmap(snapshot: dict,
                      grid_w: int, grid_h: int,
                      step: int,
                      out_path: str = "output/plot_heatmap.png"):
    """
    Chart 4 — Spatial heatmap of lionfish density.

    Parameters
    ----------
    snapshot : dict keyed by (x, y) from model.get_grid_snapshot()
    """
    lion_grid   = np.zeros((grid_h, grid_w))
    health_grid = np.zeros((grid_h, grid_w))   # 0=Healthy 1=Degraded 2=Collapsed

    health_map = {"Healthy": 0, "Degraded": 1, "Collapsed": 2}

    for (x, y), data in snapshot.items():
        lion_grid[y][x]   = data["lionfish_density"]
        health_grid[y][x] = health_map.get(data["health_state"], 0)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), facecolor=C_BG)

    # — Lionfish density heatmap
    cmap_lion = mcolors.LinearSegmentedColormap.from_list(
        "lion", ["#F5F5F5", "#FFD580", "#CC5500", "#5C1A00"])
    im1 = axes[0].imshow(lion_grid, cmap=cmap_lion, aspect="auto",
                          origin="lower", interpolation="nearest")
    fig.colorbar(im1, ax=axes[0], label="Lionfish Count")
    axes[0].set_title(f"Lionfish Density (Week {step})", fontsize=13)
    axes[0].set_xlabel("Grid X (Coastal Position)")
    axes[0].set_ylabel("Grid Y (Depth / Latitude)")

    # — Health state heatmap
    cmap_health = mcolors.ListedColormap([C_HEALTH, C_DEGRADE, C_COLLAPSE])
    im2 = axes[1].imshow(health_grid, cmap=cmap_health, aspect="auto",
                          origin="lower", interpolation="nearest",
                          vmin=0, vmax=2)
    cbar2 = fig.colorbar(im2, ax=axes[1], ticks=[0, 1, 2])
    cbar2.ax.set_yticklabels(["Healthy", "Degraded", "Collapsed"])
    axes[1].set_title(f"Reef Health State (Week {step})", fontsize=13)
    axes[1].set_xlabel("Grid X (Coastal Position)")
    axes[1].set_ylabel("Grid Y (Depth / Latitude)")

    for ax in axes:
        ax.set_facecolor(C_BG)

    fig.suptitle("Lionfish Invasion — Spatial Grid Snapshot", fontsize=15, y=1.01)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[Visualizer] Saved → {out_path}")


def generate_all_plots(model, records: list[dict]):
    """Convenience: generate all four charts from a finished model run."""
    plot_population_timeseries(records)
    plot_reef_health(records)
    plot_spread_radius(records)
    plot_grid_heatmap(
        snapshot = model.get_grid_snapshot(),
        grid_w   = model.grid_w,
        grid_h   = model.grid_h,
        step     = model.current_step,
    )
