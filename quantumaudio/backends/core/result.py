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

"""Unified result type that normalises output across backends."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from quantumaudio.backends._optional import require


@dataclass
class UnifiedResult:
    """Backend-agnostic execution result.

    Every backend produces one of these so that downstream code never
    has to care which framework ran the circuit.
    """

    counts: dict[str, int]
    shots: int
    backend_name: str
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.shots <= 0:
            raise ValueError(
                f"shots must be positive, got {self.shots}. "
                "Statevector-only execution should not produce a "
                "UnifiedResult."
            )

    def probabilities(self) -> dict[str, float]:
        """Return the probability distribution over bitstrings."""
        return {k: v / self.shots for k, v in self.counts.items()}

    def probabilities_array(self) -> np.ndarray:
        """Return probabilities as a dense array indexed by integer
        bitstring value."""
        if not self.counts:
            return np.array([])
        n_bits = len(next(iter(self.counts)))
        probs = np.zeros(2**n_bits)
        for bitstring, count in self.counts.items():
            probs[int(bitstring, 2)] = count / self.shots
        return probs

    def marginal(self, qubits: list[int]) -> UnifiedResult:
        """Marginalise the result over the given qubit indices."""
        if not self.counts:
            return UnifiedResult(
                {}, self.shots, self.backend_name, self.metadata
            )
        n_bits = len(next(iter(self.counts)))
        new_counts: dict[str, int] = {}
        for bitstring, count in self.counts.items():
            # Qubits are indexed from the right in the bitstring.
            new_key = "".join(
                bitstring[n_bits - 1 - q]
                for q in sorted(qubits, reverse=True)
            )
            new_counts[new_key] = (
                new_counts.get(new_key, 0) + count
            )
        return UnifiedResult(
            new_counts, self.shots, self.backend_name, self.metadata
        )

    def to_qiskit_result(self):
        """Construct a ``qiskit.result.Result`` for compatibility with
        code that does isinstance checks on Qiskit result types."""
        require("qiskit", extras_name="qiskit")
        from qiskit.result import Result  # noqa: PLC0415
        from qiskit.result.models import (  # noqa: PLC0415
            ExperimentResult,
            ExperimentResultData,
        )

        if self.counts:
            n_bits = len(next(iter(self.counts)))
            hex_width = (n_bits + 3) // 4
            hex_counts = {
                "0x"
                + format(int(k, 2), f"0{hex_width}x"): v
                for k, v in self.counts.items()
            }
        else:
            hex_counts = {}
            n_bits = 0

        exp_data = ExperimentResultData(counts=hex_counts)
        exp_result = ExperimentResult(
            shots=self.shots,
            success=True,
            data=exp_data,
            header={
                "metadata": self.metadata,
                "memory_slots": n_bits,
            },
        )
        return Result(
            backend_name=self.backend_name,
            backend_version="0.0.0",
            qobj_id="quantumaudio-backends",
            job_id="quantumaudio-backends",
            success=True,
            results=[exp_result],
        )
