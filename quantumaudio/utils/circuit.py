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

import qiskit
from functools import wraps
from typing import Union, Callable, Optional

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
    bitstring = []
    for reg_index, reg_qubit in enumerate(creg[:] + treg[:]):
        bit = (i >> reg_index) & 1
        bitstring.append(bit)
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


def add_classical_register(
    qc: qiskit.QuantumCircuit, position: int, label: str
) -> None:
    """Adds a classical register to a quantum circuit and measures the
    corresponding quantum register.

    Args:
        qc: The quantum circuit to which the classical register will be added.
        position: The position of the quantum register in the quantum circuit.
        label: The label for the new classical register.
    """
    qreg = qc.qregs[position]
    creg = qiskit.ClassicalRegister(qreg.size, label)
    qc.add_register(creg)
    qc.measure(qreg, creg)


def measure(
    qc: qiskit.QuantumCircuit,
    labels: tuple[str, str, str] = ("ca", "cc", "ct"),
    position: Optional[int] = None,
) -> None:
    """Adds a barrier to the quantum circuit and classical registers at the
    corresponding quantum registers.

    Args:
        qc: The quantum circuit to which the barrier and measurements will be applied.
        labels: Labels for the classical registers corresponding to the measurements.
                                                 Defaults to ("ca", "cc", "ct").
        position: The position of the qubits to be measured. If None, all qubits are measured. Defaults to None.
    """
    value_pos, *index_pos = (
        range(len(qc.qregs)) if not position else reversed(position)
    )
    value_label, *index_labels = labels
    index_labels = index_labels[len(index_labels) - len(index_pos) :]
    add_classical_register(qc, value_pos, value_label)
    for i, pos in enumerate(index_pos):
        add_classical_register(qc, pos, index_labels[i])
