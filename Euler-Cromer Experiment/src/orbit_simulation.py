"""Simulate and plot a body orbiting a fixed central mass in two dimensions."""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PLOTS_DIR = PROJECT_ROOT / "plots"
DATA_DIR = PROJECT_ROOT / "data"


def acceleration(position: np.ndarray, gm: float) -> np.ndarray:
    """Return the gravitational acceleration at a position."""
    radius = np.linalg.norm(position)
    if radius == 0:
        raise ValueError("The orbiting body reached the central mass.")
    return -gm * position / radius**3


def specific_energy(position: np.ndarray, velocity: np.ndarray, gm: float) -> float:
    """Return kinetic plus gravitational potential energy per unit mass."""
    radius = np.linalg.norm(position)
    speed_squared = np.dot(velocity, velocity)
    kinetic = 0.5 * speed_squared
    potential = -gm / radius
    return kinetic + potential


def specific_angular_momentum(position: np.ndarray, velocity: np.ndarray) -> float:
    """Return the z component of angular momentum per unit mass."""
    x, y = position
    vx, vy = velocity
    return x * vy - y * vx


def simulate_orbit(
    gm: float = 1.0,
    dt: float = 0.001,
    total_time: float = 10.0,
    initial_position: tuple[float, float] = (1.0, 0.0),
    initial_velocity: tuple[float, float] = (0.0, 1.0),
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return aligned time, position, energy, and angular momentum samples."""
    if gm <= 0 or dt <= 0 or total_time <= 0:
        raise ValueError("gm, dt, and total_time must be positive.")

    steps = max(1, round(total_time / dt))
    step_size = total_time / steps
    times = np.linspace(0.0, total_time, steps + 1)
    positions = np.empty((steps + 1, 2), dtype=float)
    energies = np.empty(steps + 1, dtype=float)
    angular_momenta = np.empty(steps + 1, dtype=float)
    positions[0] = initial_position
    velocity = np.asarray(initial_velocity, dtype=float).copy()
    current_acceleration = acceleration(positions[0], gm)
    energies[0] = specific_energy(positions[0], velocity, gm)
    angular_momenta[0] = specific_angular_momentum(positions[0], velocity)

    for index in range(steps):
        positions[index + 1] = (
            positions[index]
            + velocity * step_size
            + 0.5 * current_acceleration * step_size**2
        )
        next_acceleration = acceleration(positions[index + 1], gm)
        velocity += 0.5 * (current_acceleration + next_acceleration) * step_size
        current_acceleration = next_acceleration
        energies[index + 1] = specific_energy(positions[index + 1], velocity, gm)
        angular_momenta[index + 1] = specific_angular_momentum(
            positions[index + 1], velocity
        )

    return times, positions, energies, angular_momenta


def plot_orbit(positions: np.ndarray, output: Path, show: bool = False) -> None:
    """Save the orbit plot, optionally displaying it as well."""
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.plot(positions[:, 0], positions[:, 1], label="Orbit")
    ax.scatter(0, 0, s=100, color="gold", edgecolor="black", label="Central mass")
    ax.scatter(*positions[0], s=45, color="red", zorder=3, label="Start")
    ax.set(xlabel="x", ylabel="y", title="2D Gravitational Orbit Simulation")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    if show:
        plt.show()
    plt.close(fig)


def plot_energy(times: np.ndarray, energies: np.ndarray, output: Path, show: bool = False) -> None:
    """Save specific orbital energy against time."""
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(times, energies, label="Simulated energy")
    ax.axhline(energies[0], color="black", linestyle="--", alpha=0.6, label="Initial energy")
    max_drift = np.max(np.abs(energies - energies[0]))
    half_range = max(1e-5, 1.2 * max_drift)
    ax.set_ylim(energies[0] - half_range, energies[0] + half_range)
    ax.set(xlabel="Time", ylabel="Specific energy", title="Orbital Energy vs. Time")
    ax.ticklabel_format(axis="y", useOffset=False)
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    if show:
        plt.show()
    plt.close(fig)


def plot_angular_momentum(
    times: np.ndarray, angular_momenta: np.ndarray, output: Path, show: bool = False
) -> None:
    """Save specific angular momentum against time."""
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(times, angular_momenta, label="Simulated angular momentum")
    ax.axhline(angular_momenta[0], color="black", linestyle="--", alpha=0.6, label="Initial value")
    max_drift = np.max(np.abs(angular_momenta - angular_momenta[0]))
    half_range = max(1e-5, 1.2 * max_drift)
    ax.set_ylim(angular_momenta[0] - half_range, angular_momenta[0] + half_range)
    ax.set(xlabel="Time", ylabel="Specific angular momentum", title="Angular Momentum vs. Time")
    ax.ticklabel_format(axis="y", useOffset=False)
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    if show:
        plt.show()
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gm", type=float, default=1.0, help="Gravitational parameter")
    parser.add_argument("--dt", type=float, default=0.001, help="Requested time step")
    parser.add_argument("--total-time", type=float, default=10.0, help="Simulation duration")
    parser.add_argument("--output", type=Path, default=PLOTS_DIR / "orbit.png", help="Plot filename")
    parser.add_argument("--energy-output", type=Path, default=PLOTS_DIR / "orbit_energy.png", help="Energy plot filename")
    parser.add_argument("--energy-data", type=Path, default=DATA_DIR / "orbit_energy.csv", help="Time and energy data filename")
    parser.add_argument("--momentum-output", type=Path, default=PLOTS_DIR / "orbit_angular_momentum.png", help="Angular momentum plot filename")
    parser.add_argument("--diagnostics-data", type=Path, default=DATA_DIR / "orbit_diagnostics.csv", help="Conservation diagnostics filename")
    parser.add_argument("--show", action="store_true", help="Display the plot after saving it")
    args = parser.parse_args()

    times, positions, energies, angular_momenta = simulate_orbit(
        args.gm, args.dt, args.total_time
    )
    plot_orbit(positions, args.output, args.show)
    plot_energy(times, energies, args.energy_output, args.show)
    plot_angular_momentum(times, angular_momenta, args.momentum_output, args.show)
    energy_change = energies - energies[0]
    relative_error = (
        energy_change / abs(energies[0])
        if abs(energies[0]) > 1e-14
        else np.full_like(energies, np.nan)
    )
    np.savetxt(
        args.energy_data,
        np.column_stack((times, energies)),
        delimiter=",",
        header="time,specific_energy",
        comments="",
        fmt="%.17g",
    )
    np.savetxt(
        args.diagnostics_data,
        np.column_stack((times, energies, energy_change, relative_error, angular_momenta)),
        delimiter=",",
        header="time,specific_energy,delta_energy,relative_energy_error,specific_angular_momentum",
        comments="",
        fmt="%.17g",
    )
    radii = np.linalg.norm(positions, axis=1)
    print(f"Saved orbit and diagnostics plots plus CSV data ({len(times)} samples, {times[-1]:g} time units)")
    print(f"Radius range: {radii.min():.6f} to {radii.max():.6f}")
    print(f"Initial specific energy: {energies[0]:+.9f}")
    print(f"Maximum absolute energy change: {np.max(np.abs(energies - energies[0])):.3e}")
    print(f"Maximum absolute angular momentum change: {np.max(np.abs(angular_momenta - angular_momenta[0])):.3e}")


if __name__ == "__main__":
    main()
