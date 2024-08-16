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

import numpy as np
from tqdm import tqdm
from typing import Optional, Any

# ======================
# Buffering Utils
# ======================

def get_chunks(
    data: np.ndarray,
    chunk_size: int = 256,
    verbose: bool = False,
) -> None:
    """Generate audio chunks from a file.

    Parameters:
    file_path (str): Path to the audio file.
    sr (int, optional): Sampling rate (default is 22050).
    chunk_size (int, optional): Size of each chunk (default is 256).
    mono (bool, optional): Whether to load audio in mono (default is True).
    verbose (bool, optional): Display buffering information (default is False).

    Returns:
    None
    """
    print(f"Shape: {data.shape}")
    if data.ndim == 1:
        data = data.reshape(1, -1)
    print(
        f"Num samples: {data.shape[-1]}, Num channels: {data.shape[0]}, Buffer size: {chunk_size}"
    )
    y_chunks = []
    for i in range(0, data.shape[-1], chunk_size):
        chunk = data[:, i : i + chunk_size]
        y_chunks.append(chunk)
    print(f"Number of chunks: {len(y_chunks)}")
    print(f"Shape per buffer: {y_chunks[0].shape}")
    return y_chunks


def process(chunk: np.ndarray, scheme: Any, shots: int) -> np.ndarray:
    """Process a chunk of data according to a specified scheme.

    Parameters:
    chunk (np.ndarray): Data chunk to be processed.
    scheme (any): Processing scheme.
    shots (int): Number of shots.

    Returns:
    None
    """
    chunk = scheme.decode(scheme.encode(chunk, verbose=0), shots=shots)
    return chunk


def process_chunks(chunks: list[np.ndarray], scheme: Any, shots: int, show_progress: bool = True) -> list:
    """Process chunks of data in an iteration according to a specified scheme.

    Parameters:
    chunks (np.ndarray): Data chunks to be processed.
    scheme (any): Processing scheme.
    shots (int): Number of shots.

    Returns:
    None
    """
    processed_chunks = []
    for chunk in tqdm(chunks, disable = not show_progress):
        processed_chunk = process(chunk, scheme, shots)
        processed_chunks.append(processed_chunk)
    return processed_chunks

def combine_chunks(chunks):
    if chunks[0].ndim != 1:
        output = np.concatenate(chunks,axis=1)
    else:
        output = np.concatenate(chunks,axis=0)
    return output

def stream_data(
    data: np.ndarray,
    scheme: Any, 
    shots: int = 8000,
    chunk_size: int = 64,
    verbose: bool = False,
) -> np.ndarray:
    
    assert chunk_size < data.shape[-1], f'Chunk size ({chunk_size}) cant be smaller than number of samples ({data.shape[-1]})'
    chunks = get_chunks(data=data,chunk_size=chunk_size,verbose=verbose)
    processed_chunks = process_chunks(chunks=chunks,scheme=scheme,shots=shots)
    output = combine_chunks(processed_chunks)
    return output