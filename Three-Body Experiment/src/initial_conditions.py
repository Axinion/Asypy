"""Approximate circular starting states for the three-body experiments."""

import numpy as np


def center_system(
    masses: np.ndarray, positions: np.ndarray, velocities: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Place the initial center of mass at rest at the origin."""
    total_mass = masses.sum()
    center = np.sum(masses[:, None] * positions, axis=0) / total_mass
    center_velocity = np.sum(masses[:, None] * velocities, axis=0) / total_mass
    return positions - center, velocities - center_velocity


def sun_two_planets() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """A solar mass and two low-mass planets at radii 1 and 1.7."""
    masses = np.array((1.0, 1e-3, 1e-5))
    positions = np.array(((0.0, 0.0), (1.0, 0.0), (1.7, 0.0)))
    velocities = np.array(
        ((0.0, 0.0),
         (0.0, np.sqrt((masses[0] + masses[1]) / 1.0)),
         (0.0, np.sqrt((masses[0] + masses[2]) / 1.7)))
    )
    positions, velocities = center_system(masses, positions, velocities)
    return masses, positions, velocities


def binary_planet(planet_x: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Equal-mass circular binary with a light circumbinary planet."""
    if planet_x <= 0.5:
        raise ValueError("Place the planet outside the binary's right-hand star.")
    masses = np.array((1.0, 1.0, 1e-5))
    binary_speed = np.sqrt(2.0) / 2.0
    positions = np.array(((-0.5, 0.0), (0.5, 0.0), (planet_x, 0.0)))
    velocities = np.array(
        ((0.0, -binary_speed),
         (0.0, binary_speed),
         (0.0, np.sqrt(2.0 / planet_x)))
    )
    # Keep the requested x coordinates exact; remove only the system's net drift.
    center_velocity = np.sum(masses[:, None] * velocities, axis=0) / masses.sum()
    return masses, positions, velocities - center_velocity
