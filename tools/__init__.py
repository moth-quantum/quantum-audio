from .plot import plot
from . import audio
import numpy as np

def simulate_data(
    num_samples: int, num_channels: int = 1, seed: int = 42
) -> np.ndarray:
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