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

"""Backend abstract base class and registry."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import numpy as np

from quantumaudio.backends.core.circuit import CircuitSpec
from quantumaudio.backends.core.result import UnifiedResult


class Backend(ABC):
    """Interface that every quantum backend must implement."""

    name: str

    # Convention used by ``statevector()`` to index basis states.
    # ``"little"`` (Qiskit-style): qubit 0 is the least significant bit,
    # so basis state index ``i`` written as ``format(i, f"0{n}b")`` has
    # q0 on the right. ``"big"`` (Cirq, PennyLane): qubit 0 is the most
    # significant bit, so the bitstring must be reversed to match the
    # counts convention emitted by ``run()``. CUDA-Q is mixed: its
    # ``get_state()`` is little-endian even though ``sample()`` is
    # big-endian, so the backend declares ``"little"`` here.
    _statevector_endian: str = "little"

    @abstractmethod
    def build_circuit(self, spec: CircuitSpec) -> Any:
        """Translate a CircuitSpec into the backend's native circuit."""

    @abstractmethod
    def run(
        self, native_circuit: Any, shots: int = 1024
    ) -> UnifiedResult:
        """Execute a native circuit and return a UnifiedResult."""

    @abstractmethod
    def statevector(self, native_circuit: Any) -> np.ndarray:
        """Return the exact statevector (simulator only)."""

    def run_spec(
        self, spec: CircuitSpec, shots: int = 1024
    ) -> UnifiedResult:
        """Convenience: build and run in one call."""
        native = self.build_circuit(spec)
        return self.run(native, shots)

    def statevector_counts(
        self, native_circuit: Any, shots: int = 1024
    ) -> dict[str, int]:
        """Synthesize a counts dict from exact statevector amplitudes.

        Squares the amplitudes and scales by ``shots`` so downstream
        decoders that consume counts (the ones built around
        ``shots``-normalised probability extraction) behave as if the
        circuit had been sampled, but without shot noise.

        Returns a counts dict keyed in the same little-endian convention
        as ``run()`` emits.
        """
        sv = self.statevector(native_circuit)
        n_bits = round(np.log2(len(sv)))
        probs = np.abs(sv) ** 2
        counts: dict[str, int] = {}
        for i, p in enumerate(probs):
            c = round(float(p) * shots)
            if c == 0:
                continue
            key = format(i, f"0{n_bits}b")
            if self._statevector_endian == "big":
                key = key[::-1]
            counts[key] = c
        return counts


class BackendRegistry:
    """Singleton that tracks available backends."""

    _instance: BackendRegistry | None = None
    _backends: dict[str, type[Backend]]

    def __new__(cls) -> BackendRegistry:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._backends = {}
        return cls._instance

    def register(self, name: str, cls_: type[Backend]) -> None:
        self._backends[name] = cls_

    def get(self, name: str) -> Backend:
        """Instantiate and return a backend by name."""
        if name not in self._backends:
            available = ", ".join(self._backends) or "(none)"
            raise KeyError(
                f"Backend {name!r} not available. "
                f"Installed: {available}"
            )
        return self._backends[name]()

    def available(self) -> list[str]:
        """Return names of all registered backends."""
        return list(self._backends)


registry = BackendRegistry()
