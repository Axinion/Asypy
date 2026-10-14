"""Check apsis speeds and Kepler's second law for an elliptical orbit."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FormatStrFormatter

from orbit_simulation import integrate_orbit


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PLOT = PROJECT_ROOT / "plots" / "elliptical_validation.png"
STATE_DATA = PROJECT_ROOT / "data" / "elliptical_orbit.csv"
AREA_DATA = PROJECT_ROOT / "data" / "swept_area.csv"
DT = 0.001
TOTAL_TIME = 10.0


def first_apsides(radii: np.ndarray) -> tuple[int, int]:
    """Find the first sampled periapsis and subsequent apoapsis."""
    minima = np.flatnonzero(
        (radii[1:-1] < radii[:-2]) & (radii[1:-1] <= radii[2:])
    ) + 1
    maxima = np.flatnonzero(
        (radii[1:-1] > radii[:-2]) & (radii[1:-1] >= radii[2:])
    ) + 1
    if len(minima) == 0 or not np.any(maxima > minima[0]):
        raise ValueError("The run must include a periapsis and a later apoapsis.")
    return int(minima[0]), int(maxima[maxima > minima[0]][0])


def main() -> None:
    result = integrate_orbit(
        dt=DT,
        total_time=TOTAL_TIME,
        initial_velocity=(0.0, 0.8),
        method="leapfrog",
    )
    radii = np.linalg.norm(result.positions, axis=1)
    speeds = np.linalg.norm(result.velocities, axis=1)
    peri_index, apo_index = first_apsides(radii)

    area_steps = 0.5 * np.abs(
        result.positions[:-1, 0] * result.positions[1:, 1]
        - result.positions[:-1, 1] * result.positions[1:, 0]
    )
    area_rates = area_steps / np.diff(result.times)
    area_times = 0.5 * (result.times[:-1] + result.times[1:])
    expected_rate = result.angular_momenta[0] / 2
    max_area_error = np.max(np.abs(area_rates - expected_rate))

    print(
        f"First periapsis: t={result.times[peri_index]:.3f}, "
        f"r={radii[peri_index]:.9f}, speed={speeds[peri_index]:.9f}"
    )
    print(
        f"Next apoapsis: t={result.times[apo_index]:.3f}, "
        f"r={radii[apo_index]:.9f}, speed={speeds[apo_index]:.9f}"
    )
    print(
        f"Area rate: expected={expected_rate:.9f}, "
        f"min={area_rates.min():.9f}, max={area_rates.max():.9f}, "
        f"max_abs_error={max_area_error:.3e}"
    )

    fig, axes = plt.subplots(2, 2, figsize=(12, 9), constrained_layout=True)
    trajectory_ax, radius_ax, speed_ax, area_ax = axes.flat
    trajectory_ax.plot(result.positions[:, 0], result.positions[:, 1], linewidth=1.2)
    trajectory_ax.scatter(0, 0, color="gold", edgecolor="black", s=60, label="Central mass")
    trajectory_ax.scatter(*result.positions[peri_index], color="red", s=40, label="First periapsis")
    trajectory_ax.scatter(*result.positions[apo_index], color="green", s=40, label="Next apoapsis")
    trajectory_ax.set(title="Elliptical trajectory", xlabel="x", ylabel="y")
    trajectory_ax.set_aspect("equal", adjustable="box")
    trajectory_ax.legend(fontsize=8)

    radius_ax.plot(result.times, radii)
    radius_ax.scatter(result.times[[peri_index, apo_index]], radii[[peri_index, apo_index]], c=["red", "green"])
    radius_ax.set(title="Radius and apsides", xlabel="Time", ylabel="r(t)")

    speed_ax.plot(result.times, speeds)
    speed_ax.scatter(result.times[[peri_index, apo_index]], speeds[[peri_index, apo_index]], c=["red", "green"])
    speed_ax.set(title="Speed at the apsides", xlabel="Time", ylabel="|v(t)|")

    area_ax.plot(area_times, area_rates, label="Triangle area / Δt")
    area_ax.axhline(expected_rate, color="black", linestyle="--", alpha=0.6, label="h₀ / 2")
    half_range = max(1e-6, 1.2 * max_area_error)
    area_ax.set_ylim(expected_rate - half_range, expected_rate + half_range)
    area_ax.yaxis.set_major_formatter(FormatStrFormatter("%.7f"))
    area_ax.set(title="Swept-area rate", xlabel="Time", ylabel="ΔA / Δt")
    area_ax.legend(fontsize=8)

    for ax in axes.flat:
        ax.grid(alpha=0.3)
    fig.savefig(PLOT, dpi=160)
    plt.close(fig)

    np.savetxt(
        STATE_DATA,
        np.column_stack((result.times, result.positions, result.velocities, radii, speeds, result.energies, result.angular_momenta)),
        delimiter=",",
        header="time,x,y,vx,vy,radius,speed,specific_energy,specific_angular_momentum",
        comments="",
        fmt="%.17g",
    )
    np.savetxt(
        AREA_DATA,
        np.column_stack((area_times, area_steps, area_rates)),
        delimiter=",",
        header="midpoint_time,triangle_area,area_rate",
        comments="",
        fmt="%.17g",
    )
    print(f"Saved {PLOT}, {STATE_DATA}, and {AREA_DATA}")


if __name__ == "__main__":
    main()
