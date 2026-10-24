# Decisions before learned-controller evaluation

1. **Historical experiment preserved.** The canonical implementation now lives in `atom-wise-ris/`; the original feasibility source is archived.
2. **Port 2002 is the active machine.** The bounded v5 campaign trains sequentially on one idle RTX 3060. Other users' jobs are untouched. Since leaving the university
   network, access is via `ssh -J faris@labkc-comm1 -p 2002 faris@gpu-labkc.ub.ac.id`.
   Port 2003 can use the same route. Authentication is external to research files.
3. **Digitization is reproducible.** Separate red/blue curves, original pixel
   calibration and image hashes are retained. At 5.53 GHz the extracted states
   are approximately -5.12 and -1.83 dB, with phases -170.48 and +9.22 degrees.
   An 8x8 independent array uses the published 20x13 mm cell area.
4. **Geometry v1 rejected.** Receivers inside buildings and behind the panel were
   found by explicit audit. The corrected layout selects outdoor spatial blocks
   before ray tracing or label generation. It retains all eligible outcomes,
   including blocked direct paths; no favorable-rate filtering is used.
5. **100,000 rays is inadequate here.** Channel changes remained substantial
   under ray-count increases. Raising path capacity from 100,000 to 1,000,000
   did not resolve the diffraction instability. Even 5M-to-10M diffraction
   traces changed the sampled BS channels by approximately 18.6% in relative
   L2 norm and sampled RIS-user channels by 8.8%.
6. **The first comparison uses LOS + specular reflections.** With diffraction
   disabled, 2M-to-5M changes on the checked train/validation subset were 0.32%
   for the BS links and 0.034% for RIS-user links. The operational pilot uses
   5M rays/source, depth 3, 1M path capacity, no diffuse reflection, no refraction
   and no diffraction. This is a narrower simulation claim, not evidence that
   diffraction is negligible in reality. Final convergence is not established
   for every point or every material model.
7. **Precoder fixed from the all-OFF reference.** Direct-only RZF silently sets
   a stream to zero for a user with an entirely blocked direct channel. The
   main comparison instead computes RZF once from the all-OFF effective channel,
   including the RIS, then freezes it for every candidate and every method.
   Earlier direct-only headroom artifacts are retained as development runs.
8. **Completed pairs exist, but headroom is modest.** In the preliminary v4 dataset, 15/48 training snapshots have a positive pair move exceeding
   1e-6 bit/s/Hz after single-bit convergence. The median positive gain is
   3.52e-5 bit/s/Hz. This permits bounded learning experiments; it does not
   establish that learned mutation is worthwhile at equal online time.
9. **Export phase is checked explicitly.** The DeepMIMO-exported interaction
   phase is reconstructed with carrier delay exactly once and checked against
   the Sionna CIR. Simply summing the default DeepMIMO taps is not the coherent
   carrier-channel operation required by this evaluator. The old v2 BS export
   reconstruction had 0.12–0.14% relative L2 error, consistent with stored
   single-precision delays. The solver frequency representation is recorded.
10. **The pilot is development data.** No paper-final test has been generated.
    Physics uncertainty, convergence and small trajectory counts limit claims
    regardless of which learned policy wins a particular optimizer comparison.
