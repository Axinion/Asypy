"""Simulate two moving masses interacting through Newtonian gravity."""

import argparse
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class TwoBodyResult:
    times: np.ndarray
    positions: np.ndarray  # (time, body, x/y)
    velocities: np.ndarray  # (time, body, vx/vy)
    separation: np.ndarray
    energy: np.ndarray
    angular_momentum: np.ndarray
    total_momentum: np.ndarray  # (time, px/py)
    center_of_mass: np.ndarray  # (time, x/y)


def accelerations(positions: np.ndarray, masses: np.ndarray, gravity: float) -> np.ndarray:
    """Compute both accelerations from the same separation vector."""
    delta = positions[1] - positions[0]
    radius = np.linalg.norm(delta)
    if radius == 0:
        raise ValueError("The bodies occupy the same position.")
    a1 = gravity * masses[1] * delta / radius**3
    a2 = -gravity * masses[0] * delta / radius**3
    return np.stack((a1, a2))


def circular_barycentric_state(
    m1: float, m2: float, gravity: float, separation: float
) -> tuple[np.ndarray, np.ndarray]:
    """Start both masses on opposite sides of a stationary barycenter."""
    total_mass = m1 + m2
    angular_speed = np.sqrt(gravity * total_mass / separation**3)
    positions = np.array(
        [[-m2 / total_mass * separation, 0.0], [m1 / total_mass * separation, 0.0]]
    )
    velocities = np.array(
        [[0.0, -angular_speed * m2 / total_mass * separation],
         [0.0, angular_speed * m1 / total_mass * separation]]
    )
    return positions, velocities


def simulate_two_body(
    m1: float = 1.0,
    m2: float = 0.001,
    gravity: float = 1.0,
    separation: float = 1.0,
    dt: float = 0.001,
    total_time: float = 10.0,
) -> TwoBodyResult:
    """Advance both bodies with kick-drift-kick leapfrog."""
    if min(m1, m2, gravity, separation, dt, total_time) <= 0:
        raise ValueError("Masses, gravity, separation, dt, and total_time must be positive.")

    steps = max(1, round(total_time / dt))
    step_size = total_time / steps
    times = np.linspace(0.0, total_time, steps + 1)
    masses = np.array((m1, m2))
    positions = np.empty((steps + 1, 2, 2), dtype=float)
    velocities = np.empty_like(positions)
    positions[0], velocities[0] = circular_barycentric_state(
        m1, m2, gravity, separation
    )
    current_acceleration = accelerations(positions[0], masses, gravity)

    for index in range(steps):
        half_step_velocity = velocities[index] + 0.5 * step_size * current_acceleration
        positions[index + 1] = positions[index] + step_size * half_step_velocity
        next_acceleration = accelerations(positions[index + 1], masses, gravity)
        velocities[index + 1] = half_step_velocity + 0.5 * step_size * next_acceleration
        current_acceleration = next_acceleration

    delta = positions[:, 1] - positions[:, 0]
    radii = np.linalg.norm(delta, axis=1)
    kinetic = 0.5 * np.sum(masses[None, :] * np.sum(velocities**2, axis=2), axis=1)
    energy = kinetic - gravity * m1 * m2 / radii
    angular_momentum = np.sum(
        masses[None, :]
        * (positions[:, :, 0] * velocities[:, :, 1]
           - positions[:, :, 1] * velocities[:, :, 0]),
        axis=1,
    )
    total_momentum = np.sum(masses[None, :, None] * velocities, axis=1)
    center_of_mass = np.sum(masses[None, :, None] * positions, axis=1) / masses.sum()
    return TwoBodyResult(
        times, positions, velocities, radii, energy,
        angular_momentum, total_momentum, center_of_mass,
    )


def save_plot(result: TwoBodyResult, output: Path) -> None:
    """Show both trajectories and numerical conservation checks."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 9), constrained_layout=True)
    orbit_ax, star_ax, separation_ax, energy_ax = axes.flat
    orbit_ax.plot(*result.positions[:, 0].T, label="Body 1 (heavier)")
    orbit_ax.plot(*result.positions[:, 1].T, label="Body 2 (lighter)")
    orbit_ax.scatter(0, 0, color="black", s=15, label="Barycenter")
    orbit_ax.set(title="Both bodies orbit the barycenter", xlabel="x", ylabel="y")
    orbit_ax.set_aspect("equal", adjustable="box")
    orbit_ax.legend()

    star_ax.plot(*result.positions[:, 0].T, color="C0")
    star_ax.scatter(0, 0, color="black", s=15)
    star_ax.set(title="Zoom: heavier body's motion", xlabel="x", ylabel="y")
    star_ax.set_aspect("equal", adjustable="box")
    star_ax.ticklabel_format(axis="both", style="sci", scilimits=(-3, -3))

    separation_ax.plot(result.times, result.separation)
    separation_ax.set(title="Distance between bodies", xlabel="Time", ylabel="Separation")
    separation_ax.ticklabel_format(axis="y", useOffset=False)

    relative_energy_error = (result.energy - result.energy[0]) / abs(result.energy[0])
    energy_ax.plot(result.times, relative_energy_error)
    energy_ax.set(title="Relative total-energy error", xlabel="Time", ylabel="(E − E₀) / |E₀|")

    for ax in axes.flat:
        ax.grid(alpha=0.3)
    fig.savefig(output, dpi=160)
    plt.close(fig)


def save_data(result: TwoBodyResult, output: Path) -> None:
    """Save both bodies' states and diagnostics at every timestep."""
    columns = np.column_stack(
        (
            result.times,
            result.positions[:, 0], result.positions[:, 1],
            result.velocities[:, 0], result.velocities[:, 1],
            result.separation, result.energy, result.angular_momentum,
            result.total_momentum, result.center_of_mass,
        )
    )
    np.savetxt(
        output, columns, delimiter=",", fmt="%.17g", comments="",
        header="time,x1,y1,x2,y2,vx1,vy1,vx2,vy2,separation,energy,angular_momentum,px,py,com_x,com_y",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--m1", type=float, default=1.0)
    parser.add_argument("--m2", type=float, default=0.001)
    parser.add_argument("--gravity", type=float, default=1.0)
    parser.add_argument("--separation", type=float, default=1.0)
    parser.add_argument("--dt", type=float, default=0.001)
    parser.add_argument("--total-time", type=float, default=10.0)
    args = parser.parse_args()

    result = simulate_two_body(
        args.m1, args.m2, args.gravity, args.separation, args.dt, args.total_time
    )
    plot_path = PROJECT_ROOT / "plots" / "two_body_orbit.png"
    data_path = PROJECT_ROOT / "data" / "two_body_orbit.csv"
    save_plot(result, plot_path)
    save_data(result, data_path)

    initial_center = result.center_of_mass[0]
    print(f"Saved {plot_path} and {data_path} ({len(result.times)} samples)")
    print(f"Max separation change: {np.max(np.abs(result.separation - result.separation[0])):.3e}")
    print(f"Max relative energy error: {np.max(np.abs((result.energy - result.energy[0]) / result.energy[0])):.3e}")
    print(f"Max angular momentum change: {np.max(np.abs(result.angular_momentum - result.angular_momentum[0])):.3e}")
    print(f"Max center-of-mass drift: {np.max(np.linalg.norm(result.center_of_mass - initial_center, axis=1)):.3e}")
    print(f"Max total momentum: {np.max(np.linalg.norm(result.total_momentum, axis=1)):.3e}")


if __name__ == "__main__":
    main()
