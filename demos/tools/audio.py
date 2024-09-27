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

from typing import Any
import numpy.typing as np

from quantumaudio.tools import stream
from .audio_io import *

# ======================
# Export Helper function
# ======================


def stream_audio(
    file_path: str,
    scheme: Any,
    shots: int = 8000,
    sr: int = 22050,
    mono: bool = True,
    chunk_size: int = 256,
    verbose: bool = False,
) -> np.NDArray:
    """Convert audio file into array reconstructed from quantum audio using a specified scheme.

    Parameters:
    file_path: Path to the audio file to be converted.
    scheme: Quantum Audio scheme to be used.
    shots: Number of shots for quantum audio measurement. Default is 8000.
    sr: Sampling rate of the audio data. Default is 22050.
    mono: Whether to convert audio to mono. Default is True.
    chunk_size: Size of each chunk for processing. Default is 256.
    verbose: Whether to print additional information. Default is False.

    Returns:
    np.ndarray, int
    """
    digital_audio, sr = read(file_path=file_path, sr=sr, mono=mono)
    print(f"Sample Rate: {sr}")
    quantum_audio = stream.stream_data(
        data=digital_audio,
        scheme=scheme,
        shots=shots,
        chunk_size=chunk_size,
        verbose=verbose,
    )
    return quantum_audio, sr


# ======================
# Process and Save
# ======================


def save_audio(
    file_path: str,
    scheme: Any,
    sr: int = 22050,
    mono: bool = True,
    shots: int = 8000,
    chunk_size: int = 256,
    verbose: bool = False,
    output_filepath: str = "reconstructed_audio.wav",
    audio_format: str = "WAV",
) -> None:
    """Convert an audio file to quantum audio and save it as a WAV file.

    Parameters:
    file_path: Path to the audio file to be converted.
    scheme: Quantum Audio scheme to be used.
    sr: Sampling rate of the audio data. Default is 22050.
    mono: Whether to convert audio to mono. Default is True.
    shots: Number of shots for quantum audio measurement. Default is 8000.
    chunk_size: Size of each chunk for quantum processing. Default is 256.
    verbose: Whether to print additional information. Default is False.
    output_filepath: Filepath to save the reconstructed audio. Default is "reconstructed_audio.wav".
    audio_format: Format of the output audio file. Default is "WAV".

    Returns:
    None
    """
    quantum_audio, sr = stream_audio(
        file_path=file_path,
        sr=sr,
        mono=mono,
        scheme=scheme,
        shots=shots,
        chunk_size=chunk_size,
        verbose=verbose,
    )
    write(
        data=quantum_audio,
        sr=sr,
        output_filepath=output_filepath,
        audio_format=audio_format,
    )
