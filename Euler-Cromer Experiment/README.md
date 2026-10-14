# Orbit simulation experiments

This folder contains the orbit code, experiment reports, generated plots, and numerical data.

| Folder | Contents |
| --- | --- |
| `src/` | Simulation and experiment scripts |
| `reports/` | Physics predictions, results, and interpretation |
| `plots/` | Generated trajectory and conservation figures |
| `data/` | CSV samples for energy, angular momentum, and timestep comparisons |

Use a Python environment with NumPy and Matplotlib. To set one up from this folder:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Then run:

```bash
.venv/bin/python src/orbit_simulation.py
.venv/bin/python src/orbit_experiments.py
.venv/bin/python src/timestep_experiment.py
```

If your current Python already has those packages, `python3 src/orbit_simulation.py` and the other scripts work directly. Their default outputs go to `plots/` and `data/`, regardless of the shell's current directory.

The folder name is the requested experiment label. The current code uses **velocity Verlet**, which is a different integration method from Euler-Cromer. The reports describe the method actually used.
