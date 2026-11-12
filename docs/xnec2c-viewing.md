# Inspecting the coupled RIS wire snapshot in Xnec2c

The generated deck is `outputs/geometry/nec_view/frame_0109_alloff_161.nec`. It
contains the registered DEV geometry from frame 109: 64 RIS wires, four base
station (BS) wires, and two user-equipment (UE) wires. The coordinates come
from that frame's `centers` and `lengths` arrays, with the same 50 μm radius
and 5.53 GHz frequency as the coupled model. All 70 wires use 161 segments.

To create another view after changing a switch pattern:

```sh
PYTHONPATH=src python scripts/export_nec_view.py \
  --frame 109 --segments 161 \
  --bits 0000000000000000000000000000000000000000000000000000000000000000 \
  --output outputs/geometry/nec_view/frame_0109_alloff_161.nec
```

The default pattern is all zeroes. Bit 0 or 1 selects the corresponding
registered complex impedance from `outputs/runs/coupled_wire_v1/physics_gate.json`;
it does not mean “physical switch off/on” beyond that model's state labels. RIS
loads are placed at each wire's center segment. The six external BS/UE ports
receive the evaluator's 50-ohm real termination, and a 1 V gap source excites
the center segment of BS wire/tag 65. `GE 0` requests free space and `EK 0`
selects NEC's extended thin-wire kernel.

Open the `.nec` file in Xnec2c (for example, use its Open command), or launch
the Flatpak build from the repository root with a temporary, read-only grant
for the deck folder:

```sh
flatpak run --filesystem="$(pwd)/outputs/geometry/nec_view:ro" \
  org.xnec2c.Xnec2c \
  -i "$(pwd)/outputs/geometry/nec_view/frame_0109_alloff_161.nec"
```

This grants access for this launch only; it does not save a Flatpak override.
You can also open Xnec2c first and use its Open dialog to select the `.nec`
file through the desktop file picker portal.

The 3D view shows the small local RIS scene, not the Munich urban scene. Xnec2c is useful
for checking wire placement, tags, segmentation, and the appearance of one
loaded excitation. The accompanying JSON file records the frame and model
limits.

This is a single-excitation visual deck. The research evaluator obtains the
full 70-port impedance matrix by running 70 separate unit excitations in
PyNEC, then applies its coupled network equations. The view deck has not been
shown numerically equal to that extraction. It also represents idealized
free-space PEC wires: it omits the RIS substrate, switch packages, copper
layout, human blockers, and hardware calibration. A plot from this deck is
therefore a geometry/model illustration, not new propagation or performance
evidence. The 161-segment choice is a reference mesh under study, not a proven
convergence result.

The card meanings used here follow the [NEC-2 User's Manual EK card
description](https://www.nec2.org/other/nec2prt3.pdf) and the [Xnec2c
manual](https://www.xnec2c.org/), which documents the extended-kernel support.
