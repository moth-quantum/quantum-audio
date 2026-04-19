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

"""Framework-agnostic backend layer for quantumaudio.

This subpackage provides a backend abstraction that allows quantum
circuits built by quantumaudio schemes to be executed on different
quantum frameworks (Qiskit, Cirq, and others).
"""

from quantumaudio.backends._optional import is_available, require
from quantumaudio.backends.core import (
    CircuitSpec,
    GateOp,
    GateType,
    UnifiedResult,
    Backend,
    registry,
)

# Trigger auto-registration of installed backends.
import quantumaudio.backends.providers  # noqa: F401


def available_backends() -> list[str]:
    """Return names of all backends whose dependencies are installed."""
    return registry.available()


def get_backend(name: str = "qiskit") -> Backend:
    """Instantiate and return a backend by name."""
    return registry.get(name)


__all__ = [
    "Backend",
    "CircuitSpec",
    "GateOp",
    "GateType",
    "UnifiedResult",
    "available_backends",
    "get_backend",
    "is_available",
    "registry",
    "require",
]
