# This code is part of Qiskit.
#
# (C) Copyright IBM 2021.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

""" Test Z2Symmetries """

import unittest

from test.python.opflow import QiskitOpflowTestCase

from qiskit.quantum_info import Pauli, SparsePauliOp
from qiskit.quantum_info.analysis.z2_symmetries import Z2Symmetries


class TestSparseZ2Symmetries(QiskitOpflowTestCase):
    """Z2Symmetries tests."""

    def test_find_z2_symmetries(self):
        """test for find_z2_symmetries"""

        qubit_op = SparsePauliOp.from_list(
            [
                ("II", -1.0537076071291125),
                ("IZ", 0.393983679438514),
                ("ZI", -0.39398367943851387),
                ("ZZ", -0.01123658523318205),
                ("XX", 0.1812888082114961),
            ]
        )
        z2_symmetries = Z2Symmetries.find_z2_symmetries(qubit_op)
        self.assertEqual(z2_symmetries.symmetries, [Pauli("ZZ")])
        self.assertEqual(z2_symmetries.sq_paulis, [Pauli("IX")])
        self.assertEqual(z2_symmetries.sq_list, [0])
        self.assertEqual(z2_symmetries.tapering_values, None)

        tapered_op = z2_symmetries.taper(qubit_op)[1]
        expected_op = SparsePauliOp.from_list(
            [
                ("I", -1.0424710218959303),
                ("Z", -0.7879673588770277),
                ("X", -0.18128880821149604),
            ]
        )
        self.assertEqual(tapered_op, expected_op)

    def test_taper_empty_operator(self):
        """Test tapering of empty operator"""
        z2_symmetries = Z2Symmetries(
            symmetries=[Pauli("IIZI"), Pauli("IZIZ"), Pauli("ZIII")],
            sq_paulis=[Pauli("IIXI"), Pauli("IIIX"), Pauli("XIII")],
            sq_list=[1, 0, 3],
            tapering_values=[1, -1, -1],
        )
        empty_op = SparsePauliOp.from_list([("IIII", 0.0)])
        tapered_op = z2_symmetries.taper(empty_op)
        expected_op = SparsePauliOp.from_list([("I", 0.0)])
        self.assertEqual(tapered_op, expected_op)

    def test_truncate_tapered_op(self):
        """Test setting cutoff tolerances for the tapered operator works."""
        qubit_op = SparsePauliOp.from_list(
            [
                ("II", -1.0537076071291125),
                ("IZ", 0.393983679438514),
                ("ZI", -0.39398367943851387),
                ("ZZ", -0.01123658523318205),
                ("XX", 0.1812888082114961),
            ]
        )
        z2_symmetries = Z2Symmetries.find_z2_symmetries(qubit_op)
        z2_symmetries.tol = 0.2  # removes the X part of the tapered op which is < 0.2

        tapered_op = z2_symmetries.taper(qubit_op)[1]
        primitive = SparsePauliOp.from_list(
            [
                ("I", -1.0424710218959303),
                ("Z", -0.7879673588770277),
            ]
        )
        expected_op = primitive
        self.assertEqual(tapered_op, expected_op)

    def test_twostep_tapering(self):
        """Test the two-step tapering"""
        qubit_op = SparsePauliOp.from_list(
            [
                ("II", -1.0537076071291125),
                ("IZ", 0.393983679438514),
                ("ZI", -0.39398367943851387),
                ("ZZ", -0.01123658523318205),
                ("XX", 0.1812888082114961),
            ]
        )
        z2_symmetries = Z2Symmetries.find_z2_symmetries(qubit_op)
        converted_op_firststep = z2_symmetries.convert_clifford(qubit_op)
        tapered_op_secondstep = z2_symmetries.taper_clifford(converted_op_firststep)

        with self.subTest("Check first step: Clifford transformation"):
            converted_op_expected = SparsePauliOp.from_list(
                [
                    ("II", -1.0537076071291125),
                    ("ZX", 0.393983679438514),
                    ("ZI", -0.39398367943851387),
                    ("IX", -0.01123658523318205),
                    ("XX", 0.1812888082114961),
                ]
            )

            self.assertEqual(converted_op_expected, converted_op_firststep)

        with self.subTest("Check second step: Tapering"):
            tapered_op = z2_symmetries.taper(qubit_op)
            self.assertEqual(tapered_op, tapered_op_secondstep)


if __name__ == "__main__":
    unittest.main()
