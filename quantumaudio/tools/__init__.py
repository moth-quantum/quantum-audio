from .stream import stream_data
from .plot import plot

from typing import Optional
import numpy as np

np.random.seed(42)


def test_signal(
    num_channels: int = 1, num_samples: int = 8, seed: Optional[int] = None
) -> np.ndarray:
    """Simulates sythetic data for quick testing and plots. Typically, Audio data
       contains several thousands of samples per second which is difficult to
       visualise as circuit and plot"

    Args:
        num_channels: The number of channels for each sample. Defaults to 1.
        num_samples: The number of samples to generate.
        seed: The seed for the random number generator. Defaults to 42.

    Returns:
        A numpy array of simulated data.
    """
    if seed:
        np.random.seed(seed)
    data = np.random.rand(num_channels, num_samples)
    data = 2.0 * data - 1.0
    if num_channels == 1:
        data = data.squeeze()
    return data


__all__ = ["plot", "stream", "stream_data", "test_signal"]
