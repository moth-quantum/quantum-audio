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

"""
========
Overview
========

This subpackage contains the following tools that extends the functionality of core package:

- **plot**: Functions to plot and compare signals with any number of channels.
- **stream**: Functions to efficiently process long arrays as chunks.
"""

from .stream import stream_data
from .plot import plot

from typing import Optional
import numpy as np

np.random.seed(42)


def test_signal(
    num_samples: int = 8, num_channels: int = 1, seed: Optional[int] = None
) -> np.ndarray:
    """Simulates sythetic data for quick testing and plots. Typically, Audio data
    contains several thousands of samples per second which is difficult to
    visualise as circuit and plot.

    Args:
        num_channels: The number of channels for each sample. Defaults to 1.
        num_samples: The number of samples to generate.
        seed: The seed for the random number generator. Defaults to 42.

    Returns:
        A `numpy` array of simulated data.
    """
    if seed:
        np.random.seed(seed)
    data = np.random.rand(num_channels, num_samples)
    data = 2.0 * data - 1.0
    if num_channels == 1:
        data = data.squeeze()
    return data


__all__ = ["plot", "stream", "stream_data", "test_signal"]
