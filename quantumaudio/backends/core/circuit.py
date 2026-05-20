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

"""Framework-agnostic quantum circuit description."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

import numpy as np

from quantumaudio.backends.core.types import GateType


@dataclass(frozen=True)
class GateOp:
    """A single gate operation.

    ``params`` carries gate angles (e.g. ``RY(theta)``); ``clbits``
    carries the classical-bit targets for measurements. Keeping the
    two separate avoids overloading ``params`` for non-angle data.
    """

    gate: GateType
    qubits: tuple[int, ...]
    params: tuple[float, ...] = ()
    clbits: tuple[int, ...] = ()


@dataclass
class CircuitSpec:
    """Framework-agnostic quantum circuit specification.

    This is a pure data structure. Backends translate it into their
    native circuit representation for execution. The builder API
    mirrors the gate-method style used by Qiskit and MicroMoth so
    that circuits read naturally.
    """

    num_qubits: int
    num_clbits: int = 0
    ops: list[GateOp] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    name: str = ""

    # -- single-qubit gates -----------------------------------------------

    def h(self, qubit: int) -> CircuitSpec:
        self.ops.append(GateOp(GateType.H, (qubit,)))
        return self

    def x(self, qubit: int) -> CircuitSpec:
        self.ops.append(GateOp(GateType.X, (qubit,)))
        return self

    def y(self, qubit: int) -> CircuitSpec:
        self.ops.append(GateOp(GateType.Y, (qubit,)))
        return self

    def z(self, qubit: int) -> CircuitSpec:
        self.ops.append(GateOp(GateType.Z, (qubit,)))
        return self

    def s(self, qubit: int) -> CircuitSpec:
        self.ops.append(GateOp(GateType.S, (qubit,)))
        return self

    def t(self, qubit: int) -> CircuitSpec:
        self.ops.append(GateOp(GateType.T, (qubit,)))
        return self

    def rx(self, theta: float, qubit: int) -> CircuitSpec:
        self.ops.append(GateOp(GateType.RX, (qubit,), (theta,)))
        return self

    def ry(self, theta: float, qubit: int) -> CircuitSpec:
        self.ops.append(GateOp(GateType.RY, (qubit,), (theta,)))
        return self

    def rz(self, theta: float, qubit: int) -> CircuitSpec:
        self.ops.append(GateOp(GateType.RZ, (qubit,), (theta,)))
        return self

    # -- two-qubit gates ---------------------------------------------------

    def cx(self, control: int, target: int) -> CircuitSpec:
        self.ops.append(GateOp(GateType.CX, (control, target)))
        return self

    def cz(self, control: int, target: int) -> CircuitSpec:
        self.ops.append(GateOp(GateType.CZ, (control, target)))
        return self

    def crx(
        self, theta: float, control: int, target: int
    ) -> CircuitSpec:
        self.ops.append(
            GateOp(GateType.CRX, (control, target), (theta,))
        )
        return self

    def cry(
        self, theta: float, control: int, target: int
    ) -> CircuitSpec:
        self.ops.append(
            GateOp(GateType.CRY, (control, target), (theta,))
        )
        return self

    def crz(
        self, theta: float, control: int, target: int
    ) -> CircuitSpec:
        self.ops.append(
            GateOp(GateType.CRZ, (control, target), (theta,))
        )
        return self

    def swap(self, qubit1: int, qubit2: int) -> CircuitSpec:
        self.ops.append(GateOp(GateType.SWAP, (qubit1, qubit2)))
        return self

    # -- multi-controlled gates --------------------------------------------

    def mcx(
        self, controls: Sequence[int], target: int
    ) -> CircuitSpec:
        """Multi-controlled X gate."""
        self.ops.append(
            GateOp(GateType.MCX, (*tuple(controls), target))
        )
        return self

    def mcry(
        self, theta: float, controls: Sequence[int], target: int
    ) -> CircuitSpec:
        """Multi-controlled RY gate."""
        self.ops.append(
            GateOp(
                GateType.MCRY,
                (*tuple(controls), target),
                (theta,),
            )
        )
        return self

    # -- state preparation -------------------------------------------------

    def initialize(self, state: Sequence[float]) -> CircuitSpec:
        """Prepare the register in the given non-negative real state.

        Decomposes the state preparation into RY and CX gates using
        the Mottonen method so that all backends only need to handle
        elementary gates. The decomposition uses magnitudes via
        ``arctan2`` and therefore only encodes non-negative real
        amplitudes (e.g. QPAM probability amplitudes); signed or
        complex states are not supported.
        """
        state = np.asarray(state, dtype=float)
        n = self.num_qubits
        expected = 2**n
        if len(state) != expected:
            raise ValueError(
                f"State vector length {len(state)} does not match "
                f"the expected number of amplitudes "
                f"2**{n} = {expected}"
            )
        norm = np.linalg.norm(state)
        if norm < 1e-15:
            return self
        state = state / norm
        _apply_mottonen(self, state, n)
        return self

    # -- measurement -------------------------------------------------------

    def measure(self, qubit: int, clbit: int) -> CircuitSpec:
        self.ops.append(
            GateOp(GateType.MEASURE, (qubit,), clbits=(clbit,))
        )
        self.num_clbits = max(self.num_clbits, clbit + 1)
        return self

    def measure_all(self) -> CircuitSpec:
        """Measure every qubit into a classical bit of the same index."""
        for q in range(self.num_qubits):
            self.measure(q, q)
        return self

    # -- visual separator --------------------------------------------------

    def barrier(self) -> CircuitSpec:
        self.ops.append(GateOp(GateType.BARRIER, ()))
        return self


# ======================================================================
# Mottonen state-preparation decomposition (non-negative real states)
# ======================================================================


def _apply_mottonen(spec: CircuitSpec, state: np.ndarray, n: int):
    """Decompose a non-negative real state vector into RY and CX gates.

    Uses the Mottonen method: compute a tree of rotation angles,
    then apply uniformly controlled RY rotations from the most
    significant qubit down to the least significant.

    The qubit convention follows Qiskit's little-endian ordering:
    qubit 0 is the least significant bit of the state index.

    Angles are derived from amplitude magnitudes, so signed inputs
    are encoded as their absolute values.
    """
    angles_tree = _compute_angles(state, n)
    for level in range(n):
        target = n - 1 - level
        controls = list(range(target + 1, n))
        # Reverse controls so the UCR's recursive even/odd split
        # matches the angle indexing order.
        controls.reverse()
        thetas = angles_tree[level]
        _apply_ucry(spec, thetas, controls, target)


def _compute_angles(state: np.ndarray, n: int) -> list[list[float]]:
    """Compute the rotation angle tree for Mottonen decomposition.

    Level 0 targets the MSB (qubit n-1) with 1 angle; level k
    targets qubit n-1-k with 2^k angles.  Each angle splits a
    pair of amplitude sub-blocks via
    theta = 2 * arctan2(norm_lower, norm_upper).
    """
    all_angles = []
    for level in range(n):
        k = n - 1 - level
        stride = 2 ** (k + 1)
        half = stride // 2
        num_pairs = len(state) // stride
        angles = []
        for j in range(num_pairs):
            start = j * stride
            upper = state[start : start + half]
            lower = state[start + half : start + stride]
            norm_upper = np.linalg.norm(upper)
            norm_lower = np.linalg.norm(lower)
            if norm_upper + norm_lower < 1e-15:
                angles.append(0.0)
            else:
                angles.append(
                    2.0 * np.arctan2(norm_lower, norm_upper)
                )
        all_angles.append(angles)
    return all_angles


def _apply_ucry(
    spec: CircuitSpec,
    thetas: list[float],
    controls: list[int],
    target: int,
):
    """Apply a uniformly controlled RY rotation.

    Recursively decomposes into CX and RY gates:
      UCR_Y(theta_0, ..., theta_{2^k-1}) =
        UCR_Y(alpha_even)  @  CX(last_ctrl, target)
        @ UCR_Y(alpha_odd) @  CX(last_ctrl, target)

    where alpha_even[i] = (theta[2i] + theta[2i+1]) / 2
    and   alpha_odd[i]  = (theta[2i] - theta[2i+1]) / 2.

    Base case (no controls): a single RY(theta, target).
    """
    if not controls:
        # Base case: single rotation.
        if abs(thetas[0]) > 1e-15:
            spec.ry(thetas[0], target)
        return

    n = len(thetas)
    even = [
        (thetas[2 * i] + thetas[2 * i + 1]) / 2
        for i in range(n // 2)
    ]
    odd = [
        (thetas[2 * i] - thetas[2 * i + 1]) / 2
        for i in range(n // 2)
    ]
    last_ctrl = controls[-1]
    remaining = controls[:-1]

    _apply_ucry(spec, even, remaining, target)
    spec.cx(last_ctrl, target)
    _apply_ucry(spec, odd, remaining, target)
    spec.cx(last_ctrl, target)
