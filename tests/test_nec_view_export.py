"""Executable standard-library checks for the Xnec2c deck exporter."""
import importlib.util
from pathlib import Path
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
GEOMETRY_DECK_ATOL_M = 1e-14
IMPEDANCE_DECK_ATOL_OHM = 1e-12
spec = importlib.util.spec_from_file_location("export_nec_view", ROOT / "scripts/export_nec_view.py")
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)


class NecViewExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = exporter.load_inputs(exporter.DEFAULT_DATA, exporter.DEFAULT_GATE, 109, 161)
        cls.centers, cls.lengths, cls.radius, cls.frequency, cls.loads, _, _ = cls.inputs

    def test_registered_frame_endpoints_mesh_and_cards(self):
        text = exporter.render_deck(
            self.centers, self.lengths, self.radius, self.frequency, self.loads,
            161, np.zeros(64, dtype=np.int8), 109,
        )
        wires = [line.split() for line in text.splitlines() if line.startswith("GW ")]
        self.assertEqual(len(wires), 70)
        for tag, (fields, center, length) in enumerate(zip(wires, self.centers, self.lengths), 1):
            self.assertEqual(int(fields[1]), tag)
            self.assertEqual(int(fields[2]), 161)
            x, y, z = center
            expected = np.array([x, y, z - length / 2, x, y, z + length / 2])
            # GW coordinates use 15 significant digits; allow 1e-14 m parse error.
            np.testing.assert_allclose(np.array(fields[3:9], dtype=float), expected,
                                       rtol=0, atol=GEOMETRY_DECK_ATOL_M)
            self.assertAlmostEqual(float(fields[9]), self.radius, delta=1e-15)
        self.assertIn("FR 0 1 5530 0 0 0", text)
        self.assertIn("EK 0", text)
        self.assertIn("GE 0", text)

    def test_explicit_bits_map_to_center_segment_loads_and_excitation(self):
        bits = np.zeros(64, dtype=np.int8)
        bits[0] = bits[-1] = 1
        lines = exporter.render_deck(
            self.centers, self.lengths, self.radius, self.frequency, self.loads,
            161, bits, 109,
        ).splitlines()
        load_rows = [line.split() for line in lines if line.startswith("LD 4")]
        ris_loads = [row for row in load_rows if int(row[2]) <= 64]
        self.assertEqual(len(ris_loads), 64)
        for i, fields in enumerate(ris_loads):
            self.assertEqual(int(fields[2]), i + 1)  # LD columns: type, tag, first, last, R, X, ...
            self.assertEqual(int(fields[3]), int(fields[4]), 81)
            np.testing.assert_allclose(
                np.array(fields[5:7], dtype=float),
                [self.loads[int(bits[i])].real, self.loads[int(bits[i])].imag],
                rtol=0, atol=IMPEDANCE_DECK_ATOL_OHM,
            )
        port_loads = [row for row in load_rows if int(row[2]) >= 65]
        self.assertEqual([int(row[2]) for row in port_loads], list(range(65, 71)))
        for row in port_loads:
            self.assertEqual(int(row[3]), int(row[4]), 81)
            np.testing.assert_allclose(np.array(row[5:7], dtype=float), [50, 0], rtol=0, atol=0)
        self.assertIn("EX 0 65 81 0 1 0 0 0 0 0", lines)

    def test_invalid_mesh_and_bitvector_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "odd"):
            exporter.render_deck(self.centers, self.lengths, self.radius, self.frequency,
                                 self.loads, 160, np.zeros(64, dtype=np.int8), 109)
        with self.assertRaisesRegex(ValueError, "64 binary"):
            exporter.render_deck(self.centers, self.lengths, self.radius, self.frequency,
                                 self.loads, 161, np.zeros(63, dtype=np.int8), 109)

    def test_noncanonical_data_root_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "canonical registered DEV root"):
            exporter.load_inputs(ROOT / "data/processed/coupled_wire_test_v2",
                                 exporter.DEFAULT_GATE, 109, 161)


if __name__ == "__main__":
    unittest.main()
