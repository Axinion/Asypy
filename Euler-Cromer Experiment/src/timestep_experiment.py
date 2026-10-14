"""Compare circular-orbit accuracy and conservation at three timesteps."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FormatStrFormatter

from orbit_simulation import simulate_orbit


TIMESTEPS = (0.1, 0.05, 0.01)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT = PROJECT_ROOT / "plots" / "timestep_conservation.png"
DATA_OUTPUT = PROJECT_ROOT / "data" / "timestep_conservation.csv"


def main() -> None:
    fig, axes = plt.subplots(2, 3, figsize=(15, 9), constrained_layout=True)
    trajectory_ax, radius_ax, energy_ax, delta_ax, relative_ax, momentum_ax = axes.flat
    data_rows = []
    largest_momentum_change = 0.0

    exact_times = np.linspace(0, 10, 2001)
    trajectory_ax.plot(np.cos(exact_times), np.sin(exact_times), "k--", label="Exact circle")

    for dt in TIMESTEPS:
        times, positions, energies, angular_momenta = simulate_orbit(dt=dt)
        radii = np.linalg.norm(positions, axis=1)
        energy_change = energies - energies[0]
        relative_error = energy_change / abs(energies[0])
        momentum_change = angular_momenta - angular_momenta[0]
        position_error = np.linalg.norm(
            positions - np.column_stack((np.cos(times), np.sin(times))), axis=1
        )
        largest_momentum_change = max(
            largest_momentum_change, np.max(np.abs(momentum_change))
        )
        label = f"Δt = {dt:g}"

        trajectory_ax.plot(positions[:, 0], positions[:, 1], label=label)
        radius_ax.plot(times, radii, label=label)
        energy_ax.plot(times, energies, label=label)
        delta_ax.plot(times, energy_change, label=label)
        relative_ax.plot(times, relative_error, label=label)
        momentum_ax.plot(times, angular_momenta, label=label)

        data_rows.append(
            np.column_stack(
                (
                    np.full_like(times, dt),
                    times,
                    radii,
                    energies,
                    energy_change,
                    relative_error,
                    angular_momenta,
                )
            )
        )
        print(
            f"dt={dt:g} steps={len(times)-1} "
            f"max_position_error={np.max(position_error):.9e} "
            f"max_radius_error={np.max(np.abs(radii - 1)):.9e} "
            f"max_abs_delta_E={np.max(np.abs(energy_change)):.9e} "
            f"max_abs_relative_E={np.max(np.abs(relative_error)):.9e} "
            f"max_abs_delta_h={np.max(np.abs(momentum_change)):.9e}"
        )

    trajectory_ax.set(title="Trajectory", xlabel="x", ylabel="y")
    trajectory_ax.set_aspect("equal", adjustable="box")
    radius_ax.set(title="Radius", xlabel="Time", ylabel="r(t)")
    energy_ax.set(title="Specific energy", xlabel="Time", ylabel="E(t)")
    energy_ax.yaxis.set_major_formatter(FormatStrFormatter("%.6f"))
    delta_ax.set(title="Energy change", xlabel="Time", ylabel="E(t) − E₀")
    relative_ax.set(title="Relative energy error", xlabel="Time", ylabel="[E(t) − E₀] / |E₀|")
    momentum_ax.set(title="Specific angular momentum", xlabel="Time", ylabel="h(t)")
    momentum_range = max(1e-13, 1.2 * largest_momentum_change)
    momentum_ax.set_ylim(1 - momentum_range, 1 + momentum_range)
    for ax in axes.flat:
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)

    fig.savefig(OUTPUT, dpi=160)
    plt.close(fig)
    np.savetxt(
        DATA_OUTPUT,
        np.vstack(data_rows),
        delimiter=",",
        header="dt,time,radius,specific_energy,delta_energy,relative_energy_error,specific_angular_momentum",
        comments="",
        fmt="%.17g",
    )
    print(f"Saved {OUTPUT} and {DATA_OUTPUT}")


if __name__ == "__main__":
    main()
