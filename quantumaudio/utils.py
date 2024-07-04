import numpy as np
import matplotlib.pyplot as plt
import ipywidgets
import qiskit_aer
import qiskit
from IPython.display import display, Audio, clear_output
import librosa
import soundfile as sf
from typing import Union, Callable, Optional, Any

# ======================
# Data processing utils
# ======================


def simulate_data(num_samples: int, num_channels: int = 1, seed: int = 42) -> np.ndarray:
    """Simulates sythetic data for quick testing and plots. Typically, Audio data
       contains several thousands of samples per second which is difficult to 
       visualise as circuit and plot" 

    Args:
        num_samples (int): The number of samples to generate.
        num_channels (int, optional): The number of channels for each sample. Defaults to 1.
        seed (int, optional): The seed for the random number generator. Defaults to 42.

    Returns:
        np.ndarray: A numpy array of simulated data.
    """
    np.random.seed(seed)
    data = np.random.rand(num_samples, num_channels)
    if num_channels == 1:
        data = data.squeeze()
    return data

def apply_index_padding(array: np.ndarray, num_index_qubits: int) -> np.ndarray:
    """Applies zero-padding to 1-D array based on the specified number of index
    qubits.

    Args:
        array (np.ndarray): The input array to be padded.
        num_index_qubits (int): The number of qubits to determine the padding length.

    Returns:
        np.ndarray: The padded array.
    """
    pad_length = (2 ** num_index_qubits) - array.shape[-1]
    if pad_length > 0:
        padding = [(0, 0) for _ in range(array.ndim)]
        padding[-1] = (0, pad_length)
        array = np.pad(array, padding, mode="constant")
    return array

def apply_padding(array: np.ndarray, num_qubits: (int,int)) -> np.ndarray:
    """Applies zero-padding to both dimensions of a 2-D array based on the
    specified number of index qubits.

    Args:
        array (np.ndarray): The input array to be padded.
        num_qubits (int,int): The padding length at each dimension is determined by
                              number of channel qubits and number of index qubits
                              respectively.

    Returns:
        np.ndarray: The padded array.
    """
    padding = []
    array_shape = array.shape
    for i in range(len(array_shape)):
        n_bits = num_qubits[i] if len(num_qubits) > i else num_qubits[0]
        pad_length = (2**n_bits) - array_shape[i]
        if pad_length > 0:
            padding.append((0, pad_length))
        else:
            padding.append((0, 0))
    while len(padding) < array.ndim:
        padding.append((0, 0))
    array = np.pad(array, padding, mode="constant")
    return array


def get_bit_depth(signal: np.ndarray) -> int:
    """Determines the bit depth of a given signal.

    Args:
        signal (np.ndarray): The input signal.

    Returns:
        int: The bit depth of the signal.
    """
    unique_values = np.unique(signal)
    num_levels = len(unique_values)
    bit_depth = get_qubit_count(num_levels)
    if not bit_depth:
        bit_depth = 1
    return bit_depth


def get_qubit_count(data_length: int) -> int:
    """Calculates the number of qubits required to represent a given data
    length.

    Args:
        data_length (int): The length of the data.

    Returns:
        int: The number of qubits needed to represent the data length.
    """
    num_qubits = int(np.ceil(np.log2(data_length)))
    return num_qubits


def is_within_range(arr: np.ndarray, min_val: float, max_val: float) -> bool:
    """Checks if all elements in the array are within the specified range.

    Args:
        arr (np.ndarray): The input array.
        min_val (float): The minimum value of the range.
        max_val (float): The maximum value of the range.

    Returns:
        bool: True if all elements are within the range, False otherwise.
    """
    return np.all((arr >= min_val) & (arr <= max_val))

def interleave_channels(array: np.ndarray) -> np.ndarray:
    """Interleaves the channels of a given array.

    Args:
        array (np.ndarray): The input array with shape (samples, channels).

    Returns:
        np.ndarray: A 1-dimensional array with interleaved channels.
    """
    return np.dstack(array).flatten()

