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

from typing import Any, Callable, Optional, Union

import ipywidgets
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import Audio, clear_output, display, HTML

# ======================
# Notebook Utils
# ======================


def tune(
    obj: Any,
    function: Callable,
    max_value: int = 2048,
    step: int = 10,
    name: str = "Shots",
    ref: np.ndarray = None,
    limit: Optional[int] = None,
    figsize: tuple[int, int] = (10, 5),
) -> None:
    """Sets up an interactive widget to tune parameters and visualize the
    function.

    Args:
        obj: Encoded circuit.
        function: The decode function.
        max_value: The maximum value for the tuning parameter. Defaults to 2048.
        step: The step size for the tuning parameter. Defaults to 10.
        name: The name/description of the parameter. Defaults to "parameter".
        ref: Reference or comparison value. Defaults to None.
        limit: Limit or constraint for the parameter. Defaults to None.

    Returns:
        ipywidgets.interactive
    """

    def plot_function(shots):
        y = function(circuit=obj, backend=None, shots=shots)
        x = np.arange(0, len(y))
        plt.figure(figsize=figsize)
        if isinstance(limit, int):
            x = x[:limit]
        plt.plot(x, y[: len(x)], label=f"Measuring {shots} times")
        if isinstance(ref, np.ndarray):
            plt.plot(x, ref.squeeze()[: len(x)], label="Original")
        plt.xlabel("Shots")
        plt.ylabel("Values")
        plt.ylim(-1.0, 1.0)
        plt.legend(fontsize=14)
        plt.grid(True)
        plt.show()

    variable_slider = ipywidgets.IntSlider(
        value=1,
        min=1,
        max=max_value,
        step=step,
        description=name,
        layout=ipywidgets.widgets.Layout(width="600px"),
    )
    return ipywidgets.interact(plot_function, shots=variable_slider)


def play(
    array: Union[list[float], list[int]],
    rate: int = 44100,
    autoplay: bool = False,
) -> None:
    """Display audio from an array of audio data.

    Args:
        array: Array containing audio data.
        rate: Sampling rate of the audio data (default is 44100).
        autoplay: Whether to autoplay the audio (default is False).

    Returns:
        None
    """
    audio = Audio(data=array, rate=rate, autoplay=autoplay)
    display(audio)


def tune_audio(
    obj: Any,
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
        obj: Audio Chunks.
        function: The decode function.
        max_value: Maximum value for tuning (default is 8000).
        step: Step size for tuning (default is 10).
        name: Name of the parameter being tuned (default is 'parameter').
        limit: Limit for tuning, if any (default is None).
        sr: Sampling rate (default is 22050).
        offset: Offset for tuning (default is 0).

    Returns:
        ipywidgets.interactive
    """

    def plot_function(shots):
        y = function(
            chunks=obj[offset:limit],
            scheme=scheme,
            shots=shots,
            verbose=False,
        )
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

def compare_audio(path_1, path_2):
    """
    Display two audio files side by side in Jupyter Notebook for comparison.

    Args:
        path_1 (str): Path to the first audio file.
        path_2 (str): Path to the second audio file.

    Returns:
        None
    """
    audio1 = Audio(path_1)
    audio2 = Audio(path_2)
    display(HTML(f"""
    <div style="display: flex; gap: 20px;">
        <div>{audio1._repr_html_()}</div>
        <div>{audio2._repr_html_()}</div>
    </div>
    """))