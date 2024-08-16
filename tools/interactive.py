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

import ipywidgets
from IPython.display import display, Audio, clear_output
import numpy as np
from typing import Union, Any, Optional, Callable
import matplotlib.pyplot as plt
from . import audio, stream

# ======================
# Notebook Utils
# ======================

def tune(
    obj: np.ndarray,
    function: Callable,
    max_value: int = 2048,
    step: int = 10,
    name: str = "Shots",
    ref: np.ndarray = None,
    limit: int = None,
) -> None:
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
            plt.plot(x, ref.squeeze()[: len(x)], label="Original")
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


def play(
    array: Union[list[float], list[int]], rate: int = 44100, autoplay: bool = False
) -> None:
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
        y = function(chunks=obj[offset:limit], scheme=scheme, shots=shots, show_progress=False)
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