def restore_channels(array: np.ndarray, num_channels: int) -> np.ndarray:
    """Restores the interleaved channels into their original form.

    Args:
        array (np.ndarray): The input array with interleaved channels.
        num_channels (int): The number of channels.

    Returns:
        np.ndarray: The array with shape (samples, channels).
    """
    return np.vstack([array[i::num_channels] for i in range(num_channels)])


# ======================
# Conversions
# ======================


def convert_to_probability_amplitudes(array: np.ndarray) -> tuple[float, np.ndarray]:
    """Converts an array to probability amplitudes.

    Args:
        array (np.ndarray): The input array.

    Returns:
        tuple[float, np.ndarray]: A tuple containing the norm and the array of probability amplitudes.
    """
    array = array.squeeze().astype(float)
    array = (array + 1) / 2
    norm = np.linalg.norm(array)
    if not norm:
        norm = 1
    probability_amplitudes = array / norm
    return norm, probability_amplitudes

def convert_to_angles(array: np.ndarray) -> np.ndarray:
    """Converts an array to angles using arcsin(sqrt((x + 1) / 2)).

    Args:
        array (np.ndarray): The input array. Values must be in the range [-1, 1].

    Returns:
        np.ndarray: The array of angles.
    """
    assert is_within_range(array, min_val=-1, max_val=1), "Data not in range"
    return np.arcsin(np.sqrt((array.astype(float) + 1) / 2))

def quantize(array: np.ndarray, qubit_depth: int) -> np.ndarray:
    """Quantizes the array to a given qubit depth.

    Args:
        array (np.ndarray): The input array.
        qubit_depth (int): The number of bits to quantize to.

    Returns:
        np.ndarray: The quantized array as integers.
    """
    values = array * (2 ** (qubit_depth - 1))
    return values.astype(int)

def convert_from_probability_amplitudes(probabilities: np.ndarray, norm: float, shots: int) -> np.ndarray:
    """Converts probability amplitudes to the original data range.

    Args:
        probabilities (np.ndarray): The array of probability amplitudes.
        norm (float): The normalization factor.
        shots (int): The number of measurement shots.

    Returns:
        np.ndarray: The array of original data values.
    """
    return 2 * norm * np.sqrt(probabilities / shots) - 1

def convert_from_angles(cosine_amps: np.ndarray, sine_amps: np.ndarray, inverted: bool = False) -> np.ndarray:
    """Converts angles back to the original data range.

    Args:
        cosine_amps (np.ndarray): The cosine amplitude array.
        sine_amps (np.ndarray): The sine amplitude array.
        inverted (bool, optional): If True, uses cosine amplitudes instead of sine amplitudes. Defaults to False.

    Returns:
        np.ndarray: The array of original data values.
    """
    total_amps = cosine_amps + sine_amps
    amps = sine_amps if not inverted else cosine_amps
    ratio = np.divide(amps, total_amps, out=np.zeros_like(amps), where=total_amps != 0)
    data = 2 * ratio - 1
    return data

def de_quantize(array: np.ndarray, bit_depth: int) -> np.ndarray:
    """De-quantizes the array from a given bit depth.

    Args:
        array (np.ndarray): The quantized array.
        bit_depth (int): The bit depth used for quantization.

    Returns:
        np.ndarray: The de-quantized array.
    """
    data = array / (2 ** (bit_depth - 1))
    return data


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


def get_counts(circuit: qiskit.QuantumCircuit, backend: Optional[str] = None, shots: int = 4000, 
    pad: bool = False) -> dict:
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


def execute(circuit: qiskit.QuantumCircuit, backend: Optional[str] = None, shots: int = 4000) -> qiskit.result.Result:
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

def add_classical_register(qc: qiskit.QuantumCircuit, position: int, label: str) -> None:
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


def measure(qc: qiskit.QuantumCircuit, labels: tuple[str, str, str] = ("ca", "cc", "ct"), position: Optional[int] = None) -> None:
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


# ======================
# Plotting Utils
# ======================


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
    display(circuit.draw("mpl", style="clifford"))

