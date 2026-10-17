# Three-Body Experiment

Direct Newtonian gravity for any number of moving bodies in two dimensions. The three included experiments use a synchronized leapfrog (kick-drift-kick) integrator: every acceleration is computed from one complete position snapshot before the system advances.

## Run

From this folder, install the dependencies and run:

```sh
python3 -m pip install -r requirements.txt
python3 src/run_experiments.py
```

The script saves three figures in `plots/` and time-series CSV files in `data/`. It uses normalized units, `G = 1`, and a timestep of `0.005`. Experiments A and B run to `t = 30`; experiment C runs to `t = 40`.

## Experiments

| Experiment | Initial system | Main measurement |
| --- | --- | --- |
| A | Star of mass 1, planets of mass `1e-3` and `1e-5` | Trajectories, planet-star radii, energy error |
| B | Two stars of mass 1, planet of mass `1e-5` | Planet motion for starts at `x = 3.0` and `x = 1.5` |
| C | The binary and planet at `x₃ = 2.000` or `2.001` | Third-body separation `Δ(t)` |

The [report](reports/three_body_report.md) records physics-based predictions, measured results, and limits of the conclusions. `src/nbody.py` contains the reusable N-body integrator; `src/initial_conditions.py` defines the starting states; `src/run_experiments.py` produces the figures and CSV files.

Each full-run CSV contains time, each body's position and velocity, total energy, angular momentum, linear momentum, center of mass, and closest pair separation. The sensitivity CSV records both third-body trajectories and their separation.
