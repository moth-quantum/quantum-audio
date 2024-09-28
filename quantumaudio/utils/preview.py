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