def plot_1d(samples: np.ndarray,
         title: Union[str, None] = None,
         label: tuple[str, str] = ("original", "reconstructed")) -> None:
    """Plots the given samples.

    Args:
        samples: The samples to plot.
        title: Title for the plot. Defaults to None.
        label: Labels for the samples. Defaults to ("original", "reconstructed").

    Returns:
        None
    """
    if not isinstance(samples, list):
        samples = [samples]
    if label and not isinstance(label, tuple):
        label = (label,)

    num_samples = samples[0].shape[-1]
    x_axis = np.arange(0, num_samples)

    for i, y_axis in enumerate(samples):
        plt.plot(x_axis, y_axis.squeeze(), label=None if not label else label[i])

    plt.xlabel("Index")
    plt.ylabel("Values")
    if label:
        plt.legend()
    if title:
        plt.title(title)
    plt.show()


def plot(samples: Union[np.ndarray, list[np.ndarray]],
         title: Union[str, None] = None,
         label: tuple[str, str] = ("original", "reconstructed")) -> None:
    """Plots the given samples.

    Args:
        samples: The samples to plot. Can be a single numpy array or a list of numpy arrays.
        title: Title for the plot. Defaults to None.
        label: Labels for the samples. Defaults to ("original", "reconstructed").

    Returns:
        None
    """
    if not isinstance(samples, list):
        samples = [samples]
    if label and not isinstance(label, tuple):
        label = (label,)

    num_samples = samples[0].shape[-1]
    num_channels = 1 if samples[0].ndim == 1 else samples[0].shape[-2]
    x_axis = np.arange(0, num_samples)

    if num_channels > 1:
        fig, axs = plt.subplots(num_channels, 1, figsize=(8, 8))
        for i, y_axis in enumerate(samples):
            for c in range(num_channels):
                axs[c].plot(
                    x_axis,
                    y_axis[c][:num_samples],
                    label=None if not label else label[i],
                )
                axs[c].set_xlabel("Index")
                axs[c].set_ylabel("Values")
                axs[c].set_title(f"channel {c+1}")
                if label:
                    axs[c].legend(loc="upper right")
                axs[c].grid(True)
        plt.tight_layout()

    else:
        for i, y_axis in enumerate(samples):
            plt.plot(x_axis, y_axis.squeeze(), label=None if not label else label[i])
            plt.xlabel("Index")
            plt.ylabel("Values")
            if label:
                plt.legend()

    if title:
        plt.title(title)
    plt.show()


def tune(obj: np.ndarray,
         function: callable,
         max_value: int = 2048,
         step: int = 10,
         name: str = "Shots",
         ref: np.ndarray = None,
         limit: int = None) -> None:
    """Sets up an interactive widget to tune parameters and visualize the
    function.

    Args:
        obj (np.ndarray): Original Audio data array.
        function (callable): The decode function.
        max_value (int, optional): The maximum value for the tuning parameter. Defaults to 2048.
        step (int, optional): The step size for the tuning parameter. Defaults to 10.
        name (str, optional): The name/description of the parameter. Defaults to "parameter".
        ref (np.ndarray, optional): Reference or comparison value. Defaults to None.
        limit (any, optional): Limit or constraint for the parameter. Defaults to None.

    Returns:
        ipywidgets.interactive
    """
    def plot_function(shots):
        y = function(circuit=obj, backend=None, shots=shots)
        x = np.arange(0, len(y))
        if isinstance(limit, int):
            x = x[:limit]
        plt.plot(x, y[: len(x)], label=f"Shots = {shots}")
        if isinstance(ref, np.ndarray):
            plt.plot(x, ref[: len(x)], label="Original")
        plt.xlabel("Shots")
        plt.ylabel("Values")
        plt.ylim(0, 1.5)
        plt.legend()
        plt.grid(True)
        plt.show()

    variable_slider = ipywidgets.IntSlider(
        value=1, min=1, max=max_value, step=step, description=name
    )
    return ipywidgets.interact(plot_function, shots=variable_slider)


def play(array: Union[list[float], list[int]], rate: int = 44100, autoplay: bool = False) -> None:
    """Display audio from an array of audio data.

    Parameters:
    array (list of float or int): Array containing audio data.
    rate (int, optional): Sampling rate of the audio data (default is 44100).
    autoplay (bool, optional): Whether to autoplay the audio (default is False).

    Returns:
    None
    """
    audio = Audio(data=array, rate=rate, autoplay=autoplay)
    display(audio)


