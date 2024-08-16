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
import qiskit_aer
import matplotlib.pyplot as plt
from typing import Union, Callable, Optional

# ======================
# Measurement
# ======================


def execute(
    circuit: qiskit.QuantumCircuit,
    backend: Optional[str] = None,
    shots: int = 4000,
) -> qiskit.result.Result:
    """Executes a quantum circuit using qiskit.execute.

    Args:
            circuit: A Qiskit Circuit.
            backend: A backend string compatible with qiskit.execute method
            shots  : Total number of times the quantum circuit is measured.

    Return:
            Qiskit Result object that contains metadata
    """
    if not backend:
        backend = qiskit_aer.AerSimulator()
    job = qiskit.execute(circuit, backend=backend, shots=shots)
    result = job.result()
    return result


def pad_counts(counts: Union[dict, qiskit.result.Counts]) -> dict:
    """Pads the counts to its full length covering all basis states.

    Args:
        counts: Counts dictionary

    Returns:
        counts: Padded counts dictionary
    """
    num_qubits = len(next(iter(counts)))
    all_states = [
        format(i, "0" + str(num_qubits) + "b") for i in range(2**num_qubits)
    ]
    complete_counts = {state: counts.get(state, 0) for state in all_states}
    return complete_counts


def get_counts(
    circuit: qiskit.QuantumCircuit,
    backend: Optional[str] = None,
    shots: int = 4000,
    pad: bool = False,
) -> dict:
    """Given a qiskit circuit, executes and returns counts dictionary.

    Args:
            circuit: A Qiskit Circuit.
            backend: A backend string compatible with qiskit.execute method
            shots  : Total number of times the quantum circuit is measured.
            pad: If True, applies padding to the counts dictionary.

    Return:
            Counts dictionary
    """
    if not backend:
        backend = qiskit_aer.AerSimulator()
    job = qiskit.execute(circuit, backend=backend, shots=shots)
    result = job.result()
    counts = pad_counts(result.get_counts()) if pad else result.get_counts()
    return counts


# ======================
# Preview Functions
# ======================


def print_num_qubits(
    num_qubits: tuple[int, ...], labels: tuple[str, ...]
) -> None:
    """Prints the number of qubits required and their allocation per label.

    Args:
        num_qubits: List of integers representing the number of qubits.
        labels: List of strings representing labels for each qubit allocation.

    """
    print(f"Number of qubits required: {sum(num_qubits)}\n")
    for i, qubits in enumerate(num_qubits):
        print(f"{qubits} for {labels[i]}")


def draw_circuit(circuit: qiskit.QuantumCircuit, decompose: int = 0) -> None:
    """Draws a quantum circuit diagram.

    Args:
        circuit: The quantum circuit to draw.
        decompose: Number of times to decompose the circuit. Defaults to 0.

    """
    for i in range(decompose):
        circuit = circuit.decompose()

    try:  # Display the plot inline in Jupyter Notebook
        display(circuit.draw("mpl", style="clifford"))
    except:  # Show the plot in a separate window (for terminal)
        circuit.draw("mpl", style="clifford")
        plt.show()
