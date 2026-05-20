# Copyright 2024 Moth Quantum
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==========================================================================

"""Cirq backend for quantumaudio."""

from __future__ import annotations

import numpy as np

from quantumaudio.backends._optional import require
from quantumaudio.backends.core.backend import Backend
from quantumaudio.backends.core.circuit import CircuitSpec, GateOp
from quantumaudio.backends.core.result import UnifiedResult
from quantumaudio.backends.core.types import GateType

cirq = require("cirq", extras_name="cirq")


def _qubits(n: int):
    """Create a list of Cirq LineQubits."""
    return cirq.LineQubit.range(n)


_SINGLE_GATE = {
    GateType.H: lambda: cirq.H,
    GateType.X: lambda: cirq.X,
    GateType.Y: lambda: cirq.Y,
    GateType.Z: lambda: cirq.Z,
    GateType.S: lambda: cirq.S,
    GateType.T: lambda: cirq.T,
}

_PARAM_GATE = {
    GateType.RX: cirq.rx,
    GateType.RY: cirq.ry,
    GateType.RZ: cirq.rz,
}

_TWO_GATE = {
    GateType.CX: lambda: cirq.CNOT,
    GateType.CZ: lambda: cirq.CZ,
    GateType.SWAP: lambda: cirq.SWAP,
}

_CTRL_PARAM = {
    GateType.CRX: cirq.rx,
    GateType.CRY: cirq.ry,
    GateType.CRZ: cirq.rz,
}


def _apply_op(qubits, op: GateOp) -> list:  # noqa: PLR0911
    """Return a list of Cirq operations for a single GateOp."""
    g = op.gate
    idx = op.qubits

    if g in _SINGLE_GATE:
        return [_SINGLE_GATE[g]()(qubits[idx[0]])]
    if g in _PARAM_GATE:
        return [_PARAM_GATE[g](op.params[0])(qubits[idx[0]])]
    if g in _TWO_GATE:
        return [
            _TWO_GATE[g]()(qubits[idx[0]], qubits[idx[1]])
        ]
    if g in _CTRL_PARAM:
        return [
            _CTRL_PARAM[g](op.params[0])(
                qubits[idx[1]]
            ).controlled_by(qubits[idx[0]])
        ]
    if g == GateType.MCX:
        ctrls = [qubits[i] for i in idx[:-1]]
        return [cirq.X(qubits[idx[-1]]).controlled_by(*ctrls)]
    if g == GateType.MCRY:
        ctrls = [qubits[i] for i in idx[:-1]]
        return [
            cirq.ry(op.params[0])(
                qubits[idx[-1]]
            ).controlled_by(*ctrls)
        ]
    if g == GateType.MEASURE:
        return [
            cirq.measure(qubits[idx[0]], key=str(idx[0]))
        ]
    # BARRIER and anything else: no-op.
    return []


class CirqBackend(Backend):
    """Google Cirq simulator backend."""

    name = "cirq"

    def build_circuit(
        self, spec: CircuitSpec
    ) -> dict:
        """Build a Cirq circuit from a CircuitSpec.

        Returns a dict with the circuit, qubits, and metadata
        for use by :meth:`run` and :meth:`statevector`.
        """
        n = spec.num_qubits
        qubits = _qubits(n)
        moments_ops = []
        for op in spec.ops:
            ops = _apply_op(qubits, op)
            moments_ops.extend(ops)
        circuit = cirq.Circuit(moments_ops)
        return {
            "circuit": circuit,
            "qubits": qubits,
            "num_qubits": n,
            "metadata": {
                k: v
                for k, v in spec.metadata.items()
                if k != "registers"
            },
        }

    def run(
        self, native_circuit: dict, shots: int = 1024
    ) -> UnifiedResult:
        """Execute the circuit and return UnifiedResult."""
        circuit = native_circuit["circuit"]
        n = native_circuit["num_qubits"]
        metadata = native_circuit["metadata"]

        sim = cirq.Simulator()
        result = sim.run(circuit, repetitions=shots)

        # Build bitstrings from per-qubit measurement keys.
        # Reverse to match Qiskit's little-endian convention:
        # qubit 0 is the rightmost bit.
        counts: dict[str, int] = {}
        for i in range(shots):
            bits = []
            for q in range(n - 1, -1, -1):
                key = str(q)
                bits.append(
                    str(result.measurements[key][i, 0])
                )
            bitstring = "".join(bits)
            counts[bitstring] = counts.get(bitstring, 0) + 1

        return UnifiedResult(counts, shots, self.name, metadata)

    def statevector(self, native_circuit: dict) -> np.ndarray:
        """Return the exact statevector."""
        circuit = native_circuit["circuit"]

        # Strip measurement gates for statevector computation.
        clean_ops = [
            op
            for moment in circuit.moments
            for op in moment.operations
            if not cirq.is_measurement(op)
        ]
        clean = cirq.Circuit(clean_ops)

        sim = cirq.Simulator()
        sv_result = sim.simulate(clean)
        return sv_result.final_state_vector
