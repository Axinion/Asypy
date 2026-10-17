"""Run the three direct-gravity N-body experiments and save their results."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from initial_conditions import binary_planet, sun_two_planets
from nbody import NBodyResult, simulate_nbody


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PLOTS = PROJECT_ROOT / "plots"
DATA = PROJECT_ROOT / "data"
DT = 0.005


def save_run(result: NBodyResult, output: Path) -> None:
    """Save every body's position and velocity plus system diagnostics."""
    count = len(result.masses)
    columns = np.column_stack(
        (
            result.times,
            result.positions.reshape(len(result.times), -1),
            result.velocities.reshape(len(result.times), -1),
            result.energy,
            result.angular_momentum,
            result.total_momentum,
            result.center_of_mass,
            result.minimum_separation,
        )
    )
    position_names = [name for i in range(count) for name in (f"x{i+1}", f"y{i+1}")]
    velocity_names = [name for i in range(count) for name in (f"vx{i+1}", f"vy{i+1}")]
    header = ",".join(
        ["time", *position_names, *velocity_names,
         "energy", "angular_momentum", "px", "py", "com_x", "com_y", "minimum_separation"]
    )
    np.savetxt(output, columns, delimiter=",", header=header, comments="", fmt="%.17g")


def relative_energy_error(result: NBodyResult) -> np.ndarray:
    return (result.energy - result.energy[0]) / abs(result.energy[0])


def planet_radius_from_binary(result: NBodyResult) -> np.ndarray:
    star_masses = result.masses[:2]
    star_center = np.sum(
        star_masses[None, :, None] * result.positions[:, :2], axis=1
    ) / star_masses.sum()
    return np.linalg.norm(result.positions[:, 2] - star_center, axis=1)


def plot_a(result: NBodyResult) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(12, 9), constrained_layout=True)
    orbit_ax, star_ax, radius_ax, energy_ax = axes.flat
    for index, label in enumerate(("Star", "Planet 1", "Planet 2")):
        orbit_ax.plot(*result.positions[:, index].T, label=label)
    orbit_ax.set(title="A: star and two planets", xlabel="x", ylabel="y")
    orbit_ax.set_aspect("equal", adjustable="box")
    orbit_ax.legend()

    star_ax.plot(*result.positions[:, 0].T)
    star_ax.set(title="Star's motion (zoomed)", xlabel="x", ylabel="y")
    star_ax.set_aspect("equal", adjustable="box")
    star_ax.ticklabel_format(axis="both", style="sci", scilimits=(-3, -3))

    for index, label in ((1, "Planet 1"), (2, "Planet 2")):
        radius = np.linalg.norm(result.positions[:, index] - result.positions[:, 0], axis=1)
        radius_ax.plot(result.times, radius, label=label)
    radius_ax.set(title="Planet distance from star", xlabel="Time", ylabel="Distance")
    radius_ax.legend()

    energy_ax.plot(result.times, relative_energy_error(result))
    energy_ax.set(title="Total-energy error", xlabel="Time", ylabel="(E − E₀) / |E₀|")
    for ax in axes.flat:
        ax.grid(alpha=0.3)
    fig.savefig(PLOTS / "experiment_a.png", dpi=160)
    plt.close(fig)


def plot_b(wide: NBodyResult, close: NBodyResult) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(12, 9), constrained_layout=True)
    for ax, result, title in (
        (axes[0, 0], wide, "B: planet starts at x = 3.0"),
        (axes[0, 1], close, "B: planet starts at x = 1.5"),
    ):
        for index, label in enumerate(("Star 1", "Star 2", "Planet")):
            ax.plot(*result.positions[:, index].T, label=label)
        ax.set(title=title, xlabel="x", ylabel="y")
        ax.set_aspect("equal", adjustable="box")
        ax.legend(fontsize=8)

    for result, label in ((wide, "x = 3.0"), (close, "x = 1.5")):
        axes[1, 0].plot(result.times, planet_radius_from_binary(result), label=label)
        planet_to_stars = np.linalg.norm(
            result.positions[:, :2] - result.positions[:, 2, None, :], axis=2
        )
        axes[1, 1].plot(result.times, planet_to_stars.min(axis=1), label=label)
    axes[1, 0].set(title="Planet distance from binary center", xlabel="Time", ylabel="Distance")
    axes[1, 1].set(title="Closest planet–star separation", xlabel="Time", ylabel="Distance")
    for ax in axes.flat:
        ax.grid(alpha=0.3)
    for ax in axes[1]:
        ax.legend()
    fig.savefig(PLOTS / "experiment_b.png", dpi=160)
    plt.close(fig)


