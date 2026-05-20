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

"""Qiskit backend for quantumaudio."""

from __future__ import annotations

import numpy as np
import qiskit
import qiskit_aer
from qiskit import ClassicalRegister
from qiskit.circuit.library import RYGate
from qiskit.quantum_info import Statevector
from qiskit.transpiler.preset_passmanagers import (
    generate_preset_pass_manager,
)

from quantumaudio.backends.core.backend import Backend
from quantumaudio.backends.core.circuit import CircuitSpec, GateOp
from quantumaudio.backends.core.result import UnifiedResult
from quantumaudio.backends.core.types import GateType


_SINGLE_QUBIT = {
    GateType.H: "h",
    GateType.X: "x",
    GateType.Y: "y",
    GateType.Z: "z",
    GateType.S: "s",
    GateType.T: "t",
}

_SINGLE_QUBIT_PARAM = {
    GateType.RX: "rx",
    GateType.RY: "ry",
    GateType.RZ: "rz",
}

_TWO_QUBIT = {
    GateType.CX: "cx",
    GateType.CZ: "cz",
    GateType.SWAP: "swap",
}

_TWO_QUBIT_PARAM = {
    GateType.CRX: "crx",
    GateType.CRY: "cry",
    GateType.CRZ: "crz",
}


def _apply_op(qc, qubits, op: GateOp):
    """Apply a single GateOp to a Qiskit QuantumCircuit."""
    g = op.gate
    idx = op.qubits

    if g in _SINGLE_QUBIT:
        getattr(qc, _SINGLE_QUBIT[g])(qubits[idx[0]])
    elif g in _SINGLE_QUBIT_PARAM:
        getattr(qc, _SINGLE_QUBIT_PARAM[g])(
            op.params[0], qubits[idx[0]]
        )
    elif g in _TWO_QUBIT:
        getattr(qc, _TWO_QUBIT[g])(
            qubits[idx[0]], qubits[idx[1]]
        )
    elif g in _TWO_QUBIT_PARAM:
        getattr(qc, _TWO_QUBIT_PARAM[g])(
            op.params[0], qubits[idx[0]], qubits[idx[1]]
        )
    elif g == GateType.MCX:
        ctrls = [qubits[i] for i in idx[:-1]]
        qc.mcx(ctrls, qubits[idx[-1]])
    elif g == GateType.MCRY:
        ctrls = [qubits[i] for i in idx[:-1]]
        controlled_ry = RYGate(op.params[0]).control(
            len(ctrls)
        )
        qc.append(controlled_ry, [*ctrls, qubits[idx[-1]]])
    elif g == GateType.MEASURE:
        qc.measure(qubits[idx[0]], op.clbits[0])
    elif g == GateType.BARRIER:
        qc.barrier()


class QiskitBackend(Backend):
    """Qiskit / AerSimulator backend."""

    name = "qiskit"

    def build_circuit(self, spec: CircuitSpec) -> qiskit.QuantumCircuit:
        """Translate CircuitSpec to a Qiskit QuantumCircuit.

        If register metadata is present, named QuantumRegisters are
        created for better circuit visualisation.
        """
        regs_meta = spec.metadata.get("registers", {})
        if regs_meta:
            regs = []
            qubit_list = [None] * spec.num_qubits
            for reg_name, (start, size) in regs_meta.items():
                if size > 0:
                    reg = qiskit.QuantumRegister(size, reg_name)
                    regs.append(reg)
                    for i in range(size):
                        qubit_list[start + i] = reg[i]
            qc = qiskit.QuantumCircuit(
                *regs, name=spec.name
            )
            # Map integer qubit indices to Qiskit qubit objects.
            qubits = qc.qubits
        else:
            qc = qiskit.QuantumCircuit(
                spec.num_qubits, spec.num_clbits, name=spec.name
            )
            qubits = qc.qubits

        # Copy non-register metadata to the Qiskit circuit.
        qc.metadata = {
            k: v
            for k, v in spec.metadata.items()
            if k != "registers"
        }

        for op in spec.ops:
            if op.gate == GateType.MEASURE and not qc.cregs:
                qc.add_register(
                    ClassicalRegister(spec.num_clbits)
                )
            _apply_op(qc, qubits, op)

        return qc

    def run(
        self, native_circuit, shots: int = 1024
    ) -> UnifiedResult:
        """Execute on AerSimulator and return UnifiedResult."""
        backend = qiskit_aer.AerSimulator()
        pm = generate_preset_pass_manager(
            optimization_level=1, backend=backend
        )
        transpiled = pm.run(native_circuit)
        job = backend.run(transpiled, shots=shots)
        result = job.result()
        raw_counts = result.get_counts()

        # Normalise keys to zero-padded binary strings.
        n_bits = native_circuit.num_clbits
        counts: dict[str, int] = {}
        for raw_key, val in raw_counts.items():
            key = raw_key.replace(" ", "")
            if key.startswith("0x"):
                bits = bin(int(key, 16))[2:].zfill(n_bits)
            else:
                bits = key.zfill(n_bits)
            counts[bits] = counts.get(bits, 0) + val

        metadata = (
            native_circuit.metadata
            if native_circuit.metadata
            else {}
        )
        return UnifiedResult(counts, shots, self.name, metadata)

    def statevector(self, native_circuit) -> np.ndarray:
        """Return the exact statevector."""
        # Strip measurements for statevector computation.
        qc = native_circuit.remove_final_measurements(
            inplace=False
        )
        sv = Statevector.from_instruction(qc)
        return np.asarray(sv)
