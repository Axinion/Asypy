"""Run the five initial-speed experiments and save trajectory and energy plots."""

from math import sqrt
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from orbit_simulation import simulate_orbit


SPEEDS = (0.8, 1.0, 1.2, sqrt(2), 1.5)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT = PROJECT_ROOT / "plots" / "orbit_experiments.png"
ENERGY_OUTPUT = PROJECT_ROOT / "plots" / "orbit_experiments_energy.png"
ENERGY_DATA = PROJECT_ROOT / "data" / "orbit_experiments_energy.csv"


def main() -> None:
    fig, axes = plt.subplots(2, 3, figsize=(13, 8), constrained_layout=True)
    energy_fig, energy_ax = plt.subplots(figsize=(9, 5))
    energy_columns = []

    for speed, ax in zip(SPEEDS, axes.flat):
        times, positions, energies, _ = simulate_orbit(initial_velocity=(0.0, speed))
        if not energy_columns:
            energy_columns.append(times)
        energy_columns.append(energies)
        radii = np.linalg.norm(positions, axis=1)
        energy = energies[0]
        max_energy_change = np.max(np.abs(energies - energy))

        ax.plot(positions[:, 0], positions[:, 1], linewidth=1.4)
        ax.scatter(0, 0, s=65, color="gold", edgecolor="black", zorder=3)
        ax.scatter(*positions[0], s=30, color="red", zorder=3)
        ax.set(title=f"v₀ = {speed:.6g}, ε = {energy:+.3f}", xlabel="x", ylabel="y")
        ax.set_aspect("equal", adjustable="datalim")
        ax.grid(alpha=0.25)
        energy_ax.plot(times, energies, label=f"v₀ = {speed:.6g}")

        print(
            f"v0={speed:.9f}  energy={energy:+.9f}  "
            f"r_min={radii.min():.9f} at t={times[radii.argmin()]:.3f}  "
            f"r_max={radii.max():.9f} at t={times[radii.argmax()]:.3f}  "
            f"r_final={radii[-1]:.9f}  max_dE={max_energy_change:.3e}"
        )

    axes.flat[-1].axis("off")
    fig.savefig(OUTPUT, dpi=160)
    plt.close(fig)
    energy_ax.set(xlabel="Time", ylabel="Specific energy", title="Orbital Energy vs. Time")
    energy_ax.grid(alpha=0.3)
    energy_ax.legend()
    energy_fig.tight_layout()
    energy_fig.savefig(ENERGY_OUTPUT, dpi=160)
    plt.close(energy_fig)
    np.savetxt(
        ENERGY_DATA,
        np.column_stack(energy_columns),
        delimiter=",",
        header="time,E_v0_0.8,E_v0_1.0,E_v0_1.2,E_v0_sqrt2,E_v0_1.5",
        comments="",
        fmt="%.17g",
    )
    print(f"Saved {OUTPUT}, {ENERGY_OUTPUT}, and {ENERGY_DATA}")


if __name__ == "__main__":
    main()
