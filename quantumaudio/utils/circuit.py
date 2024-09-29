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

import qiskit

# ======================
# Circuit Preparation Utils
# ======================


def apply_x_at_index(qc: qiskit.QuantumCircuit, i: int) -> None:
    """This function is used to encode an index value into control qubits of a circuit.

    Args:
        qc: Qiskit Circuit
        i: Index position
    """
    if len(qc.qregs) != 2:
        _, creg, treg = qc.qregs
    else:
        _, treg = qc.qregs
        creg = []
    for reg_index, reg_qubit in enumerate(creg[:] + treg[:]):
        bit = (i >> reg_index) & 1
        if not bit:
            qc.x(reg_qubit)


def with_indexing(func: Callable) -> Callable:
    """Used as decorator with a value-setting operation.

    Args:
        func: A value-setting function to be decorated.

    Returns:
        The wrapped function with time indexing applied.
    """

    @wraps(func)  # added to fix docstrings not printing func
    def wrapper(*args, **kwargs):
        qc = kwargs.get("circuit")
        i = kwargs.get("index")
        qc.barrier()
        apply_x_at_index(qc, i)
        func(*args, **kwargs)
        apply_x_at_index(qc, i)

    return wrapper
