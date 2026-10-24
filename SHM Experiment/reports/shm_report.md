# Simple Harmonic Motion: Euler-Cromer Experiment

## Initial conditions and prediction

With \(m=k=1\), \(x_0=1\), and \(v_0=0\), the acceleration is \(a=-x\) and the angular frequency is \(\omega=\sqrt{k/m}=1\). The exact solution is \(x(t)=\cos t\), with period \(2\pi\). I expect the Euler-Cromer position to follow an approximately sinusoidal curve close to \(\cos t\).

At \(t=0\), all energy is spring potential energy: \(K_0=0\), \(U_0=\tfrac12 kx_0^2=0.5\). As the mass passes the equilibrium point, potential energy should fall while kinetic energy rises. Their sum should stay nearly constant. Euler-Cromer has a finite timestep, so small total-energy oscillations are expected.

## Method

At each step, calculate \(a_n=-(k/m)x_n\), then \(v_{n+1}=v_n+a_n\Delta t\), then \(x_{n+1}=x_n+v_{n+1}\Delta t\). The initial state is saved as sample zero. This run uses \(\Delta t=0.01\) through \(t=20\). At each saved state, calculate \(K=\tfrac12 mv^2\), \(U=\tfrac12 kx^2\), and \(E=K+U\).

## Results

The numerical position closely follows \(\cos t\) through a little more than three periods. Across the 2,001 saved samples, the largest absolute position difference was **0.005072**. Halving the timestep to \(0.005\) reduced that maximum difference to **0.002518**, as expected when refining the numerical approximation.

Kinetic and spring potential energy alternate: when one approaches its maximum, the other approaches zero. The initial values are \(K_0=0\), \(U_0=0.5\), and \(E_0=0.5\). Numerical total energy ranged from **0.497512** to **0.502513**, with a maximum relative change from its initial value of **0.005025**, or about **0.50%**. The small bounded oscillation reflects Euler-Cromer's finite-step error; the plot shows no sustained energy drift over this interval.

**Prediction check:** Yes. The displacement is approximately sinusoidal and agrees closely with the analytical solution. Energy moves between kinetic and potential forms while their sum remains nearly constant.

[Numerical and analytical position plot](../plots/position_comparison.png) · [Energy plot](../plots/energy_exchange.png) · [Time-series data](../data/shm_timeseries.csv)
