import qiskit
import qiskit_aer
import matplotlib.pyplot as plt
from typing import Union, Callable, Optional

# ======================
# Quantum Computing Utils
# ======================

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


def apply_x_at_index(qc: qiskit.QuantumCircuit, i: int) -> None:
    """This function is used to encode an index as control qubits to a circuit.

    Args:
        circuit: Qiskit Circuit
        index: Index position
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
        func (Callable): A value-setting function to be decorated.

    Returns:
        Callable: The wrapped function with time indexing applied.
    """

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
        qc (QuantumCircuit): The quantum circuit to which the classical register will be added.
        position (int): The position of the quantum register in the quantum circuit.
        label (str): The label for the new classical register.

    Returns:
        None
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
        qc (QuantumCircuit): The quantum circuit to which the barrier and measurements will be applied.
        labels (tuple[str, str, str], optional): Labels for the classical registers corresponding to the measurements.
                                                 Defaults to ("ca", "cc", "ct").
        position (int, optional): The position of the qubits to be measured. If None, all qubits are measured. Defaults to None.

    Returns:
        None
    """
    value_pos, *index_pos = range(len(qc.qregs)) if not position else reversed(position)
    value_label, *index_labels = labels
    index_labels = index_labels[len(index_labels) - len(index_pos) :]
    add_classical_register(qc, value_pos, value_label)
    for i, pos in enumerate(index_pos):
        add_classical_register(qc, pos, index_labels[i])


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