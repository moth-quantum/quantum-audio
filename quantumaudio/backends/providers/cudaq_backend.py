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

"""NVIDIA CUDA-Q backend for quantumaudio."""

from __future__ import annotations

from typing import Any

import numpy as np

from quantumaudio.backends._optional import require
from quantumaudio.backends.core.backend import Backend
from quantumaudio.backends.core.circuit import CircuitSpec, GateOp
from quantumaudio.backends.core.result import UnifiedResult
from quantumaudio.backends.core.types import GateType

cudaq = require("cudaq", extras_name="cudaq")


# Map GateType to the kernel-builder method name that takes the same
# argument shape (single target, single param + target, two qubits, etc.).
_SINGLE_GATE = {
    GateType.H: "h",
    GateType.X: "x",
    GateType.Y: "y",
    GateType.Z: "z",
    GateType.S: "s",
    GateType.T: "t",
}

_PARAM_GATE = {
    GateType.RX: "rx",
    GateType.RY: "ry",
    GateType.RZ: "rz",
}

_TWO_GATE = {
    GateType.CX: "cx",
    GateType.CZ: "cz",
    GateType.SWAP: "swap",
}

_CTRL_PARAM = {
    GateType.CRX: "crx",
    GateType.CRY: "cry",
    GateType.CRZ: "crz",
}


def _apply_op(kernel, qubits, op: GateOp) -> None:  # noqa: PLR0911
    """Emit one CUDA-Q kernel operation for a single GateOp."""
    g = op.gate
    idx = op.qubits

    if g in _SINGLE_GATE:
        getattr(kernel, _SINGLE_GATE[g])(qubits[idx[0]])
        return
    if g in _PARAM_GATE:
        getattr(kernel, _PARAM_GATE[g])(
            op.params[0], qubits[idx[0]]
        )
        return
    if g in _TWO_GATE:
        getattr(kernel, _TWO_GATE[g])(
            qubits[idx[0]], qubits[idx[1]]
        )
        return
    if g in _CTRL_PARAM:
        getattr(kernel, _CTRL_PARAM[g])(
            op.params[0], qubits[idx[0]], qubits[idx[1]]
        )
        return
    if g == GateType.MCX:
        # cx accepts a list of control qubits for multi-control.
        controls = [qubits[i] for i in idx[:-1]]
        kernel.cx(controls, qubits[idx[-1]])
        return
    if g == GateType.MCRY:
        controls = [qubits[i] for i in idx[:-1]]
        kernel.cry(op.params[0], controls, qubits[idx[-1]])
        return
    if g == GateType.MEASURE:
        kernel.mz(qubits[idx[0]])
        return
    # BARRIER and anything else: no-op for execution.


# Remote vendor targets where omitting a machine-selector kwarg routes
# to *real* QPU hardware (paid). Mapping is target name -> name of the
# kwarg that selects simulator vs specific QPU. Omitting the kwarg is
# blocked at construction time so a bare `CudaQBackend(target="ionq")`
# cannot silently reach for billed hardware.
_REMOTE_TARGETS_REQUIRE_SELECTOR = {
    "ionq": "qpu",
    "anyon": "machine",
    "braket": "machine",
    "infleqtion": "machine",
    "oqc": "machine",
    "quantinuum": "machine",
    "scaleway": "machine",
}


class CudaQBackend(Backend):
    """NVIDIA CUDA-Q backend.

    Defaults to the ``qpp-cpu`` target so that tests run in CPU-only
    environments. Pass any other CUDA-Q target name (e.g. ``"nvidia"``,
    ``"nvidia-mgpu"``, ``"tensornet"``, ``"ionq"``, ``"quantinuum"``,
    ``"iqm"``, ``"braket"``) to target a different simulator or hardware,
    plus any target-specific keyword arguments (e.g.
    ``CudaQBackend(target="ionq", qpu="simulator")`` to hit IonQ's cloud
    simulator instead of the real QPU). Vendor credentials must be
    configured per CUDA-Q's documentation for any non-local target.

    For vendor targets where omitting the machine-selector kwarg defaults
    to running on real hardware (``ionq``, ``anyon``, ``braket``,
    ``infleqtion``, ``oqc``, ``quantinuum``, ``scaleway``), the
    constructor refuses to instantiate without an explicit selector --
    pass e.g. ``qpu="simulator"`` for IonQ's cloud simulator (free) or
    ``qpu="qpu.aria-1"`` for a specific QPU.

    Note: ``cudaq.set_target()`` mutates process-global state; this
    backend re-asserts its target on every ``run()`` and ``statevector()``
    call, so multiple backend instances in the same process do not
    interfere with each other but concurrent use across threads is not
    supported.
    """

    name = "cudaq"

    def __init__(self, target: str = "qpp-cpu", **target_kwargs: Any):
        selector = _REMOTE_TARGETS_REQUIRE_SELECTOR.get(target)
        if selector is not None and selector not in target_kwargs:
            raise ValueError(
                f"CudaQBackend(target={target!r}) defaults to running "
                f"on real hardware, which can be expensive. Pass "
                f"{selector}=<value> explicitly: e.g. "
                f"{selector}='simulator' for the vendor's free cloud "
                f"simulator, or {selector}='<qpu-name>' for a specific "
                f"QPU."
            )
        self._target = target
        self._target_kwargs = target_kwargs

    def build_circuit(self, spec: CircuitSpec) -> dict:
        """Build a CUDA-Q kernel from a CircuitSpec.

        Returns a dict carrying the kernel and metadata for use by
        :meth:`run` and :meth:`statevector`.
        """
        kernel = cudaq.make_kernel()
        qubits = kernel.qalloc(spec.num_qubits)
        for op in spec.ops:
            _apply_op(kernel, qubits, op)
        return {
            "kernel": kernel,
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
        """Execute on the configured CUDA-Q target."""
        cudaq.set_target(self._target, **self._target_kwargs)
        sample = cudaq.sample(
            native_circuit["kernel"], shots_count=shots
        )
        # CUDA-Q returns counts in big-endian wire order (qubit 0 is
        # the leftmost character). Reverse to match the codebase's
        # Qiskit little-endian convention.
        counts = {k[::-1]: int(v) for k, v in sample.items()}
        return UnifiedResult(
            counts, shots, self.name, native_circuit["metadata"]
        )

    def statevector(self, native_circuit: dict) -> np.ndarray:
        """Return the exact statevector.

        Uses the configured target if it supports state extraction; the
        default ``qpp-cpu`` target does. Hardware targets do not.
        """
        cudaq.set_target(self._target, **self._target_kwargs)
        return np.asarray(cudaq.get_state(native_circuit["kernel"]))
