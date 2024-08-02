import librosa
import soundfile as sf
from . import stream
import numpy.typing as np
from typing import Any

# ======================
# I/O handling functions
# ======================

def read(
    file_path: str,
    sr: int = 22050,
    mono: bool = True,
) -> None:
    """Generate audio chunks from a file.

    Parameters:
    file_path (str): Path to the audio file.
    sr (int, optional): Sampling rate (default is 22050).
    chunk_size (int, optional): Size of each chunk (default is 256).
    mono (bool, optional): Whether to load audio in mono (default is True).
    preview (bool, optional): Whether to preview each chunk (default is False).

    Returns:
    None
    """
    y, sr = librosa.load(file_path, sr=sr, mono=mono)
    return y, sr

def write(
    data: np.NDArray,
    sr: int,
    output_filepath: str = "audio.wav",
) -> None:
    """
    Export processed audio chunks into a single WAV file.

    Parameters:
    processed_chunks (list of np.ndarray): List containing arrays of processed audio chunks.
    sr (int): Sampling rate of the audio data.
    output_filepath (str, optional): Filepath to save the reconstructed audio.

    Returns:
    None
    """
    sf.write(output_filepath, data, sr, format="WAV")
    print(output_filepath)

# ======================
# Main Processing function
# ======================

def get_quantumaudio(
    file_path: str,
    scheme: Any,
    shots: int = 8000, 
    sr: int = 22050,
    mono: bool = True,
    chunk_size: int = 256,
    verbose: bool = False,
) -> np.NDArray:
    
    digital_audio, sr = read(file_path=file_path,sr=sr,mono=mono)
    quantum_audio = stream.stream_data(data=digital_audio,scheme=scheme,shots=shots,chunk_size=chunk_size,verbose=verbose)
    return quantum_audio, sr


# ======================
# Process and Save
# ======================

def save_quantumaudio(
    file_path: str,
    scheme: Any, 
    sr: int = 22050,
    mono: bool = True,
    shots: int = 8000,
    chunk_size: int = 256,
    verbose: bool = False,
    output_filepath: str = "reconstructed_audio.wav",
) -> None:
    
    quantum_audio, sr = get_quantumaudio(file_path=file_path,sr=sr,mono=mono,scheme=scheme,shots=shots,chunk_size=chunk_size,verbose=verbose)
    write(data=quantum_audio,sr=sr,output_filepath=output_filepath)