# ======================
# Audio
# ======================


def get_chunks(file_path: str, sr: int = 22050, chunk_size: int = 256, mono: bool = True, preview: bool = False) -> None:
    """Generate audio chunks from a file.

    Parameters:
    file_path (str): Path to the audio file.
    sr (int, optional): Sampling rate (default is 22050).
    chunk_size (int, optional): Size of each chunk (default is 256).
    mono (bool, optional): Whether to load audio in mono (default is True).
    preview (bool, optional): Whether to preview each chunk (default is False).

    Returns:
    None
    """
    y, sr = librosa.load(file_path, sr=sr, mono=mono)
    if preview:
        play(array=y, rate=sr)
    print(f"Shape: {y.shape}")
    if y.ndim == 1:
        y = y.reshape(1, -1)
    print(
        f"Num samples: {y.shape[-1]}, Num channels: {y.shape[0]}, Sample rate: {sr}, Buffer size: {chunk_size}"
    )
    y_chunks = []
    for i in range(0, y.shape[-1], chunk_size):
        chunk = y[:, i : i + chunk_size]
        y_chunks.append(chunk)
    print(f"Number of chunks: {len(y_chunks)}")
    print(f"Shape per buffer: {y_chunks[0].shape}")
    return y_chunks, sr


def process(chunk : np.ndarray, scheme: Any, shots: int) -> np.ndarray:
    """Process a chunk of data according to a specified scheme.

    Parameters:
    chunk (np.ndarray): Data chunk to be processed.
    scheme (any): Processing scheme.
    shots (int): Number of shots.

    Returns:
    None
    """
    chunk = scheme.decode(scheme.encode(chunk,verbose=0), shots=shots)
    return chunk


def process_chunks(chunks: list[np.ndarray], scheme: Any, shots: int) -> list:
    """Process chunks of data in an iteration according to a specified scheme.

    Parameters:
    chunks (np.ndarray): Data chunks to be processed.
    scheme (any): Processing scheme.
    shots (int): Number of shots.

    Returns:
    None
    """
    processed_chunks = []
    for chunk in chunks:
        processed_chunk = process(chunk, scheme, shots)
        processed_chunks.append(processed_chunk)
    return processed_chunks


def tune_audio(
    obj: np.ndarray,
    scheme: Any,
    function: Callable,
    max_value: int = 8000,
    step: int = 10,
    name: str = "Shots",
    limit: Optional[int] = None,
    sr: int = 22050,
    offset: int = 0,
) -> None:
    """Tune audio parameters according to a specified function and scheme.

    Args:
        obj (np.ndarray): Original Audio data array.
        function (callable): The decode function.
        max_value (int, optional): Maximum value for tuning (default is 8000).
        step (int, optional): Step size for tuning (default is 10).
        name (str, optional): Name of the parameter being tuned (default is 'parameter').
        limit (int, optional): Limit for tuning, if any (default is None).
        sr (int, optional): Sampling rate (default is 22050).
        offset (int, optional): Offset for tuning (default is 0).

    Returns:
        ipywidgets.interactive
    """
    def plot_function(shots):
        y = function(chunks=obj[offset:limit], scheme=scheme, shots=shots)
        if y:
            y = np.concatenate(y)
        clear_output(wait=True)
        play(y, rate=sr, autoplay=True)

    variable_slider = ipywidgets.IntSlider(
        value=1,
        min=1,
        max=max_value,
        step=step,
        description=name,
        continuous_update=False,
    )
    return ipywidgets.interact(plot_function, shots=variable_slider)

def export_audio(processed_chunks: list[np.ndarray], sr: int, output_filepath: str = 'reconstructed_audio.wav') -> None:
    """
    Export processed audio chunks into a single WAV file.

    Parameters:
    processed_chunks (list of np.ndarray): List containing arrays of processed audio chunks.
    sr (int): Sampling rate of the audio data.
    output_filepath (str, optional): Filepath to save the reconstructed audio.

    Returns:
    None
    """
    output = np.concatenate(processed_chunks)
    sf.write(output_filepath, output, sr, format='WAV')
    print(output_filepath)