# Integrator Comparison Experiment

This experiment compares forward Euler, Euler-Cromer, and leapfrog using the same circular-orbit setup. It also checks the numerical orbital period against \(2\pi\), then tests apsis speeds and Kepler's area law on an elliptical orbit.

| Folder | Contents |
| --- | --- |
| `src/` | Standalone integration core and experiment scripts |
| `reports/` | Predictions, measurements, and interpretation |
| `plots/` | Comparison and elliptical-orbit figures |
| `data/` | CSV samples for trajectories and swept areas |

Set up NumPy and Matplotlib from this folder:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Run both experiments:

```bash
.venv/bin/python src/method_comparison.py
.venv/bin/python src/elliptical_validation.py
```

The scripts save their outputs under this folder's `plots/` and `data/` directories. See [the report](reports/method_period_ellipse_report.md) for the results.
