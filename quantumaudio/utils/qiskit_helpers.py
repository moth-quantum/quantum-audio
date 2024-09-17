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

from typing import Union

import matplotlib.pyplot as plt
import qiskit
import qiskit_aer
from qiskit import transpile
from qiskit.primitives import PrimitiveResult, SamplerPubResult

# ======================
# Measurement
# ======================


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


def execute(circuit, backend=None, shots=4000, memory=False):
    """
    Executes a quantum circuit on a given backend and return the results.

    Args:
        circuit: The quantum circuit to be executed.
        backend: The backend on which to run the circuit. If None, the default backend `qiskit_aer.AerSimulator()` is used.
        shots: Total number of times the quantum circuit is measured.
        memory: Whether to return the memory (quantum state) of each shot.

    Returns:
        Result: The result of the execution, containing the counts and other metadata.
    """
    backend = qiskit_aer.AerSimulator() if not backend else backend
    circuit = transpile(circuit, backend)
    job = backend.run(circuit, shots=shots, memory=memory)
    result = job.result()
    return result


def get_counts(results_obj, result_id=0):
    """
    Extract counts from a results object.

    Args:
        results_obj: An instance of `PrimitiveResult` or `Result` object from which to extract counts.
        result_id: The index of the result to extract if the results object contains multiple results.

    Returns:
        counts: The counts of measurements from the results object.
    """
    counts = {}

    if isinstance(results_obj, PrimitiveResult):
        results_obj = results_obj[result_id]

    if isinstance(results_obj, SamplerPubResult):
        counts = results_obj.data.meas.get_counts()

    elif isinstance(results_obj, qiskit.result.Result):
        counts = results_obj.get_counts()

    else:
        raise TypeError("Unsupported result object type.")

    return counts


def get_metadata(results_obj, result_id=0):
    """
    Extract metadata from a results object.

    Args:
        results_obj: An instance of `PrimitiveResult` or `Result` object from which to extract metadata.
        result_id: The index of the result to extract if the results object contains multiple results.

    Returns:
        metadata: The metadata associated with the result.
    """
    metadata = {}

    if isinstance(results_obj, PrimitiveResult):
        results_obj = results_obj[result_id]

    if isinstance(results_obj, SamplerPubResult):
        metadata = results_obj.metadata["circuit_metadata"]
        metadata["shots"] = results_obj.metadata["shots"]

    elif isinstance(results_obj, qiskit.result.Result):
        metadata = results_obj.results[result_id].header.metadata
        metadata["shots"] = results_obj.results[result_id].shots

    else:
        raise TypeError("Unsupported result object type.")

    return metadata


def get_counts_and_metadata(results_obj, result_id=0):
    """
    Extract counts and metadata from a results object.

    Args:
        results_obj: An instance of `PrimitiveResult` or `Result` object from which to extract counts and metadata.
        result_id: The index of the result to extract if the results object if it contains multiple results.

    Returns:
        counts: The counts of measurements from the results object.
        metadata: The metadata associated with the result.
    """
    counts = get_counts(results_obj, result_id)
    metadata = get_metadata(results_obj, result_id)
    return counts, metadata


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
    for _i in range(decompose):
        circuit = circuit.decompose()

    fig = circuit.draw("mpl", style="clifford")

    try:  # Check if the code is running in Jupyter Notebook
        display(fig)
    except NameError:
        plt.show()
