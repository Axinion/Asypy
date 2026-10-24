# Simple Harmonic Motion Experiment

This experiment integrates a one-dimensional mass-spring oscillator with Euler-Cromer, compares its position with the exact solution, and tracks kinetic, potential, and total energy.

The default parameters are `m = 1`, `k = 1`, `x₀ = 1`, `v₀ = 0`, `dt = 0.01`, and a duration of 20 time units. Thus `a = -x`, `ω = 1`, and the analytical position is `x(t) = cos(t)`.

## Run

From this folder:

```sh
python3 -m pip install -r requirements.txt
python3 src/shm.py
```

The script saves [the position comparison](plots/position_comparison.png), [the energy plot](plots/energy_exchange.png), and [the full time series](data/shm_timeseries.csv). The [report](reports/shm_report.md) records the prediction, measurements, and interpretation. To try another setup, call `simulate_shm` with different parameters from Python.
