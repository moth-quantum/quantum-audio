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
