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

import matplotlib.pyplot as plt
import qiskit

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
        print(f"{qubits} qubits for {labels[i]}")


def draw_circuit(circuit: qiskit.QuantumCircuit, decompose: int = 0) -> None:
    """Draws a quantum circuit diagram.

    Args:
        circuit: The quantum circuit to draw.
        decompose: Number of times to decompose the circuit. Defaults to 0.

    """
    for _i in range(decompose):
        circuit = circuit.decompose()

    fig = circuit.draw("mpl", style="clifford")

    try:  # Check if the code is running in Jupyter Notebook
        display(fig)
    except NameError:
        plt.show()
