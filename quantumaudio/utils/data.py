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

import numpy as np
from typing import Union

# ======================
# Assertions
# ======================


def is_within_range(arr: np.ndarray, min_val: float, max_val: float) -> bool:
    """Checks if all elements in the array are within the specified range.

    Args:
        arr: The input array.
        min_val: The minimum value of the range.
        max_val: The maximum value of the range.

    Returns:
        True if all elements are within the range, False otherwise.
    """
    return np.all((arr >= min_val) & (arr <= max_val))


def validate_data(data: Union[list, tuple, np.ndarray]) -> None:
    """Ensure the input data is a `numpy` array and that its values
    are within the digital audio range: -1.0 to 1.0.

    Args:
        data: Input data array.
    """
    if not isinstance(data, np.ndarray):
        raise TypeError("Input data must be a `numpy` array")
    if not is_within_range(data, min_val=-1.0, max_val=1.0):
        raise ValueError("Data not in the digital audio range (-1.0 to 1.0).")


# ==============
# Decoding utils
# ==============


def split_string(input_str, lengths):
    """Splits the input string into segments based on the specified lengths.

    Args:
        input_str: The string to be split.
        lengths: A list of integers representing the lengths of each segment.

    Returns:
        A list of substrings split according to the specified lengths.
    """
    assert len(input_str) == sum(
        lengths
    ), "Sum of qubits doesn't match the state length"
    res = []
    start = 0

    for length in lengths:
        # Slicing the string and appending to the result list
        res.append(input_str[start : start + length])
        start += length

    return res


# ======================
# Data processing utils
# ======================


def apply_index_padding(
    array: np.ndarray, num_index_qubits: int
) -> np.ndarray:
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
