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

from functools import wraps
from typing import Callable

from quantumaudio.backends.core.circuit import CircuitSpec

# =========================
# Circuit Preparation Utils
# =========================


def apply_x_at_index(
    spec: CircuitSpec, scheme, i: int
) -> None:
    """Encode an index value into control qubits of a circuit.

    Applies X gates to each control qubit whose corresponding
    bit in *i* is 0, preparing the control state for a
    multi-controlled operation at index *i*.

    Args:
        spec: The circuit specification.
        scheme: The scheme instance (provides register ranges).
        i: Index position.
    """
    control_qubits = []
    if hasattr(scheme, "_channel_range"):
        ch_start, ch_size = scheme._channel_range
        control_qubits.extend(range(ch_start, ch_start + ch_size))
    idx_start, idx_size = scheme._index_range
    control_qubits.extend(range(idx_start, idx_start + idx_size))

    for reg_index, qubit in enumerate(control_qubits):
        bit = (i >> reg_index) & 1
        if not bit:
            spec.x(qubit)


def with_indexing(func: Callable) -> Callable:
    """Used as decorator with a value-setting operation.

    Args:
        func: A value-setting function to be decorated.

    Returns:
        The wrapped function with time indexing applied.
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        spec = kwargs.get("circuit")
        i = kwargs.get("index")
        spec.barrier()
        apply_x_at_index(spec, self, i)
        func(self, *args, **kwargs)
        apply_x_at_index(spec, self, i)

    return wrapper
