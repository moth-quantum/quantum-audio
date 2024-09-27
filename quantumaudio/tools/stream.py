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

import numpy as np
from tqdm import tqdm

# ======================
# Buffering Utils
# ======================


def get_chunks(
    data: np.ndarray,
    chunk_size: int = 256,
    verbose: bool = False,
) -> None:
    """
    Splits a NumPy array into smaller chunks of specified size.

    This function takes a long array and divides it into smaller chunks,
    which can be useful for processing large datasets in manageable pieces.

    Args:
        data: The input array to be split. The array can be one-dimensional
                           or two-dimensional. If one-dimensional, it will be reshaped
                           into two dimensions.
        chunk_size: The size of each chunk. Default is 256.
        verbose: If True, prints detailed information about the data
                                  and chunks. Default is False.

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
    chunk: Data chunk to be processed.
    scheme: Processing scheme.
    shots: Number of shots.

    Returns:
    None
    """
    chunk = scheme.decode(scheme.encode(chunk, verbose=0), shots=shots)
    return chunk


def process_chunks(
    chunks: list[np.ndarray],
    scheme: Any,
    shots: int,
    process_function: Callable[[np.ndarray, Any, int], np.ndarray] = process,
    show_progress: bool = True,
) -> list:
    """Process chunks of data in an iteration according to a specified scheme.

    Parameters:
    chunks: Data chunks to be processed.
    scheme: Processing scheme.
    shots: Number of shots.
    process_function: Function to process each chunk (default is 'process'). 

    Returns:
    None
    """
    processed_chunks = []
    for chunk in tqdm(chunks, disable=not show_progress):
        processed_chunk = process_function(chunk, scheme, shots)
        processed_chunks.append(processed_chunk)
    return processed_chunks


def combine_chunks(chunks: list[np.ndarray]) -> np.ndarray:
    """Combine a list of NumPy arrays along a specified axis.

    Parameters:
    chunks: A list of NumPy arrays to be combined.

    Returns:
    np.ndarray
    """
    if chunks[0].ndim != 1:
        output = np.concatenate(chunks, axis=1)
    else:
        output = np.concatenate(chunks, axis=0)
    return output


def stream_data(
    data: np.ndarray,
    scheme: Any,
    shots: int = 8000,
    process_function: Callable[[np.ndarray, Any, int], np.ndarray] = process,
    chunk_size: int = 64,
    verbose: bool = False,
) -> np.ndarray:
    """Processes data by dividing it into chunks, applying a Quantum Audio scheme, and combining the results.

    Args:
        data: The input data array to be processed.
        scheme: The quantum audio scheme to be applied to each chunk.
        shots: The number of shots for circuit measurement. Defaults to 8000.
        process_function: Function to process each chunk (default is 'process').
        chunk_size: The size of each chunk. Defaults to 64.
        verbose: If True, enables verbose logging. Defaults to False.

    Returns:
        np.ndarray
    """
    assert (
        chunk_size < data.shape[-1]
    ), f"Chunk size ({chunk_size}) cant be smaller than number of samples ({data.shape[-1]})"
    chunks = get_chunks(data=data, chunk_size=chunk_size, verbose=verbose)
    processed_chunks = process_chunks(
        chunks=chunks, scheme=scheme, shots=shots, process_function=process_function,
    )
    output = combine_chunks(processed_chunks)
    return output
