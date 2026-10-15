# Two-Body Orbit Experiment

Both masses move under their mutual gravitational force. The simulation uses kick-drift-kick leapfrog and starts them on opposite sides of their shared center of mass.

The default setup is \(G=1\), \(m_1=1\), \(m_2=0.001\), initial separation 1, timestep 0.001, and total time 10. Both trajectories and conservation diagnostics are saved to `plots/` and `data/`.

Set up dependencies and run from this folder:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python src/two_body_orbit.py
```

You can vary the setup, for example:

```bash
.venv/bin/python src/two_body_orbit.py --m1 1 --m2 0.01 --dt 0.001 --total-time 10
```

See [the report](reports/two_body_report.md) for the equations and measured results.
