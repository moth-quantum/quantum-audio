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

"""PennyLane backend for quantumaudio."""

from __future__ import annotations

from typing import Any, Callable

import numpy as np

from quantumaudio.backends._optional import require
from quantumaudio.backends.core.backend import Backend
from quantumaudio.backends.core.circuit import CircuitSpec, GateOp
from quantumaudio.backends.core.result import UnifiedResult
from quantumaudio.backends.core.types import GateType

qml = require("pennylane", extras_name="pennylane")


_SINGLE_GATE = {
    GateType.H: qml.Hadamard,
    GateType.X: qml.PauliX,
    GateType.Y: qml.PauliY,
    GateType.Z: qml.PauliZ,
    GateType.S: qml.S,
    GateType.T: qml.T,
}

_PARAM_GATE = {
    GateType.RX: qml.RX,
    GateType.RY: qml.RY,
    GateType.RZ: qml.RZ,
}

_TWO_GATE = {
    GateType.CX: qml.CNOT,
    GateType.CZ: qml.CZ,
    GateType.SWAP: qml.SWAP,
}

_CTRL_PARAM = {
    GateType.CRX: qml.CRX,
    GateType.CRY: qml.CRY,
    GateType.CRZ: qml.CRZ,
}


def _apply_op(op: GateOp) -> None:
    """Apply a single GateOp by emitting the matching PennyLane op."""
    g = op.gate
    idx = op.qubits

    if g in _SINGLE_GATE:
        _SINGLE_GATE[g](wires=idx[0])
        return
    if g in _PARAM_GATE:
        _PARAM_GATE[g](op.params[0], wires=idx[0])
        return
    if g in _TWO_GATE:
        _TWO_GATE[g](wires=[idx[0], idx[1]])
        return
    if g in _CTRL_PARAM:
        _CTRL_PARAM[g](op.params[0], wires=[idx[0], idx[1]])
        return
    if g == GateType.MCX:
        qml.MultiControlledX(wires=list(idx))
        return
    if g == GateType.MCRY:
        qml.ctrl(qml.RY, control=list(idx[:-1]))(
            op.params[0], wires=idx[-1]
        )
        return
    # MEASURE is collected separately by build_circuit.
    # BARRIER and anything else: no-op for execution.


def _kernel_factory(
    spec: CircuitSpec,
) -> tuple[Callable[[], None], list[int]]:
    """Build a closure that applies all non-measurement ops, plus the
    list of wires marked by MEASURE ops in the order encountered."""
    measured_wires: list[int] = []
    gate_ops: list[GateOp] = []
    for op in spec.ops:
        if op.gate == GateType.MEASURE:
            measured_wires.append(op.qubits[0])
        elif op.gate == GateType.BARRIER:
            continue
        else:
            gate_ops.append(op)

    def kernel_fn() -> None:
        for op in gate_ops:
            _apply_op(op)

    return kernel_fn, measured_wires


class PennyLaneBackend(Backend):
    """PennyLane backend.

    Defaults to the ``default.qubit`` simulator. Pass any other PennyLane
    device name (e.g. ``"lightning.qubit"``, ``"ionq.simulator"``,
    ``"ionq.qpu"``) to target a different simulator or hardware. Vendor
    plugins must be installed separately.
    """

    name = "pennylane"

    def __init__(
        self, device: str = "default.qubit", **device_kwargs: Any
    ):
        self._device = device
        self._device_kwargs = device_kwargs

    def build_circuit(self, spec: CircuitSpec) -> dict:
        """Build a closure-based representation of the circuit.

        Returns a dict carrying the gate-emitting kernel function, the
        wires to measure, and metadata for use by :meth:`run` and
        :meth:`statevector`.
        """
        kernel_fn, measured_wires = _kernel_factory(spec)
        return {
            "kernel_fn": kernel_fn,
            "measured_wires": measured_wires,
            "num_qubits": spec.num_qubits,
            "metadata": {
                k: v
                for k, v in spec.metadata.items()
                if k != "registers"
            },
        }

    def run(
        self, native_circuit: dict, shots: int = 1024
    ) -> UnifiedResult:
        """Execute on the configured PennyLane device."""
        n = native_circuit["num_qubits"]
        kernel_fn = native_circuit["kernel_fn"]
        measured = native_circuit["measured_wires"] or list(range(n))

        dev = qml.device(
            self._device, wires=n, **self._device_kwargs
        )

        @qml.qnode(dev)
        def node():
            kernel_fn()
            return qml.counts(wires=measured)

        raw = qml.set_shots(node, shots=shots)()
        # PennyLane returns counts in big-endian wire order (wire 0 is
        # the leftmost character). Reverse to match the codebase's
        # Qiskit little-endian convention.
        counts = {str(k)[::-1]: int(v) for k, v in raw.items()}
        return UnifiedResult(
            counts, shots, self.name, native_circuit["metadata"]
        )

    def statevector(self, native_circuit: dict) -> np.ndarray:
        """Return the exact statevector via ``default.qubit``.

        Hardware devices do not expose statevectors, so this always
        runs on the local simulator regardless of the configured device.
        """
        n = native_circuit["num_qubits"]
        kernel_fn = native_circuit["kernel_fn"]
        dev = qml.device("default.qubit", wires=n)

        @qml.qnode(dev)
        def sv_node():
            kernel_fn()
            return qml.state()

        return np.asarray(sv_node())
