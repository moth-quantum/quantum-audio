import numpy as np

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


def convert_from_probability_amplitudes(
    probabilities: np.ndarray, norm: float, shots: int
) -> np.ndarray:
    """Converts probability amplitudes to the original data range.

    Args:
        probabilities (np.ndarray): The array of probability amplitudes.
        norm (float): The normalization factor.
        shots (int): The number of measurement shots.

    Returns:
        np.ndarray: The array of original data values.
    """
    return 2 * norm * np.sqrt(probabilities / shots) - 1


def convert_from_angles(
    cosine_amps: np.ndarray, sine_amps: np.ndarray, inverted: bool = False
) -> np.ndarray:
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
# Assertions
# ======================

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