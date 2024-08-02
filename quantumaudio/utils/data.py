import numpy as np

# ======================
# Data processing utils
# ======================


def simulate_data(
    num_samples: int, num_channels: int = 1, seed: int = 42
) -> np.ndarray:
    """Simulates sythetic data for quick testing and plots. Typically, Audio data
       contains several thousands of samples per second which is difficult to
       visualise as circuit and plot"

    Args:
        num_samples: The number of samples to generate.
        num_channels: The number of channels for each sample. Defaults to 1.
        seed: The seed for the random number generator. Defaults to 42.

    Returns:
        A numpy array of simulated data.
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
        array: The input array to be padded.
        num_index_qubits: The number of qubits to determine the padding length.

    Returns:
        The padded array.
    """
    pad_length = (2**num_index_qubits) - array.shape[-1]
    if pad_length > 0:
        padding = [(0, 0) for _ in range(array.ndim)]
        padding[-1] = (0, pad_length)
        array = np.pad(array, padding, mode="constant")
    return array


def apply_padding(array: np.ndarray, num_qubits: (int, int)) -> np.ndarray:
    """Applies zero-padding to both dimensions of a 2-D array based on the
    specified number of index qubits.

    Args:
        array: The input array to be padded.
        num_qubits: The padding length at each dimension is determined by
                              number of channel qubits and number of index qubits
                              respectively.

    Returns:
        The padded array.
    """
    padding = []
    if array.ndim == 1:
        array = array.reshape(1, -1)
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
        signal: The input signal.

    Returns:
        The bit depth of the signal.
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
        data_length: The length of the data.

    Returns:
        The number of qubits needed to represent the data length.
    """
    num_qubits = int(np.ceil(np.log2(data_length)))
    return num_qubits


def interleave_channels(array: np.ndarray) -> np.ndarray:
    """Interleaves the channels of a given array.

    Args:
        array: The input array with shape (samples, channels).

    Returns:
        A 1-dimensional array with interleaved channels.
    """
    return np.dstack(array).flatten()


def restore_channels(array: np.ndarray, num_channels: int) -> np.ndarray:
    """Restores the interleaved channels into their original form.

    Args:
        array: The input array with interleaved channels.
        num_channels: The number of channels.

    Returns:
        The array with shape (samples, channels).
    """
    return np.vstack([array[i::num_channels] for i in range(num_channels)])
