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

from typing import Any, Callable, Union

import numpy as np
from tqdm import tqdm

# ======================
# Buffering Functions
# ======================


def get_chunks(
    data: np.ndarray,
    chunk_size: int = 256,
    verbose: bool = False,
) -> None:
    """
    Splits a `numpy` array into smaller chunks of specified size.

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
    if verbose:
        print(f"\nShape: {data.shape}")
    if data.ndim == 1:
        data = data.reshape(1, -1)
    y_chunks = []
    for i in range(0, data.shape[-1], chunk_size):
        chunk = data[:, i : i + chunk_size]
        y_chunks.append(chunk)

    if verbose:
        print(
            f"Num samples: {data.shape[-1]}, Num channels: {data.shape[0]}, Buffer size: {chunk_size}"
        )
        print(f"Number of chunks: {len(y_chunks)}")
        print(f"Shape per buffer: {y_chunks[0].shape}\n")
    return y_chunks


def process(
    chunk: np.ndarray, scheme: "quantumaudio.schemes.Scheme", backend: Any = None, shots: int = 8000
) -> np.ndarray:
    """Process a chunk of data according to a specified scheme by encoding it and decoding it back.

    Args:
        chunk: Data chunk to be processed.
        scheme: Processing scheme.
        backend: A valid Backend object accepted by the :ref:`execute function <execute>` at `decode`.
                 Defaults to `qiskit_aer.AerSimulator()`.
        shots: Number of shots.

    Returns:
        None
    """
    chunk = scheme.decode(
        scheme.encode(chunk, verbose=0), backend=backend, shots=shots
    )
    return chunk


def process_chunks(
    chunks: list[np.ndarray],
    scheme: "quantumaudio.schemes.Scheme",
    process_function: Callable[[np.ndarray, Any, dict], list] = process,
    batch_process: bool = False,
    verbose: bool = True,
    **kwargs,
) -> list:
    """Process chunks of data in an iteration according to a specified scheme.

    Args:
        chunks: Data chunks to be processed.
        scheme: Processing scheme.
        process_function: Function to process each chunk (default is 'process').
        verbose: If True, enables verbose logging. Defaults to False.

    Returns:
        None
    """
    processed_chunks = []
    if not batch_process:  # process one by one
        try:
            for chunk in tqdm(chunks, disable=not verbose):
                processed_chunk = process_function(chunk, scheme, **kwargs)
                processed_chunks.append(processed_chunk)
        except (KeyboardInterrupt, Exception) as e:
            print(e)
            return processed_chunks
    else:  # process all at once
        processed_chunks = process_function(chunks, scheme, **kwargs)
    return processed_chunks


def combine_chunks(chunks: list[np.ndarray]) -> np.ndarray:
    """Combine a list of `numpy` arrays along an axis based on the data dimension.

    Args:
        chunks: A list of `numpy` arrays to be combined.

    Returns:
        np.ndarray
    """
    if chunks[0].ndim != 1:
        output = np.concatenate(chunks, axis=1)
    else:
        output = np.concatenate(chunks, axis=0)
    return output

def normalize(data: np.ndarray) -> np.ndarray:
    """Normalize the input data to ensure it lies within the standard range [-1.0, 1.0].
    
    Args:
        data: Input array containing audio data.
    """
    if not np.all((data >= -1.0) & (data <= 1.0)):
        print("Warning: Values outside the digital audio range are clipped.")
        data = np.clip(data, -1.0, 1.0)
    return data

def stream_data(
    data: np.ndarray,
    scheme: "quantumaudio.schemes.Scheme",
    chunk_size: int = 64,
    process_function: Callable[[np.ndarray, Any, dict], list] = process,
    batch_process: bool = False,
    verbose: Union[int, bool] = 2,
    **kwargs,
) -> np.ndarray:
    """Processes data by dividing it into chunks, applying a Quantum Audio scheme, and combining the results.

    Args:
        data: The input data array to be processed.
        scheme: The quantum audio scheme to be applied to each chunk.
        chunk_size: The size of each chunk. Defaults to 64.
        process_function: Function to process each chunk.

              - Defaults to :func:`process` which accepts any additional `**kwargs`.

        batch_process: Boolean value to inidicate whether the provided `process_function` applies to a single chunk or a batch.
        verbose: If True, enables verbose logging. Defaults to 2.

              - >1: Shows progress bar.
              - >2: Shows additional information such as buffer size and number of qubits.

    Returns:
        np.ndarray
    """
    data = normalize(data)
    if chunk_size > data.shape[-1]:
        chunk_size = data.shape[-1]
        if verbose == 2:
            print(f"Chunk size set to {data.shape[-1]}.")
    chunks = get_chunks(
        data=data, chunk_size=chunk_size, verbose=(verbose == 2)
    )
    if verbose == 2:
        scheme.calculate(chunks[0])
    processed_chunks = process_chunks(
        chunks=chunks,
        scheme=scheme,
        process_function=process_function,
        batch_process=batch_process,
        verbose=verbose,
        **kwargs,
    )
    output = combine_chunks(processed_chunks)
    return output
