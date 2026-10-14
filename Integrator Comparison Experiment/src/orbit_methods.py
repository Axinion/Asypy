"""Integrate a 2D Kepler orbit with three explicit numerical methods."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class OrbitHistory:
    """Position, velocity, and invariants sampled at matching times."""

    times: np.ndarray
    positions: np.ndarray
    velocities: np.ndarray
    energies: np.ndarray
    angular_momenta: np.ndarray


def acceleration(position: np.ndarray, gm: float) -> np.ndarray:
    radius = np.linalg.norm(position)
    if radius == 0:
        raise ValueError("The orbiting body reached the central mass.")
    return -gm * position / radius**3


def specific_energy(position: np.ndarray, velocity: np.ndarray, gm: float) -> float:
    return 0.5 * np.dot(velocity, velocity) - gm / np.linalg.norm(position)


def specific_angular_momentum(position: np.ndarray, velocity: np.ndarray) -> float:
    x, y = position
    vx, vy = velocity
    return x * vy - y * vx


def integrate_orbit(
    gm: float = 1.0,
    dt: float = 0.001,
    total_time: float = 10.0,
    initial_position: tuple[float, float] = (1.0, 0.0),
    initial_velocity: tuple[float, float] = (0.0, 1.0),
    method: str = "leapfrog",
) -> OrbitHistory:
    """Return a complete trajectory using one selected integration method."""
    if gm <= 0 or dt <= 0 or total_time <= 0:
        raise ValueError("gm, dt, and total_time must be positive.")
    if method not in {"forward_euler", "euler_cromer", "leapfrog"}:
        raise ValueError(f"Unknown integration method: {method}")

    steps = max(1, round(total_time / dt))
    step_size = total_time / steps
    times = np.linspace(0.0, total_time, steps + 1)
    positions = np.empty((steps + 1, 2), dtype=float)
    velocities = np.empty((steps + 1, 2), dtype=float)
    energies = np.empty(steps + 1, dtype=float)
    angular_momenta = np.empty(steps + 1, dtype=float)
    positions[0] = initial_position
    velocities[0] = initial_velocity
    current_acceleration = acceleration(positions[0], gm)
    energies[0] = specific_energy(positions[0], velocities[0], gm)
    angular_momenta[0] = specific_angular_momentum(positions[0], velocities[0])

    for index in range(steps):
        if method == "forward_euler":
            positions[index + 1] = positions[index] + velocities[index] * step_size
            velocities[index + 1] = velocities[index] + current_acceleration * step_size
            current_acceleration = acceleration(positions[index + 1], gm)
        elif method == "euler_cromer":
            velocities[index + 1] = velocities[index] + current_acceleration * step_size
            positions[index + 1] = positions[index] + velocities[index + 1] * step_size
            current_acceleration = acceleration(positions[index + 1], gm)
        else:
            positions[index + 1] = (
                positions[index]
                + velocities[index] * step_size
                + 0.5 * current_acceleration * step_size**2
            )
            next_acceleration = acceleration(positions[index + 1], gm)
            velocities[index + 1] = velocities[index] + 0.5 * (
                current_acceleration + next_acceleration
            ) * step_size
            current_acceleration = next_acceleration

        energies[index + 1] = specific_energy(
            positions[index + 1], velocities[index + 1], gm
        )
        angular_momenta[index + 1] = specific_angular_momentum(
            positions[index + 1], velocities[index + 1]
        )

    return OrbitHistory(times, positions, velocities, energies, angular_momenta)
