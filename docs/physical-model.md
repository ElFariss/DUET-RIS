# Physical model and applicability

This project evaluates optimizer feasibility in a **measurement-informed simulation**. It contains no electromagnetic unit-cell solver and no measured mixed-pattern hardware validation.

## Transfer convention

`G[n,m]` is the BS-antenna-to-cell complex voltage gain; `H[k,n]` is the cell-to-user gain; `D[k,m]` is the direct gain. Paths share one geometry and carrier frequency. No matrix is independently normalized to unit variance.

For fixed precoder `W` and bits `b`, the effective stream matrix is

```
U[k,j] = (D W)[k,j]
       + Σ_n H[k,n] Γ[n,b[n]] (G W)[n,j] · 4πA/λ².
```

`A = 0.020 × 0.013 m²`. Each propagation loss and the chosen complex response enter once. The scalar aperture factor converts the two isotropic antenna gains into an approximate cell scattering amplitude; it does not model a measured bistatic element pattern. Coordinates are in metres. Sionna uses explicit singleton antenna probes, not a synthetic far-field panel array. The panel itself is not an occluding scene mesh.

The reference effective channel is the all-OFF configuration. Regularized zero forcing is calculated from that reference once per episode, normalized to 0.1 W total BS power, then kept fixed across candidate patterns and controllers. Using only the direct channel would incorrectly assign zero transmitted streams to users with blocked direct paths; the reference-channel construction avoids that failure.

Per-user desired power is `|U[k,k]|²`; interference sums `|U[k,j]|²` for `j != k`. Noise is 290 K thermal noise over 1 MHz with 7 dB noise figure. The objective is `min_k log2(1 + SINR_k)`.

## Frequency and phase

Nominal frequency is 5.53 GHz. Sionna represents it as 5,529,999,872 Hz in float32. The saved metadata records both. `paths.cir(normalize_delays=False)` already includes the carrier phase; do not apply it again. Exported DeepMIMO interaction phases require the delay term once when reconstructing a coherent narrowband channel. `verify_export.py` tests this against the saved CIR and matches transmitter/receiver coordinates, since conversion reorders transmitters.

The measurement phase is referenced to a metal plate. Its absolute registration to the simulated channel is uncertain. Shared phase-offset stress tests are essential because the direct and reflected paths interfere coherently.

## Response source and limitations

The OpenSourceRIS source commit is recorded in `data/processed/responses/opensourceris_v1.json`. Published magnitude/phase plots describe a uniformly switched 16×16 surface at normal incidence. We digitize them and extrapolate the two responses to an independent 8×8 mixed-state array with scalar V polarization. At 5.53 GHz the nominal contrast is approximately 179.70 degrees; amplitudes differ between states.

The model omits mutual coupling, edge effects, angle-dependent and element-specific calibration, cross-polarization, surface-induced shadowing, control circuitry, RF switching, and channel-estimation errors. The main simulation uses LOS and specular reflection, depth three, five million rays per source. Diffraction-enabled trials failed the inspected convergence checks; excluding diffraction is an explicit limitation, not evidence that diffraction is negligible.

## Uncertainty protocol

Fixed nominal actions are rescored with the nominal precoder frozen:

- 20 shared response perturbations within ±0.1 dB and ±2 degrees (digitization envelope).
- 20 within ±1 dB and ±15 degrees (uncalibrated model stress envelope).
- Common phase offsets of 45, 90, 180 and 270 degrees.
- Scalar aperture multipliers 0.5 and 2.

Together with nominal this gives 47 conditions. These are stress tests, not measured confidence intervals or retrained robust policies. Ranking changes under large phase offsets require physical validation; they do not establish a learned advantage.

The response digitization also records a horizontal-axis uncertainty of approximately ±3 MHz. The current sensitivity campaign perturbs amplitude and phase directly and does not separately sweep that horizontal offset; the wider model envelope is not a calibrated substitute for this missing check.
