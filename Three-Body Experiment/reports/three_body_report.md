# Direct three-body gravity experiments

## Method

Every body has a mass, two-dimensional position, velocity, and acceleration. For body \(i\), the code sums \(Gm_j(\mathbf r_j-\mathbf r_i)/|\mathbf r_j-\mathbf r_i|^3\) over all \(j\ne i\). Every acceleration comes from the same position snapshot. A kick-drift-kick leapfrog step then updates all velocities by half a step, all positions by a full step, recomputes all accelerations from the new positions, and finishes the velocity update. The code does not resolve physical collisions.

## Predictions before running

**A. Sun + two planets:** With masses \((1,10^{-3},10^{-5})\), planets initially at radii 1 and 1.7 should orbit mostly under the star's gravity. The planets also exert small mutual forces, so their paths need not be perfect independent Kepler circles.

**B. Binary star + planet:** Two stars of mass 1 start in an approximately circular binary of separation 1. A planet of mass \(10^{-5}\) starts outside them. A wider start should look more regular over this finite run; a closer start may show stronger distortions or a close encounter. A finite trajectory alone cannot establish permanent stability.

**C. Small perturbation:** Two binary-planet runs differ only in the third body's initial \(x\): 2.000 versus 2.001. The initial third-body separation is 0.001. I expect their trajectories to diverge with time, but growth alone is not proof of chaos; ordinary phase drift can also increase \(\Delta(t)\).

## Measured results

All runs use \(G=1\) and leapfrog steps of \(\Delta t=0.005\). A and B run to \(t=30\); C runs to \(t=40\). Positions and velocities for every body, along with conservation diagnostics, are saved in the linked CSV files.

### A. Sun + two planets

The inner planet's distance from the star ranged from **0.999871 to 1.000108**; the outer planet's ranged from **1.687974 to 1.700000**. The star moved around the system's center of mass on a scale of roughly \(10^{-3}\). The planets followed nearly circular paths, with small radial changes as all three bodies interacted. The minimum separation between any pair was **0.696031**. The maximum relative total-energy error was **\(1.55\times10^{-9}\)**.

**Prediction check:** Broadly correct. The star dominates both planets' motion, and the finite-mass planets perturb the shared system. The radius variations alone do not isolate how much came from mutual planetary gravity versus the approximate circular initial conditions, so this run should not be treated as a quantitative measurement of the planet-planet perturbation.

[A plot](../plots/experiment_a.png) · [A data](../data/experiment_a.csv)

### B. Binary star + planet

With the third body initially at \(x=3.0\), its distance from the binary center remained near **3** and ended at **2.958702**. With the third body initially at \(x=1.5\), its distance grew to **21.804043** by \(t=30\). The closest planet-star separation in the close-start run was **0.960499**. These are distinct outcomes from changing the starting position while keeping the masses and the binary-star setup fixed.

**Prediction check:** Correct over the simulated interval. The wider case looks regular; the closer case moves far outward after a strong disturbance. This finite run does not prove permanent stability for the wide case or establish the close case's final asymptotic fate. Maximum relative total-energy errors were **\(6.23\times10^{-10}\)** (wide) and **\(7.04\times10^{-10}\)** (close).

[B plot](../plots/experiment_b.png) · [Wide-start data](../data/experiment_b_wide.csv) · [Close-start data](../data/experiment_b_close.csv)

### C. Small perturbation

Only the third body's initial \(x\) coordinate differs: **2.000** versus **2.001**. Its trajectory separation \(\Delta(t)\) started at **0.001000**, reached **0.047285** at \(t=40\), and attained a maximum of **0.057516** during the run. The two curves still look similar on a whole-orbit plot, while the separation graph resolves their difference.

**Prediction check:** Correct that the separation grows. This demonstrates sensitivity to a small initial change in this setup, but it is **not** by itself evidence of chaos or exponential divergence. Phase drift between nearby orbits can produce the observed growth.

[C plot](../plots/experiment_c.png) · [C data](../data/experiment_c_sensitivity.csv)

## Numerical validation and limits

For an isolated Newtonian system, total energy, total angular momentum, and total linear momentum should be conserved. In A, the largest relative angular-momentum change was approximately **\(4.1\times10^{-15}\)** and the largest linear-momentum magnitude was approximately **\(9.5\times10^{-18}\)**; its energy error is reported above. The very small drift supports the numerical implementation over this interval. The code stops if two bodies approach within \(10^{-8}\), rather than modeling collisions. Long-term stability and close encounters require longer runs and timestep-convergence checks.
