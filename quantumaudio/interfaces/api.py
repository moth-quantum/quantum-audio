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

"""The `quantumaudio.interfaces.api` module provides easy access to some of the core functions 
without explicitly instantiating a Scheme class. They are made directly accessible from `quantumaudio`.
"""

import quantumaudio
from quantumaudio import load_scheme
from quantumaudio.utils import pick_key
from quantumaudio.tools import stream_data
from typing import Union

# ------------------- Core Functions ---------------------------

def encode(
    data: "np.ndarray",
    scheme: Union[str, quantumaudio.schemes.Scheme] = "qpam",
    **kwargs,
):
    """Encodes data and prepares circuit using a specified quantum scheme.

    Args:
        data: The data to encode.
        scheme: Name of the encoding scheme or a scheme object to use. Defaults to "qpam".
        **kwargs: Additional keyword arguments passed required for encoding method and scheme initialisation.

    Returns:
        Qiskit circuit encoding the data.
    """
    scheme_kwargs, kwargs = _split_kwargs(kwargs)
    return _load_scheme(scheme, **scheme_kwargs).encode(data, **kwargs)


def decode(circuit: "qiskit.QuantumCircuit", **kwargs):
    """Decodes a quantum circuit using the scheme it was encoded with.

    Args:
        circuit: Qiskit circuit object to decode.
        **kwargs: Additional keyword arguments passed to the decoding method. Refer to the scheme's `decode` method.

    Returns:
        Decoded data from the quantum circuit.
    """
    scheme, scheme_kwargs, kwargs = _fetch_kwargs(circuit, kwargs)
    return _load_scheme(scheme, **scheme_kwargs).decode(circuit, **kwargs)


# ------------------- Tool Function ---------------------------


def stream(
    data: "np.ndarray",
    scheme: Union[str, quantumaudio.schemes.Scheme] = "qpam",
    **kwargs,
):
    """Streams data through a quantum encoding scheme for longer arrays.

    Args:
        data: Data to be streamed.
        scheme: Name of the quantum scheme to use for streaming.
        **kwargs: Additional keyword arguments passed to the streaming method.

    Returns:
        Processed stream data based on the quantum scheme.
    """
    scheme_kwargs, kwargs = _split_kwargs(kwargs)
    scheme = _load_scheme(scheme, **scheme_kwargs)
    return stream_data(data=data, scheme=scheme, **kwargs)


# ------------------- Additional Functions ---------------------------


def calculate(
    data: "np.ndarray",
    scheme: Union[str, quantumaudio.schemes.Scheme] = "qpam",
    **kwargs,
):
    """Estimates and Prints the resources required (number of qubits) according to a scheme.

    Args:
        data: The data to encode.
        scheme: Name of the encoding scheme or a scheme object to use. Defaults to "qpam".
        **kwargs: Additional keyword arguments passed to the scheme class.
    """
    _load_scheme(scheme, **kwargs).calculate(data)


def decode_result(
    result: Union[
        "qiskit.result.Result",
        "qiskit.primitives.PrimitiveResult",
        "qiskit.primitives.SamplerPubResult",
    ],
    **kwargs,
):
    """Decodes a quantum result object using the scheme it was encoded with.

    Args:
        result: Qiskit result object to decode.
        **kwargs: Additional keyword arguments passed to the decoding method. Refer to the scheme's `decode_result` method.

    Returns:
        Decoded data from the result object.
    """
    scheme, scheme_kwargs, kwargs = _fetch_kwargs(result, kwargs)
    return _load_scheme(scheme, **scheme_kwargs).decode_result(
        result, **kwargs
    )


def decode_counts(counts: dict, metadata: dict, **kwargs):
    """Decodes Quantum circuit measurement counts using metadata.

    Args:
        counts: Counts dictionary to decode.
        metadata: Metadata dictionary associated with the circuit that was executed.
        **kwargs: Additional keyword arguments passed to the decoding method. Refer to the scheme's `decode_counts` method.

    Returns:
        Decoded data from the counts.
    """
    kwargs["metadata"] = metadata
    scheme, scheme_kwargs, kwargs = _fetch_kwargs(counts, kwargs)
    return _load_scheme(scheme, **scheme_kwargs).decode_counts(
        counts, **kwargs
    )


# ------------------- API Helpers ---------------------------

_cache = {}


def _load_scheme(
    scheme: Union[str, quantumaudio.schemes.Scheme], **scheme_kwargs
):
    """Load a scheme with specified keyword arguments, caching the result to
    avoid repeated loading for the same parameters.

    Args:
        scheme: Name of the quantum scheme or scheme object to use for streaming.
        scheme_kwargs: Dictionary containing keyword arguments.

    Returns:
        The loaded or cached scheme object.
    """
    if isinstance(scheme, quantumaudio.schemes.Scheme):
        return scheme

    cache_key = (scheme, frozenset(scheme_kwargs.items()))
    if cache_key not in _cache:
        _cache[cache_key] = load_scheme(scheme, **scheme_kwargs)
    return _cache[cache_key]


def _split_kwargs(kwargs: dict):
    """Splits keyword arguments between scheme loading and encoding operations.

    Args:
        kwargs (dict): Dictionary containing keyword arguments.

    Returns:
        Two dictionaries for scheme-related keyword arguments, and remaining keyword arguments.
    """
    scheme_args = ("qubit_depth", "num_channels")
    return {
        arg: kwargs.pop(arg) for arg in scheme_args if arg in kwargs
    }, kwargs


def _fetch_kwargs(
    instance: Union[
        "dict",
        "qiskit.QuantumCircuit",
        "qiskit.result.Result",
        "qiskit.primitives.PrimitiveResult",
        "qiskit.primitives.SamplerPubResult",
    ],
    kwargs: dict,
):
    """Fetches scheme at decoding and splits keyword arguments accordingly.

    Args:
        instance (object): Qiskit circuit or Results object.
        kwargs (dict): Dictionary containing keyword arguments.

    Returns:
        Tuple of Scheme name, scheme-related keyword arguments, and remaining keyword arguments.
    """
    scheme = kwargs.pop("scheme", None)
    if scheme and isinstance(scheme, quantumaudio.schemes.Scheme):
        return scheme, {}, kwargs
    scheme = pick_key(kwargs, instance, key="scheme")
    scheme_kwargs = {}
    num_channels = pick_key(kwargs, instance, key="num_channels")
    if num_channels:
        scheme_kwargs["num_channels"] = num_channels
    qubit_shape = pick_key(kwargs, instance, key="qubit_shape")
    if qubit_shape and "qsm" in scheme:
        scheme_kwargs["qubit_depth"] = qubit_shape[-1]
    return scheme, scheme_kwargs, kwargs