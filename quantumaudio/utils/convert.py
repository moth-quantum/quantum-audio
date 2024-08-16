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
# ==============================================================================

import numpy as np

# ======================
# Conversions
# ======================


def convert_to_probability_amplitudes(
    array: np.ndarray,
) -> tuple[float, np.ndarray]:
    """Converts an array to probability amplitudes.

    Args:
        array: The input array.

    Returns:
        A tuple containing the norm and the array of probability amplitudes.
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
        array: The input array. Values must be in the range [-1, 1].

    Returns:
        The array of angles.
    """
    assert is_within_range(array, min_val=-1, max_val=1), "Data not in range"
    return np.arcsin(np.sqrt((array.astype(float) + 1) / 2))


def quantize(array: np.ndarray, qubit_depth: int) -> np.ndarray:
    """Quantizes the array to a given qubit depth.

    Args:
        array: The input array.
        qubit_depth: The number of bits to quantize to.

    Returns:
        The quantized array as integers.
    """
    values = array * (2 ** (qubit_depth - 1))
    return values.astype(int)


def convert_from_probability_amplitudes(
    probabilities: np.ndarray, norm: float, shots: int
) -> np.ndarray:
    """Converts probability amplitudes to the original data range.

    Args:
        probabilities: The array of probability amplitudes.
        norm: The normalization factor.
        shots: The number of measurement shots.

    Returns:
        The array of original data values.
    """
    return 2 * norm * np.sqrt(probabilities / shots) - 1


def convert_from_angles(
    cosine_amps: np.ndarray, sine_amps: np.ndarray, inverted: bool = False
) -> np.ndarray:
    """Converts angles back to the original data range.

    Args:
        cosine_amps: The cosine amplitude array.
        sine_amps: The sine amplitude array.
        inverted: If True, uses cosine amplitudes instead of sine amplitudes. Defaults to False.

    Returns:
        The array of original data values.
    """
    total_amps = cosine_amps + sine_amps
    amps = sine_amps if not inverted else cosine_amps
    ratio = np.divide(
        amps, total_amps, out=np.zeros_like(amps), where=total_amps != 0
    )
    data = 2 * ratio - 1
    return data


def de_quantize(array: np.ndarray, bit_depth: int) -> np.ndarray:
    """De-quantizes the array from a given bit depth.

    Args:
        array: The quantized array.
        bit_depth: The bit depth used for quantization.

    Returns:
        The de-quantized array.
    """
    data = array / (2 ** (bit_depth - 1))
    return data


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
