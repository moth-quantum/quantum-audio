import qiskit
import qiskit_aer
import matplotlib.pyplot as plt
from typing import Union, Callable, Optional

# ------------------- Measurement ---------------------------

def execute(
    circuit: qiskit.QuantumCircuit, backend: Optional[str] = None, shots: int = 4000
) -> qiskit.result.Result:
    """Executes a quantum circuit using qiskit.execute.

    Args:
            circuit: A Qiskit Circuit.
            backend: A backend string compatible with qiskit.execute method
            shots  : Total number of times the quantum circuit is measured.
    Return:
            qiskit.result.Result: Result object that contains metadata
    """
    if not backend:
        backend = qiskit_aer.AerSimulator()
    job = qiskit.execute(circuit, backend=backend, shots=shots)
    result = job.result()
    return result

def pad_counts(counts: Union[dict, qiskit.result.Counts]) -> dict:
    """Pads the counts to its full length covering all basis states.

    Args:
        counts (dict, qiskit.result.Counts): counts dictionary

    Returns:
        counts: Padded counts dictionary
    """
    num_qubits = len(next(iter(counts)))
    all_states = [format(i, "0" + str(num_qubits) + "b") for i in range(2**num_qubits)]
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
            counts: Dictionary
    """
    if not backend:
        backend = qiskit_aer.AerSimulator()
    job = qiskit.execute(circuit, backend=backend, shots=shots)
    result = job.result()
    counts = pad_counts(result.get_counts()) if pad else result.get_counts()
    return counts

# ------------------- Preview Functions ---------------------------

def print_num_qubits(num_qubits: tuple[int, ...], labels: tuple[str, ...]) -> None:
    """Prints the number of qubits required and their allocation per label.

    Args:
        num_qubits (List[int]): List of integers representing the number of qubits.
        labels (List[str]): List of strings representing labels for each qubit allocation.

    Returns:
        None
    """
    print(f"Number of qubits required: {sum(num_qubits)}\n")
    for i, qubits in enumerate(num_qubits):
        print(f"{qubits} for {labels[i]}")
    print("\n")


def draw_circuit(circuit: qiskit.QuantumCircuit, decompose: int = 0) -> None:
    """Draws a quantum circuit diagram.

    Args:
        circuit (QuantumCircuit): The quantum circuit to draw.
        decompose (int, optional): Number of times to decompose the circuit. Defaults to 0.

    Returns:
        None
    """
    for i in range(decompose):
        circuit = circuit.decompose()

    try: # Display the plot inline in Jupyter Notebook
        display(circuit.draw("mpl", style="clifford"))
    except: # Show the plot in a separate window (for terminal)
        circuit.draw("mpl", style="clifford")
        plt.show()