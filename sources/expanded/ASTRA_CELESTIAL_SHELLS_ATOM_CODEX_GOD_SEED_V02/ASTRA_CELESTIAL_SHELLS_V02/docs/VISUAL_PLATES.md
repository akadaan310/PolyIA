# Render plates, depth, optics, and attention

## Current runnable plate compositor

`stars`, `plasma`, and `focus` are separate HTML Canvas2D draw surfaces, ordered by z-layer and projected through CSS transforms; each can be disabled independently. The stellar plane draws a small **observed Hipparcos/J2000 direction sample** from the previous Astro commission and independent decorative particles clearly not attributed to a catalogue. The plasma plane draws trigonometric phase fields, not measured atomic plasmas. The focus plane draws an inferred attention marker.

Their displacement is controlled by a damped second-order spring:

`d²y/dt² + 2ζω dy/dt + ω² (y - y_goal) = 0`

The prototype integrates with a bounded explicit timestep in the `requestAnimationFrame` loop. This is **layer-motion physics** only, not material plasticity, actual 3D interpenetration, or physically accurate camera depth of field. Plate depth values are normalized 0–1 and are not measured distances. Current performance reporting is a local sample of frame intervals, not a rigorous jitter/latency certification.

## Proposed higher-fidelity pipeline

1. Convert typed plate objects to a render graph with dependencies and intermediate attachments.
2. Use WebGPU/wgpu or an equivalent GPU abstraction for compositing and compute passes.
3. Introduce depth maps and focus distances, then physically plausible circle-of-confusion (CoC) blur; keep a no-blur accessibility mode.
4. Add real celestial coordinates with a catalog spatial index and Horizons/NAIF SPICE observer ephemerides, choosing inertial frames and light-time conventions explicitly.
5. Separate spectral observables (real measurements, uncertainty) from scientific visual representations.
6. Add user-initiated audio mapping and Isnad verse identifiers behind an explicit source adapter, preserving recitation rights and exact text; never invent recitation content.
7. Benchmark actual Android (including thermal behavior), desktop browsers, and hardware GPUs with percentile frame-time distributions; label software renderer runs honestly.

## Attention

Simulated attention uses last pointer/touch location. Without pointer activity it uses an **idle motion heuristic** for display demonstration. No webcam, no true gaze prediction, and no claim of psychological measurement. A proper learned saliency model would require a declared dataset, comparison baseline, privacy controls, and evidence of prediction quality; it must not be represented as direct eye tracking.
