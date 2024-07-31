import numpy as np
import matplotlib.pyplot as plt
from typing import Union

# ======================
# Plotting Utils
# ======================

def plot_1d(
    samples: np.ndarray,
    title: Union[str, None] = None,
    label: tuple[str, str] = ("original", "reconstructed"),
) -> None:
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


def plot(
    samples: Union[np.ndarray, list[np.ndarray]],
    title: Union[str, None] = None,
    label: tuple[str, str] = ("original", "reconstructed"),
) -> None:
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