"""Compare three orbit integrators and estimate the circular orbital period."""

import csv
from math import pi
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from orbit_simulation import integrate_orbit


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PLOT = PROJECT_ROOT / "plots" / "method_comparison.png"
DATA = PROJECT_ROOT / "data" / "method_comparison.csv"
METHODS = (
    ("forward_euler", "Forward Euler"),
    ("euler_cromer", "Euler-Cromer"),
    ("leapfrog", "Leapfrog (velocity Verlet)"),
)
DT = 0.05
TOTAL_TIME = 20.0


def first_revolution_time(times: np.ndarray, positions: np.ndarray) -> float:
    """Interpolate the first crossing of 2π in unwrapped polar angle."""
    angles = np.unwrap(np.arctan2(positions[:, 1], positions[:, 0]))
    target = angles[0] + 2 * pi
    crossing = np.searchsorted(angles, target)
    if crossing == 0 or crossing == len(angles):
        raise ValueError("The simulated orbit did not complete one revolution.")
    fraction = (target - angles[crossing - 1]) / (
        angles[crossing] - angles[crossing - 1]
    )
    return times[crossing - 1] + fraction * (
        times[crossing] - times[crossing - 1]
    )


def main() -> None:
    fig, axes = plt.subplots(2, 2, figsize=(12, 9), constrained_layout=True)
    trajectory_ax, radius_ax, energy_ax, momentum_ax = axes.flat
    exact_times = np.linspace(0, TOTAL_TIME, 4001)
    trajectory_ax.plot(np.cos(exact_times), np.sin(exact_times), "k--", label="Exact circle")

    with DATA.open("w", newline="") as data_file:
        writer = csv.writer(data_file, lineterminator="\n")
        writer.writerow(("method", "time", "x", "y", "vx", "vy", "radius", "specific_energy", "specific_angular_momentum"))

        for method, label in METHODS:
            result = integrate_orbit(dt=DT, total_time=TOTAL_TIME, method=method)
            radii = np.linalg.norm(result.positions, axis=1)
            period = first_revolution_time(result.times, result.positions)
            period_error = abs(period - 2 * pi) / (2 * pi)
            max_radius_error = np.max(np.abs(radii - 1))
            max_energy_change = np.max(np.abs(result.energies - result.energies[0]))
            max_momentum_change = np.max(
                np.abs(result.angular_momenta - result.angular_momenta[0])
            )

            trajectory_ax.plot(result.positions[:, 0], result.positions[:, 1], label=label)
            radius_ax.plot(result.times, radii, label=label)
            energy_ax.plot(result.times, result.energies, label=label)
            momentum_ax.plot(result.times, result.angular_momenta, label=label)

            for time, position, velocity, radius, energy, momentum in zip(
                result.times,
                result.positions,
                result.velocities,
                radii,
                result.energies,
                result.angular_momenta,
            ):
                writer.writerow((method, time, *position, *velocity, radius, energy, momentum))

            print(
                f"{label}: steps={len(result.times)-1}, "
                f"max|r-1|={max_radius_error:.9e}, "
                f"max|E-E0|={max_energy_change:.9e}, "
                f"max|h-h0|={max_momentum_change:.9e}, "
                f"T_num={period:.9f}, relative_period_error={period_error:.9e}"
            )

    trajectory_ax.set(title="Trajectory", xlabel="x", ylabel="y")
    trajectory_ax.set_aspect("equal", adjustable="box")
    radius_ax.set(title="Radius", xlabel="Time", ylabel="r(t)")
    energy_ax.set(title="Specific energy", xlabel="Time", ylabel="E(t)")
    momentum_ax.set(title="Specific angular momentum", xlabel="Time", ylabel="h(t)")
    radius_ax.axhline(1, color="black", linestyle="--", alpha=0.5)
    energy_ax.axhline(-0.5, color="black", linestyle="--", alpha=0.5)
    momentum_ax.axhline(1, color="black", linestyle="--", alpha=0.5)
    for ax in axes.flat:
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
    fig.savefig(PLOT, dpi=160)
    plt.close(fig)
    print(f"Saved {PLOT} and {DATA}")


if __name__ == "__main__":
    main()
