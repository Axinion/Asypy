"""Euler-Cromer simulation of a one-dimensional mass-spring oscillator."""

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class SHMResult:
    time: np.ndarray
    position: np.ndarray
    velocity: np.ndarray
    analytic_position: np.ndarray
    kinetic_energy: np.ndarray
    potential_energy: np.ndarray
    total_energy: np.ndarray


def simulate_shm(
    mass: float = 1.0,
    spring_constant: float = 1.0,
    initial_position: float = 1.0,
    initial_velocity: float = 0.0,
    dt: float = 0.01,
    total_time: float = 20.0,
) -> SHMResult:
    """Advance velocity first, then position, and include the initial state."""
    values = np.array(
        (mass, spring_constant, initial_position, initial_velocity, dt, total_time),
        dtype=float,
    )
    if not np.all(np.isfinite(values)) or mass <= 0 or spring_constant <= 0 or dt <= 0 or total_time <= 0:
        raise ValueError("Parameters must be finite; mass, spring constant, dt, and total time must be positive.")

    steps = max(1, int(np.ceil(total_time / dt)))
    step_size = total_time / steps
    time = np.linspace(0.0, total_time, steps + 1)
    position = np.empty(steps + 1)
    velocity = np.empty(steps + 1)
    position[0], velocity[0] = initial_position, initial_velocity

    for index in range(steps):
        acceleration = -(spring_constant / mass) * position[index]
        velocity[index + 1] = velocity[index] + acceleration * step_size
        position[index + 1] = position[index] + velocity[index + 1] * step_size

    omega = np.sqrt(spring_constant / mass)
    analytic_position = (
        initial_position * np.cos(omega * time)
        + initial_velocity / omega * np.sin(omega * time)
    )
    kinetic_energy = 0.5 * mass * velocity**2
    potential_energy = 0.5 * spring_constant * position**2
    total_energy = kinetic_energy + potential_energy
    return SHMResult(
        time, position, velocity, analytic_position,
        kinetic_energy, potential_energy, total_energy,
    )


def save_results(result: SHMResult) -> None:
    """Write the numerical and analytical series and their energies to CSV."""
    data = np.column_stack(
        (
            result.time, result.position, result.velocity,
            result.analytic_position, result.position - result.analytic_position,
            result.kinetic_energy, result.potential_energy, result.total_energy,
        )
    )
    np.savetxt(
        ROOT / "data" / "shm_timeseries.csv",
        data,
        delimiter=",",
        header="time,position,velocity,analytic_position,position_error,kinetic_energy,potential_energy,total_energy",
        comments="",
        fmt="%.17g",
    )


def plot_results(result: SHMResult) -> None:
    """Save the trajectory comparison and energy-exchange plots."""
    figure, axis = plt.subplots(figsize=(10, 5), constrained_layout=True)
    axis.plot(result.time, result.analytic_position, label="Analytical: cos(t)", linewidth=2)
    axis.plot(result.time, result.position, label="Euler-Cromer", linestyle="--")
    axis.set(xlabel="Time", ylabel="Position x", title="Simple harmonic motion: numerical vs analytical")
    axis.grid(alpha=0.3)
    axis.legend()
    figure.savefig(ROOT / "plots" / "position_comparison.png", dpi=160)
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(10, 5), constrained_layout=True)
    axis.plot(result.time, result.kinetic_energy, label="Kinetic energy K")
    axis.plot(result.time, result.potential_energy, label="Potential energy U")
    axis.plot(result.time, result.total_energy, label="Total energy E", linewidth=2)
    axis.set(xlabel="Time", ylabel="Energy", title="Kinetic and potential energy exchange")
    axis.grid(alpha=0.3)
    axis.legend()
    figure.savefig(ROOT / "plots" / "energy_exchange.png", dpi=160)
    plt.close(figure)


def main() -> None:
    result = simulate_shm()
    save_results(result)
    plot_results(result)
    position_error = np.max(np.abs(result.position - result.analytic_position))
    energy_error = np.max(np.abs((result.total_energy - result.total_energy[0]) / result.total_energy[0]))
    print(f"Maximum |x_numerical - cos(t)|: {position_error:.6g}")
    print(f"Maximum relative total-energy change: {energy_error:.6g}")
    print(f"Saved plots and CSV data under {ROOT}")


if __name__ == "__main__":
    main()