def plot_c(baseline: NBodyResult, perturbed: NBodyResult, delta: np.ndarray) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(9, 9), constrained_layout=True)
    axes[0].plot(*baseline.positions[:, 2].T, label="x₃(0) = 2.000")
    axes[0].plot(*perturbed.positions[:, 2].T, label="x₃(0) = 2.001", alpha=0.8)
    axes[0].set(title="C: third-body trajectories", xlabel="x", ylabel="y")
    axes[0].set_aspect("equal", adjustable="box")
    axes[0].legend()

    axes[1].semilogy(baseline.times, delta)
    axes[1].axhline(delta[0], color="black", linestyle="--", alpha=0.5)
    axes[1].set(title="Separation between the two third-body trajectories", xlabel="Time", ylabel="Δ(t)")
    for ax in axes:
        ax.grid(alpha=0.3)
    fig.savefig(PLOTS / "experiment_c.png", dpi=160)
    plt.close(fig)


def main() -> None:
    masses_a, positions_a, velocities_a = sun_two_planets()
    a = simulate_nbody(masses_a, positions_a, velocities_a, dt=DT, total_time=30.0)
    save_run(a, DATA / "experiment_a.csv")
    plot_a(a)
    print(
        f"A: min pair separation={a.minimum_separation.min():.6f}, "
        f"max relative energy error={np.max(np.abs(relative_energy_error(a))):.3e}"
    )

    masses_w, positions_w, velocities_w = binary_planet(3.0)
    wide = simulate_nbody(masses_w, positions_w, velocities_w, dt=DT, total_time=30.0)
    masses_c, positions_c, velocities_c = binary_planet(1.5)
    close = simulate_nbody(masses_c, positions_c, velocities_c, dt=DT, total_time=30.0)
    save_run(wide, DATA / "experiment_b_wide.csv")
    save_run(close, DATA / "experiment_b_close.csv")
    plot_b(wide, close)
    print(
        f"B wide: final planet radius={planet_radius_from_binary(wide)[-1]:.6f}; "
        f"B close: final planet radius={planet_radius_from_binary(close)[-1]:.6f}"
    )

    masses_p, positions_p, velocities_p = binary_planet(2.0)
    shifted_positions = positions_p.copy()
    shifted_positions[2, 0] += 0.001  # Only the third body's initial x changes.
    baseline = simulate_nbody(masses_p, positions_p, velocities_p, dt=DT, total_time=40.0)
    perturbed = simulate_nbody(masses_p, shifted_positions, velocities_p, dt=DT, total_time=40.0)
    delta = np.linalg.norm(baseline.positions[:, 2] - perturbed.positions[:, 2], axis=1)
    np.savetxt(
        DATA / "experiment_c_sensitivity.csv",
        np.column_stack((baseline.times, baseline.positions[:, 2], perturbed.positions[:, 2], delta)),
        delimiter=",", fmt="%.17g", comments="",
        header="time,x3_baseline,y3_baseline,x3_perturbed,y3_perturbed,delta",
    )
    plot_c(baseline, perturbed, delta)
    print(f"C: Δ(0)={delta[0]:.6f}, Δ(40)={delta[-1]:.6f}, max Δ={delta.max():.6f}")
    print(f"Saved plots and CSV data under {PROJECT_ROOT}")


if __name__ == "__main__":
    main()
