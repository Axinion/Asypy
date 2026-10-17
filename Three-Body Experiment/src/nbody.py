"""Direct Newtonian N-body gravity with synchronized leapfrog updates."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class NBodyResult:
    times: np.ndarray
    masses: np.ndarray
    positions: np.ndarray  # (time, body, x/y)
    velocities: np.ndarray  # (time, body, vx/vy)
    energy: np.ndarray
    angular_momentum: np.ndarray
    total_momentum: np.ndarray  # (time, px/py)
    center_of_mass: np.ndarray  # (time, x/y)
    minimum_separation: np.ndarray


def accelerations(positions: np.ndarray, masses: np.ndarray, gravity: float) -> np.ndarray:
    """Calculate every acceleration from one shared position snapshot."""
    count = len(masses)
    result = np.zeros_like(positions)
    for i in range(count):
        for j in range(count):
            if i == j:
                continue
            displacement = positions[j] - positions[i]
            radius = np.linalg.norm(displacement)
            if radius < 1e-8:
                raise ValueError(f"Bodies {i} and {j} reached a close encounter (r < 1e-8).")
            result[i] += gravity * masses[j] * displacement / radius**3
    return result


def simulate_nbody(
    masses: np.ndarray,
    initial_positions: np.ndarray,
    initial_velocities: np.ndarray,
    *,
    gravity: float = 1.0,
    dt: float = 0.005,
    total_time: float = 30.0,
) -> NBodyResult:
    """Advance every body through synchronized kick-drift-kick steps."""
    masses = np.asarray(masses, dtype=float)
    initial_positions = np.asarray(initial_positions, dtype=float)
    initial_velocities = np.asarray(initial_velocities, dtype=float)
    count = len(masses)
    if count < 2 or initial_positions.shape != (count, 2) or initial_velocities.shape != (count, 2):
        raise ValueError("Provide at least two masses and matching (body, 2) position/velocity arrays.")
    if not all(np.all(np.isfinite(values)) for values in (masses, initial_positions, initial_velocities)):
        raise ValueError("Masses, positions, and velocities must be finite.")
    if np.any(masses <= 0) or min(gravity, dt, total_time) <= 0:
        raise ValueError("Masses, gravity, dt, and total_time must be positive.")

    steps = max(1, round(total_time / dt))
    step_size = total_time / steps
    times = np.linspace(0.0, total_time, steps + 1)
    positions = np.empty((steps + 1, count, 2), dtype=float)
    velocities = np.empty_like(positions)
    positions[0] = initial_positions
    velocities[0] = initial_velocities
    current_acceleration = accelerations(positions[0], masses, gravity)

    for step in range(steps):
        half_step_velocity = velocities[step] + 0.5 * step_size * current_acceleration
        positions[step + 1] = positions[step] + step_size * half_step_velocity
        next_acceleration = accelerations(positions[step + 1], masses, gravity)
        velocities[step + 1] = half_step_velocity + 0.5 * step_size * next_acceleration
        current_acceleration = next_acceleration

    kinetic = 0.5 * np.sum(masses[None, :] * np.sum(velocities**2, axis=2), axis=1)
    potential = np.zeros(steps + 1)
    minimum_separation = np.full(steps + 1, np.inf)
    for i in range(count):
        for j in range(i + 1, count):
            distance = np.linalg.norm(positions[:, j] - positions[:, i], axis=1)
            potential -= gravity * masses[i] * masses[j] / distance
            minimum_separation = np.minimum(minimum_separation, distance)

    angular_momentum = np.sum(
        masses[None, :]
        * (positions[:, :, 0] * velocities[:, :, 1]
           - positions[:, :, 1] * velocities[:, :, 0]),
        axis=1,
    )
    total_momentum = np.sum(masses[None, :, None] * velocities, axis=1)
    center_of_mass = np.sum(masses[None, :, None] * positions, axis=1) / masses.sum()
    return NBodyResult(
        times, masses, positions, velocities, kinetic + potential,
        angular_momentum, total_momentum, center_of_mass, minimum_separation,
    )
