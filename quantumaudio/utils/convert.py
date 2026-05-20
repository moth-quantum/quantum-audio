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

import numbers

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
    return float(norm), probability_amplitudes


def convert_to_angles(array: np.ndarray) -> np.ndarray:
    """Converts an array of values to angles.
    The conversion is done using the formula:

    `arcsin(sqrt((x + 1) / 2))`

    Args:
        array: The input array. Values must be in the range [-1, 1].

    Returns:
        The array of angles.
    """
    return np.arcsin(np.sqrt((array.astype(float) + 1) / 2))


def quantize(array: np.ndarray, qubit_depth: int) -> np.ndarray:
    """Quantizes the array to a given qubit depth.

    Values outside the representable signed-integer range
    ``[-2**(qubit_depth - 1), 2**(qubit_depth - 1) - 1]`` are saturated
    rather than wrapped, mirroring the standard audio-clipping
    convention. Without this, an input of ``+1.0`` at ``qubit_depth=3``
    would produce integer ``+4``, which does not fit in a 3-bit signed
    register and wraps to ``-4`` (decoded ``-1.0``): a sign-flip glitch
    on every peak sample.

    Args:
        array: The input array.
        qubit_depth: The number of bits to quantize to. Must be an
            integer >= 1.

    Returns:
        The quantized array as integers.

    Raises:
        ValueError: If ``qubit_depth`` is not an integer >= 1.
    """
    if (
        not isinstance(qubit_depth, numbers.Integral)
        or isinstance(qubit_depth, bool)
        or qubit_depth < 1
    ):
        raise ValueError(
            f"qubit_depth must be an integer >= 1, got {qubit_depth!r}."
        )
    # Coerce to Python int so the arithmetic below cannot overflow a
    # narrow NumPy integer dtype (e.g. ``np.uint8``).
    qubit_depth = int(qubit_depth)
    scale = 2 ** (qubit_depth - 1)
    values = array * scale
    return np.clip(values, -scale, scale - 1).astype(np.int64)


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
